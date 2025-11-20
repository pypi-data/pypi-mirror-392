"""
Matplotlab - Extended Plotting and ML Utilities
================================================

A comprehensive library covering:
- Reinforcement Learning (rl)
- Artificial Neural Networks (ann)
- Speech Processing (sp)

Usage:
    from matplotlab import rl, ann, sp

Author: ML Community
Date: 2025
"""

__version__ = "0.1.6"
__author__ = "ML Community"

# Import submodules
from . import rl
from . import ann
from . import sp

__all__ = ["rl", "ann", "sp"]
