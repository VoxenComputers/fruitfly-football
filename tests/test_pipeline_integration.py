"""Integration tests for the closed-loop Drosophila Connectome SNN pipeline."""

import pytest
from main import run_pipeline


def test_closed_loop_pipeline_dry_run():
    """Verify 40 steps of full closed-loop pipeline in dry-run mode."""
    steps = 40
    summary = run_pipeline(
        dry_run=True,
        max_steps=steps,
        gui=False,
        device="cpu",
        cooldown_ms=100.0,
    )

    assert summary["steps_executed"] == steps
    assert summary["total_spikes"] > 0, "No spikes generated across pipeline"
    assert summary["mean_fps"] > 15.0, f"Pipeline too slow: {summary['mean_fps']:.1f} FPS"
    assert len(summary["actions_triggered"]) > 0, "No motor actions triggered during dry-run"
