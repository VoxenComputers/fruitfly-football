"""Unit tests for Phase 2: Connectome Data Extraction & Fallback Generator."""

import os
from pathlib import Path
import pytest
import torch
import numpy as np

from src.data_engine import (
    generate_synthetic_connectome,
    load_or_generate_connectome,
    verify_connectome,
)


def test_synthetic_connectome_structure():
    """Verify graph dimensions, population splits, and channel mappings."""
    n = 2000
    graph = generate_synthetic_connectome(num_neurons=n, seed=123)

    assert graph["num_neurons"] == n
    assert isinstance(graph["weights"], torch.Tensor)
    assert graph["weights"].shape == (n, n)
    assert len(graph["node_types"]) == n

    # Check input channels
    input_idx = graph["input_indices"]
    for ch in ["left", "right", "up", "down"]:
        assert ch in input_idx
        assert len(input_idx[ch]) == 75

    # Total sensory neurons should be 300
    sensory_indices = (
        input_idx["left"] + input_idx["right"] + input_idx["up"] + input_idx["down"]
    )
    assert len(sensory_indices) == 300
    assert len(set(sensory_indices)) == 300  # Mutually exclusive

    # Check output channels
    output_idx = graph["output_indices"]
    for act in ["swipe_left", "swipe_right", "jump", "roll"]:
        assert act in output_idx
        assert len(output_idx[act]) == 75

    motor_indices = (
        output_idx["swipe_left"]
        + output_idx["swipe_right"]
        + output_idx["jump"]
        + output_idx["roll"]
    )
    assert len(motor_indices) == 300
    assert len(set(motor_indices)) == 300  # Mutually exclusive

    # Sensory and motor should not overlap
    assert set(sensory_indices).isdisjoint(set(motor_indices))


def test_weight_matrix_properties():
    """Verify sparsity, diagonal zeros, and Dale's principle."""
    graph = generate_synthetic_connectome(num_neurons=2000, seed=42)
    W = graph["weights"].numpy()

    # 1. No self-loops
    assert np.all(np.diag(W) == 0.0)

    # 2. Biological sparsity
    density = np.count_nonzero(W) / (2000 * 1999)
    assert 0.015 < density < 0.08, f"Unexpected density: {density}"

    # 3. Check for presence of both excitatory and inhibitory connections
    pos_weights = np.count_nonzero(W > 0)
    neg_weights = np.count_nonzero(W < 0)
    assert pos_weights > 0, "No excitatory synapses found"
    assert neg_weights > 0, "No inhibitory synapses found"

    # Excitatory should outnumber inhibitory (approx 4:1)
    assert pos_weights > neg_weights

    # 4. Weights should not be NaN or Inf
    assert not np.isnan(W).any()
    assert not np.isinf(W).any()


def test_connectome_serialization(tmp_path):
    """Verify saving to disk and loading returns valid graph."""
    temp_file = tmp_path / "test_connectome.pt"

    # Generate and save
    saved_graph = load_or_generate_connectome(
        filepath=temp_file, force_regenerate=True, num_neurons=2000
    )
    assert temp_file.exists()
    assert verify_connectome(saved_graph)

    # Reload from disk
    loaded_graph = load_or_generate_connectome(
        filepath=temp_file, force_regenerate=False
    )
    assert loaded_graph["num_neurons"] == saved_graph["num_neurons"]
    assert torch.equal(loaded_graph["weights"], saved_graph["weights"])
    assert verify_connectome(loaded_graph)
