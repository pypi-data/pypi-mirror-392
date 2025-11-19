# oncosplice/engines.py
from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Union

import numpy as np

# These are your existing helpers; keep them in separate modules if you want.
# from ._spliceai_utils import one_hot_encode, sai_models  # type: ignore
# from ._pangolin_utils import pangolin_predict_probs, pang_models  # type: ignore
import torch
from pkg_resources import resource_filename
from pangolin.model import *
import numpy as np
import sys

pang_model_nums = [0, 1, 2, 3, 4, 5, 6, 7]
pang_models = []

def get_best_device():
    """Get the best available device for computation."""
    if sys.platform == 'darwin' and torch.backends.mps.is_available():
        try:
            # Test MPS availability
            torch.tensor([1.0], device="mps")
            return torch.device("mps")
        except RuntimeError:
            print("Warning: MPS not available, falling back to CPU")
            return torch.device("cpu")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")

device = get_best_device()
print(f"Pangolin loaded to {device}.")

# Initialize models with improved error handling
try:
    for i in pang_model_nums:
        for j in range(1, 6):
            try:
                model = Pangolin(L, W, AR).to(device)
                
                # Load weights with proper device mapping
                model_path = resource_filename("pangolin", f"models/final.{j}.{i}.3")
                weights = torch.load(model_path, weights_only=True, map_location=device)
                
                model.load_state_dict(weights)
                model.eval()
                pang_models.append(model)
                
            except Exception as e:
                print(f"Warning: Failed to load Pangolin model {j}.{i}: {e}")
                continue
                
except Exception as e:
    print(f"Error initializing Pangolin models: {e}")
    pang_models = []


def pang_one_hot_encode(seq: str) -> np.ndarray:
    """One-hot encode DNA sequence for Pangolin model.
    
    Args:
        seq: DNA sequence string
        
    Returns:
        One-hot encoded array of shape (len(seq), 4)
        
    Raises:
        ValueError: If sequence contains invalid characters
    """
    if not isinstance(seq, str):
        raise TypeError(f"Expected string, got {type(seq).__name__}")
    
    IN_MAP = np.asarray([[0, 0, 0, 0],  # N or unknown
                         [1, 0, 0, 0],  # A
                         [0, 1, 0, 0],  # C
                         [0, 0, 1, 0],  # G
                         [0, 0, 0, 1]]) # T
    
    # Validate sequence
    valid_chars = set('ACGTN')
    if not all(c.upper() in valid_chars for c in seq):
        raise ValueError("Sequence contains invalid characters (only A, C, G, T, N allowed)")
    
    # Convert to numeric representation
    seq = seq.upper().replace('A', '1').replace('C', '2')
    seq = seq.replace('G', '3').replace('T', '4').replace('N', '0')
    
    try:
        seq_array = np.asarray(list(map(int, list(seq))))
        return IN_MAP[seq_array.astype('int8')]
    except (ValueError, IndexError) as e:
        raise ValueError(f"Failed to encode sequence: {e}") from e




import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import os
import sys
import tensorflow as tf
import numpy as np
from keras.models import load_model
from importlib import resources


# Force device selection with error handling
def get_best_tensorflow_device():
    """Get the best available TensorFlow device."""
    try:
        # Try GPU first
        if tf.config.list_physical_devices('GPU'):
            return '/GPU:0'
        # Try MPS on macOS
        elif sys.platform == 'darwin' and tf.config.list_physical_devices('MPS'):
            return '/device:GPU:0'
        else:
            return '/CPU:0'
    except Exception as e:
        print(f"Warning: Device selection failed, using CPU: {e}")
        return '/CPU:0'

device = get_best_tensorflow_device()

# Model loading paths with error handling
def load_spliceai_models():
    """Load SpliceAI models with proper error handling."""
    try:
        if sys.platform == 'darwin':
            model_filenames = [f"models/spliceai{i}.h5" for i in range(1, 6)]
            model_paths = [resources.files('spliceai').joinpath(f) for f in model_filenames]
        else:
            model_paths = [f"/tamir2/nicolaslynn/tools/SpliceAI/spliceai/models/spliceai{i}.h5"
                           for i in range(1, 6)]
        
        # Load models onto correct device
        models = []
        with tf.device(device):
            for i, model_path in enumerate(model_paths):
                try:
                    model = load_model(str(model_path))
                    models.append(model)
                except Exception as e:
                    print(f"Warning: Failed to load SpliceAI model {i+1}: {e}")
                    continue
        
        if not models:
            raise RuntimeError("No SpliceAI models could be loaded")
            
        return models
        
    except Exception as e:
        print(f"Error loading SpliceAI models: {e}")
        return []

sai_models = load_spliceai_models()


print(f"SpliceAI loaded to {device}.")

def one_hot_encode(seq: str) -> np.ndarray:
    """One-hot encode DNA sequence for SpliceAI model.
    
    Args:
        seq: DNA sequence string
        
    Returns:
        One-hot encoded array of shape (len(seq), 4)
        
    Raises:
        ValueError: If sequence contains invalid characters
    """
    if not isinstance(seq, str):
        raise TypeError(f"Expected string, got {type(seq).__name__}")
    
    # Validate sequence
    valid_chars = set('ACGTN')
    if not all(c.upper() in valid_chars for c in seq):
        raise ValueError("Sequence contains invalid characters (only A, C, G, T, N allowed)")
    
    encoding_map = np.asarray([[0, 0, 0, 0],  # N or unknown
                               [1, 0, 0, 0],  # A
                               [0, 1, 0, 0],  # C
                               [0, 0, 1, 0],  # G
                               [0, 0, 0, 1]]) # T

    # Convert to numeric representation
    seq = seq.upper().replace('A', '\x01').replace('C', '\x02')
    seq = seq.replace('G', '\x03').replace('T', '\x04').replace('N', '\x00')

    try:
        return encoding_map[np.frombuffer(seq.encode('latin1'), np.int8) % 5]
    except Exception as e:
        raise ValueError(f"Failed to encode sequence: {e}") from e


def sai_predict_probs(seq: str, models: list) -> tuple[np.ndarray, np.ndarray]:
    """
    Predict donor and acceptor probabilities for each nt in seq using SpliceAI.
    Returns (acceptor_probs, donor_probs) as np.ndarray of shape (L,).
    """
    if not models:
        raise ValueError("No SpliceAI models loaded")

    if not isinstance(seq, str):
        raise TypeError(f"Expected string, got {type(seq).__name__}")

    if len(seq) < 1000:
        raise ValueError(f"Sequence too short: {len(seq)} (expected >= 1000)")

    try:
        x = one_hot_encode(seq)[None, :]
        preds = []
        for i, model in enumerate(models):
            try:
                pred = model.predict(x, verbose=0)
                preds.append(pred)
            except Exception as e:
                print(f"Warning: SpliceAI model {i+1} failed: {e}")
        if not preds:
            raise RuntimeError("All SpliceAI model predictions failed")

        y = np.mean(preds, axis=0)          # (1, L, 3)
        y = y[0, :, 1:].T                   # (2, L) -> [acceptor, donor]
        return y[0, :], y[1, :]

    except Exception as e:
        raise RuntimeError(f"SpliceAI prediction failed: {e}") from e


def run_spliceai_seq(
    seq: str,
    indices: Union[List[int], np.ndarray],
    threshold: float = 0.0,
) -> tuple[Dict[int, float], Dict[int, float]]:
    """
    Run SpliceAI on seq and return donor / acceptor sites above threshold.
    Returns (donor_indices, acceptor_indices) as dict[pos -> prob]
    """
    if not isinstance(seq, str):
        raise TypeError(f"Expected string sequence, got {type(seq).__name__}")

    if not isinstance(indices, (list, np.ndarray)):
        raise TypeError(f"Expected list or array for indices, got {type(indices).__name__}")

    if len(indices) != len(seq):
        raise ValueError(f"indices length ({len(indices)}) must match sequence length ({len(seq)})")

    if not isinstance(threshold, (int, float)):
        raise TypeError(f"Threshold must be numeric, got {type(threshold).__name__}")

    try:
        acc_probs, don_probs = sai_predict_probs(seq, models=sai_models)
        acceptor = {pos: p for pos, p in zip(indices, acc_probs) if p >= threshold}
        donor = {pos: p for pos, p in zip(indices, don_probs) if p >= threshold}
        return donor, acceptor
    except Exception as e:
        raise RuntimeError(f"SpliceAI sequence analysis failed: {e}") from e


def run_splicing_engine(
    seq: Optional[str] = None,
    engine: str = "spliceai",
) -> Tuple[List[float], List[float]]:
    """
    Run specified splicing engine to predict splice site probabilities.

    Returns:
        (donor_probs, acceptor_probs) as lists
    """
    from .utils import generate_random_sequence  # type: ignore

    if seq is None:
        seq = generate_random_sequence(15_001)

    if not isinstance(seq, str):
        raise TypeError(f"Sequence must be string, got {type(seq).__name__}")
    if not seq:
        raise ValueError("Sequence cannot be empty")

    valid_chars = set("ACGTN")
    if not all(c.upper() in valid_chars for c in seq):
        raise ValueError("Sequence contains invalid nucleotides (only A, C, G, T, N allowed)")

    try:
        match engine:
            case "spliceai":
                acc, don = sai_predict_probs(seq, models=sai_models)
                donor_probs, acceptor_probs = don.tolist(), acc.tolist()
            case "spliceai-pytorch":
                raise ValueError("spliceai-pytorch engine has been removed. Use 'spliceai' instead.")
            case "pangolin":
                donor_probs, acceptor_probs = pangolin_predict_probs(seq, models=pang_models)
            case _:
                raise ValueError(f"Engine '{engine}' not implemented. Available: 'spliceai', 'pangolin'")
    except ImportError as e:
        raise ImportError(f"Failed to import engine '{engine}': {e}") from e

    return donor_probs, acceptor_probs