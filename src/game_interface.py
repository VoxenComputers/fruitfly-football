"""Visual Motion & Neural Interface for Drosophila Connectome Pipeline.

Components:
1. ScreenGrabber: Low-latency screen grabber via mss with synthetic visual stimulus generator.
2. VisualMotionProcessor: Optic flow processor (temporal differencing + Farneback flow + looming divergence)
   converting visual dynamics into Poisson spike trains for T4/T5 optic lobe neurons.
3. GameActionController: Action dispatcher with refractory cooldown gating.
"""

from __future__ import annotations

import os
import sys
import time
import logging
from typing import Dict, List, Optional, Tuple, Any

import cv2
import numpy as np

logger = logging.getLogger("GameInterface")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ScreenGrabber:
    """Captures gameplay screen using mss or produces synthetic gameplay frames."""

    def __init__(self, region: Optional[Dict[str, int]] = None, monitor_idx: int = 1):
        self.region = region
        self.monitor_idx = monitor_idx
        self._sct = None
        self._synthetic_step = 0

        try:
            import mss
            mss_cls = getattr(mss, "MSS", mss.mss)
            self._sct = mss_cls()
            if self.region is None:
                # Target primary monitor centered Subway Surfers portrait area
                mon = self._sct.monitors[min(self.monitor_idx, len(self._sct.monitors) - 1)]
                # Center portrait region (e.g. 540x960 centered on screen)
                w = 540
                h = 960
                left = mon["left"] + (mon["width"] - w) // 2
                top = mon["top"] + (mon["height"] - h) // 2
                self.region = {"top": top, "left": left, "width": w, "height": h}
        except Exception as e:
            logger.warning(f"mss initialization failed ({e}). Falling back to synthetic screen generator.")
            self._sct = None

    def grab_frame(self) -> np.ndarray:
        """Captures a frame as BGR numpy array."""
        if self._sct is not None and self.region is not None:
            try:
                sct_img = self._sct.grab(self.region)
                frame = np.array(sct_img)
                # Convert BGRA to BGR
                return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            except Exception as e:
                logger.debug(f"mss grab failed: {e}. Using synthetic frame.")

        return self.generate_synthetic_frame()

    def generate_synthetic_frame(
        self,
        stimulus_direction: Optional[str] = None
    ) -> np.ndarray:
        """Generates dynamic synthetic visual stimuli for optic flow and motion testing."""
        self._synthetic_step += 1
        h, w = 960, 540
        frame = np.zeros((h, w, 3), dtype=np.uint8)

        # Ambient background
        frame[:, :] = (35, 40, 45)

        # Dynamic stimulus based on requested directional cue
        t = (self._synthetic_step * 24) % w
        if stimulus_direction == "left":
            x = (w - t) % w
            cv2.rectangle(frame, (x, h // 4), (x + 120, 3 * h // 4), (200, 200, 230), -1)
        elif stimulus_direction == "right":
            x = t % w
            cv2.rectangle(frame, (x, h // 4), (x + 120, 3 * h // 4), (200, 200, 230), -1)
        elif stimulus_direction == "up":
            # Looming expansion stimulus
            radius = int(30 + (self._synthetic_step * 8) % 180)
            cv2.circle(frame, (w // 2, h // 2), radius, (230, 160, 40), -1)
        elif stimulus_direction == "down":
            y = (self._synthetic_step * 24) % h
            cv2.rectangle(frame, (w // 4, y), (3 * w // 4, y + 100), (40, 210, 210), -1)
        else:
            # Default shifting visual texture
            phase = self._synthetic_step * 0.15
            x_vals = np.linspace(0, 4 * np.pi, w)
            strip = ((np.sin(x_vals + phase) + 1.0) * 80 + 50).astype(np.uint8)
            frame[:, :, 0] = strip
            frame[:, :, 1] = strip
            frame[:, :, 2] = strip

        return frame


class VisualMotionProcessor:
    """Computes optic flow and encodes directional velocity into Poisson spike trains."""

    def __init__(
        self,
        grid_size: int = 32,
        neurons_per_channel: int = 75,
        gain: float = 2.5,
    ):
        self.grid_size = grid_size
        self.num_neurons = neurons_per_channel
        self.gain = gain
        self.prev_gray: Optional[np.ndarray] = None

    def process_frame(
        self,
        bgr_frame: np.ndarray
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, float], np.ndarray]:
        """Processes an incoming visual frame into directional Poisson spike trains.

        Returns:
            - spike_dict: {'left': array(75,), 'right': array(75,), 'up': array(75,), 'down': array(75,)}
            - flow_rates: {'left': float, 'right': float, 'up': float, 'down': float}
            - downsampled_vis: 32x32 visual representation for diagnostics
        """
        # 1. Convert to grayscale and resize to 32x32
        gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (self.grid_size, self.grid_size), interpolation=cv2.INTER_AREA)
        blurred = cv2.GaussianBlur(resized, (3, 3), 0.8)

        if self.prev_gray is None:
            self.prev_gray = blurred
            zeros = {ch: np.zeros(self.num_neurons, dtype=np.float32) for ch in ["left", "right", "up", "down"]}
            rates = {ch: 0.0 for ch in ["left", "right", "up", "down"]}
            return zeros, rates, resized

        # 2. Compute Farneback Optical Flow (dense pixel velocities u, v)
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray,
            blurred,
            None,
            pyr_scale=0.5,
            levels=2,
            winsize=5,
            iterations=2,
            poly_n=5,
            poly_sigma=1.1,
            flags=0,
        )
        self.prev_gray = blurred

        u = flow[..., 0]  # Horizontal velocity (+ = right, - = left)
        v = flow[..., 1]  # Vertical velocity (+ = down, - = up)

        # 3. Directional Motion Intensity & Looming Divergence
        # Left flow (motion to the left, indicating right obstacle or leftward turn)
        flow_left = np.maximum(0.0, -u)
        # Right flow
        flow_right = np.maximum(0.0, u)
        # Upward flow (ground looming / approaching obstacle from below)
        flow_up = np.maximum(0.0, -v)
        # Downward flow
        flow_down = np.maximum(0.0, v)

        # Spatial weighting: center region looms strongly when obstacles approach
        # Flank regions detect peripheral left/right motion
        mid_x = self.grid_size // 2
        mid_y = self.grid_size // 2

        # Right-flank motion pushes steering LEFT
        mag_left = float(np.mean(flow_left[:, :mid_x]) * 0.6 + np.mean(flow_right[:, mid_x:]) * 0.4)
        # Left-flank motion pushes steering RIGHT
        mag_right = float(np.mean(flow_right[:, mid_x:]) * 0.6 + np.mean(flow_left[:, :mid_x]) * 0.4)
        # Upward expansion / jump cue
        mag_up = float(np.mean(flow_up[mid_y:, :]))
        # Downward expansion / roll cue
        mag_down = float(np.mean(flow_down[:mid_y, :]))

        flow_rates = {
            "left": mag_left,
            "right": mag_right,
            "up": mag_up,
            "down": mag_down,
        }

        # 4. Poisson Spike Generation
        # Convert motion intensity to spike probability
        spike_dict: Dict[str, np.ndarray] = {}
        for channel, mag in flow_rates.items():
            prob = float(np.clip(mag * self.gain, 0.0, 0.95))
            # Bernoulli / Poisson trial per neuron
            spikes = (np.random.rand(self.num_neurons) < prob).astype(np.float32)
            spike_dict[channel] = spikes

        return spike_dict, flow_rates, resized


class GameActionController:
    """Dispatches and logs neural motor decisions with refractory cooldown gating.

    Decoupled from mobile runner key injection and ADB gestures.
    """

    def __init__(
        self,
        cooldown_ms: float = 250.0,
        dry_run: bool = True,
        **kwargs,
    ):
        self.cooldown_ms = cooldown_ms
        self.dry_run = dry_run
        self.last_action_time: float = 0.0

    def execute_action(self, action: str) -> bool:
        """Dispatches action if refractory cooldown has elapsed.

        Args:
            action: Motor action identifier.

        Returns:
            True if action was accepted, False if blocked by cooldown or invalid.
        """
        if not action:
            return False

        now = time.time() * 1000.0  # ms
        elapsed = now - self.last_action_time
        if elapsed < self.cooldown_ms:
            logger.debug(f"Action '{action}' blocked by cooldown ({elapsed:.1f}ms < {self.cooldown_ms}ms)")
            return False

        self.last_action_time = now
        logger.info(f"[MOTOR ACTION] {action}")
        return True

