"""Spiking Neural Network (SNN) Engine for Drosophila Visual-Motor Circuit.

Simulates a vectorized Leaky Integrate-and-Fire (LIF) network with dynamic
threshold adaptation, absolute refractory periods, and connectome-derived
synaptic connectivity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import torch

from src.data_engine import load_or_generate_connectome, DEFAULT_CONNECTOME_PATH


@dataclass
class BrainStepResult:
    """Output telemetry and motor decisions from a single simulation step."""
    spikes: torch.Tensor  # Binary spike vector shape (N,)
    motor_rates: Dict[str, float]  # Smoothed activity per motor channel
    action: Optional[str]  # Winner action ('SWIPE_LEFT', 'SWIPE_RIGHT', 'JUMP', 'ROLL', or None)
    confidence: float  # Margin or confidence of winner action
    sensory_spikes_count: int  # Number of input spikes
    total_spikes_count: int  # Total spikes in circuit this step
    mean_voltage: float  # Mean membrane potential across network


class DrosophilaLIFBrain:
    """Vectorized PyTorch Leaky Integrate-and-Fire (LIF) Drosophila Brain.

    Dynamics:
    - dV/dt = -(V - V_rest)/tau_m + R * (I_syn + I_sensory)
    - Dynamic adaptive threshold: V_th(t) = V_th0 + theta(t)
    - Absolute refractory period clamping V to V_reset for tau_ref ms
    """

    ACTION_MAP = {
        "swipe_left": "SWIPE_LEFT",
        "swipe_right": "SWIPE_RIGHT",
        "jump": "JUMP",
        "roll": "ROLL",
    }

    def __init__(
        self,
        connectome_data: Optional[Dict[str, Any]] = None,
        connectome_path: str | Path = DEFAULT_CONNECTOME_PATH,
        dt_ms: float = 1.0,
        tau_m_ms: float = 20.0,
        v_rest: float = 0.0,
        v_reset: float = 0.0,
        v_th0: float = 1.0,
        tau_theta_ms: float = 50.0,
        delta_theta: float = 0.15,
        refractory_steps: int = 3,
        motor_tau_ms: float = 20.0,
        motor_threshold: float = 0.05,
        device: Optional[str] = None,
    ):
        # 1. Device selection
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # 2. Load Connectome
        if connectome_data is None:
            connectome_data = load_or_generate_connectome(connectome_path)
        self.connectome = connectome_data
        self.num_neurons = self.connectome["num_neurons"]

        # 3. Weights Matrix (Shape: N x N, where W[j, i] = weight from j to i)
        weights_cpu = self.connectome["weights"]
        self.weights = weights_cpu.to(self.device).float()

        # 4. Neural Populations and Indices
        self.input_indices = self.connectome["input_indices"]
        self.output_indices = self.connectome["output_indices"]
        self.subpopulations = self.connectome.get("subpopulations", {})

        # Precompute flat sensory index tensor for fast indexing
        self.all_sensory_indices = torch.tensor(
            self.input_indices["left"]
            + self.input_indices["right"]
            + self.input_indices["up"]
            + self.input_indices["down"],
            dtype=torch.int64,
            device=self.device,
        )

        # Precompute motor channel index tensors
        self.motor_tensors = {
            act: torch.tensor(indices, dtype=torch.int64, device=self.device)
            for act, indices in self.output_indices.items()
        }

        # 5. LIF Parameters
        self.dt = dt_ms
        self.tau_m = tau_m_ms
        self.decay_v = math.exp(-self.dt / self.tau_m)  # Membrane decay factor
        self.v_rest = v_rest
        self.v_reset = v_reset
        self.v_th0 = v_th0

        # Dynamic Threshold parameters
        self.tau_theta = tau_theta_ms
        self.decay_theta = math.exp(-self.dt / self.tau_theta)
        self.delta_theta = delta_theta

        # Refractory parameters
        self.refractory_steps = refractory_steps

        # Motor decoding parameters
        self.motor_decay = math.exp(-self.dt / motor_tau_ms)
        self.motor_threshold = motor_threshold

        # 6. Initialize State Variables
        self.v = torch.zeros(self.num_neurons, device=self.device, dtype=torch.float32)
        self.theta = torch.zeros(self.num_neurons, device=self.device, dtype=torch.float32)
        self.refractory_timer = torch.zeros(
            self.num_neurons, device=self.device, dtype=torch.int32
        )
        self.spikes = torch.zeros(
            self.num_neurons, device=self.device, dtype=torch.float32
        )

        # Filtered motor rates (Exponential Moving Average)
        self.motor_smoothed = {act: 0.0 for act in self.output_indices.keys()}

        self.reset()

    def reset(self):
        """Resets network state potentials, timers, and spike history."""
        self.v.fill_(self.v_rest)
        self.theta.fill_(0.0)
        self.refractory_timer.fill_(0)
        self.spikes.fill_(0.0)
        for act in self.motor_smoothed:
            self.motor_smoothed[act] = 0.0

    def step(
        self,
        sensory_spikes: torch.Tensor | np.ndarray | Dict[str, torch.Tensor | np.ndarray]
    ) -> BrainStepResult:
        """Executes one simulation timestep (dt = 1 ms).

        Args:
            sensory_spikes: Vector of sensory spikes (300 neurons) or dict with
                            'left', 'right', 'up', 'down' binary arrays.

        Returns:
            BrainStepResult containing spikes, motor activations, and chosen action.
        """
        # 1. Format input sensory spikes into network-wide external current
        i_sensory = torch.zeros(self.num_neurons, device=self.device, dtype=torch.float32)

        if isinstance(sensory_spikes, dict):
            for channel, spikes in sensory_spikes.items():
                if channel in self.input_indices:
                    indices = self.input_indices[channel]
                    if isinstance(spikes, np.ndarray):
                        spk_t = torch.from_numpy(spikes).to(self.device).float()
                    elif isinstance(spikes, torch.Tensor):
                        spk_t = spikes.to(self.device).float()
                    else:
                        spk_t = torch.tensor(spikes, device=self.device, dtype=torch.float32)
                    i_sensory[indices] = spk_t
        elif isinstance(sensory_spikes, (np.ndarray, torch.Tensor, list)):
            if isinstance(sensory_spikes, np.ndarray):
                spk_t = torch.from_numpy(sensory_spikes).to(self.device).float()
            elif isinstance(sensory_spikes, list):
                spk_t = torch.tensor(sensory_spikes, device=self.device, dtype=torch.float32)
            else:
                spk_t = sensory_spikes.to(self.device).float()

            if spk_t.numel() == len(self.all_sensory_indices):
                i_sensory[self.all_sensory_indices] = spk_t
            elif spk_t.numel() == self.num_neurons:
                i_sensory = spk_t

        num_sensory_spikes = int((i_sensory > 0).sum().item())

        # 2. Synaptic current from previous step spikes:
        # I_syn = spikes @ weights (since W[j, i] is presynaptic j -> postsynaptic i)
        i_syn = torch.matmul(self.spikes, self.weights)

        # Total input current
        # Scale sensory current so external stimulus drives responsive sensory firing
        i_total = i_syn + i_sensory * 2.5

        # 3. Refractory mask
        is_refractory = self.refractory_timer > 0

        # Decrement refractory timer
        self.refractory_timer = torch.clamp(self.refractory_timer - 1, min=0)

        # 4. Membrane Potential Decay & Integration for non-refractory neurons
        # V(t) = V_rest + (V(t-1) - V_rest) * decay + I_total
        v_next = self.v_rest + (self.v - self.v_rest) * self.decay_v + i_total
        # Clamp refractory neurons to V_reset
        v_next = torch.where(is_refractory, torch.full_like(v_next, self.v_reset), v_next)

        # 5. Dynamic Threshold Adaptation Decay
        self.theta = self.theta * self.decay_theta
        effective_threshold = self.v_th0 + self.theta

        # 6. Spike Generation
        new_spikes = (v_next >= effective_threshold) & (~is_refractory)
        new_spikes_float = new_spikes.float()

        # 7. Post-spike resets and adaptation updates
        # Reset voltage of spiking neurons to V_reset
        self.v = torch.where(new_spikes, torch.full_like(v_next, self.v_reset), v_next)
        # Set refractory counter for spiking neurons
        self.refractory_timer = torch.where(
            new_spikes,
            torch.full_like(self.refractory_timer, self.refractory_steps),
            self.refractory_timer,
        )
        # Elevate adaptive threshold
        self.theta = self.theta + new_spikes_float * self.delta_theta

        # Store current spikes
        self.spikes = new_spikes_float

        # 8. Motor Channel Activity Decoding
        motor_raw_rates: Dict[str, float] = {}
        for act, idx_tensor in self.motor_tensors.items():
            channel_spikes = self.spikes[idx_tensor]
            mean_rate = float(channel_spikes.mean().item())
            # Update smoothed rate
            self.motor_smoothed[act] = (
                self.motor_smoothed[act] * self.motor_decay
                + mean_rate * (1.0 - self.motor_decay)
            )
            motor_raw_rates[act] = self.motor_smoothed[act]

        # 9. Winner-Take-All Action Selection
        best_act = None
        best_rate = -1.0
        second_rate = -1.0

        for act, rate in self.motor_smoothed.items():
            if rate > best_rate:
                second_rate = best_rate
                best_rate = rate
                best_act = act
            elif rate > second_rate:
                second_rate = rate

        confidence = max(0.0, best_rate - max(0.0, second_rate))
        chosen_action: Optional[str] = None
        if best_rate >= self.motor_threshold and best_act is not None:
            chosen_action = self.ACTION_MAP.get(best_act)

        total_spikes = int(new_spikes.sum().item())
        mean_voltage = float(self.v.mean().item())

        return BrainStepResult(
            spikes=self.spikes,
            motor_rates=motor_raw_rates,
            action=chosen_action,
            confidence=confidence,
            sensory_spikes_count=num_sensory_spikes,
            total_spikes_count=total_spikes,
            mean_voltage=mean_voltage,
        )
