"""Unit tests for Phase 4: Vision & Emulator Input Bridge."""

import time
import pytest
import numpy as np

from src.game_interface import (
    ScreenGrabber,
    VisualMotionProcessor,
    GameActionController,
)


def test_screen_grabber():
    """Verify screen capture and synthetic frame generation."""
    grabber = ScreenGrabber()
    frame = grabber.grab_frame()

    assert frame is not None
    assert isinstance(frame, np.ndarray)
    assert len(frame.shape) == 3
    assert frame.shape[2] == 3  # BGR
    assert frame.dtype == np.uint8

    # Test synthetic frame generator directly
    syn_frame = grabber.generate_synthetic_frame(stimulus_direction="left")
    assert syn_frame.shape == (960, 540, 3)


def test_visual_motion_processor():
    """Verify 32x32 preprocessing, optic flow, and Poisson spike generation."""
    processor = VisualMotionProcessor(grid_size=32, neurons_per_channel=75, gain=3.0)

    # Frame 1: Blank frame
    frame1 = np.full((960, 540, 3), 50, dtype=np.uint8)
    spikes1, rates1, vis1 = processor.process_frame(frame1)

    assert vis1.shape == (32, 32)
    # First frame has 0 flow
    for ch in ["left", "right", "up", "down"]:
        assert len(spikes1[ch]) == 75
        assert rates1[ch] == 0.0

    # Frame 2: Shifted / moving content to generate leftward optic flow
    frame2 = np.copy(frame1)
    # Add bright patch moving leftwards
    frame2[400:600, 100:300] = 220
    spikes2, rates2, vis2 = processor.process_frame(frame2)

    # Verify spike formats
    for ch in ["left", "right", "up", "down"]:
        assert len(spikes2[ch]) == 75
        assert spikes2[ch].dtype == np.float32
        # Values should be binary 0.0 or 1.0
        assert np.all(np.isin(spikes2[ch], [0.0, 1.0]))

    # Directional rate should be non-zero after motion
    total_rate = sum(rates2.values())
    assert total_rate > 0.0


def test_game_action_controller_cooldown():
    """Verify action refractory cooldown (250 ms) prevents command spamming."""
    controller = GameActionController(cooldown_ms=250.0, dry_run=True)

    # Action 1: should succeed immediately
    ok1 = controller.execute_action("SWIPE_LEFT")
    assert ok1 is True

    # Action 2 immediately after: should be blocked by cooldown
    ok2 = controller.execute_action("SWIPE_RIGHT")
    assert ok2 is False

    # Wait for cooldown to expire
    time.sleep(0.26)

    # Action 3: should succeed now
    ok3 = controller.execute_action("JUMP")
    assert ok3 is True
