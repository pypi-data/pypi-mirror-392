"""Route package exposing the road entity used in simulations."""

from .feu_rouge import FeuRouge
from .route import Route

__all__ = ["Route", "FeuRouge"]
