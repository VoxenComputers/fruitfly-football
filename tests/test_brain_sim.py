"""Unit tests for Phase 3: Drosophila Spiking Neural Network (LIF) Engine."""

import pytest
import torch
import numpy as np

from src.brain_sim import DrosophilaLIFBrain, BrainStepResult
from src.data_engine import generate_synthetic_connectome


@pytest.fixture
def mock_brain():
    """Returns a DrosophilaLIFBrain instance with a fast synthetic connectome."""
    graph = generate_synthetic_connectome(num_neurons=2000, seed=42)
    brain = DrosophilaLIFBrain(connectome_data=graph, device="cpu")
    return brain


def test_subthreshold_decay(mock_brain):
    """Verify membrane potential exponentially decays toward V_rest without input."""
    # Manually set membrane potentials to 0.8 mV
    mock_brain.v.fill_(0.8)
    initial_v = float(mock_brain.v[0].item())

    # Step with 0 input
    res = mock_brain.step(sensory_spikes=torch.zeros(300))

    decayed_v = float(mock_brain.v[0].item())
    expected_v = initial_v * mock_brain.decay_v
    assert pytest.approx(decayed_v, rel=1e-3) == expected_v
    assert decayed_v < initial_v


def test_spike_generation_and_reset(mock_brain):
    """Verify that strong current input triggers a spike and voltage resets."""
    # Direct injection into neuron 0
    stim = torch.zeros(2000)
    stim[0] = 5.0  # Above threshold 1.0

    res = mock_brain.step(sensory_spikes=stim)

    # Neuron 0 should have spiked
    assert res.spikes[0].item() == 1.0
    # Membrane voltage should have reset to V_reset (0.0)
    assert mock_brain.v[0].item() == mock_brain.v_reset
    # Refractory timer should be activated
    assert mock_brain.refractory_timer[0].item() == mock_brain.refractory_steps


def test_refractory_period(mock_brain):
    """Verify that a neuron cannot spike again while refractory."""
    stim = torch.zeros(2000)
    stim[0] = 10.0

    # Step 1: Spikes and enters refractory period
    res1 = mock_brain.step(sensory_spikes=stim)
    assert res1.spikes[0].item() == 1.0

    # Step 2: Input continues, but refractory timer is active -> cannot spike
    res2 = mock_brain.step(sensory_spikes=stim)
    assert res2.spikes[0].item() == 0.0
    assert mock_brain.v[0].item() == mock_brain.v_reset


def test_directional_sensory_to_motor_pathways(mock_brain):
    """Verify directional optic input drives specific motor outputs."""
    # Test Left Optic Flow -> DNg SWIPE_LEFT
    mock_brain.reset()
    left_spikes = torch.ones(75)  # Fire all left T4/T5 cells
    actions_recorded = []

    # Run for 15 steps of persistent stimulus
    for _ in range(25):
        res = mock_brain.step(sensory_spikes={"left": left_spikes})
        if res.action:
            actions_recorded.append(res.action)

    # Left motor rate should dominate right motor rate
    assert mock_brain.motor_smoothed["swipe_left"] > mock_brain.motor_smoothed["swipe_right"]
    assert "SWIPE_LEFT" in actions_recorded

    # Test Upward Optic Flow (Jump cue) -> DNp JUMP
    mock_brain.reset()
    up_spikes = torch.ones(75)
    jump_actions = []

    for _ in range(25):
        res = mock_brain.step(sensory_spikes={"up": up_spikes})
        if res.action:
            jump_actions.append(res.action)

    assert mock_brain.motor_smoothed["jump"] > mock_brain.motor_smoothed["swipe_left"]
    assert "JUMP" in jump_actions
