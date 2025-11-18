"""Interface Python pour l'extension Cython de mise à jour des positions."""

from __future__ import annotations

from typing import Iterable, Sequence

try:  # pragma: no cover - import optionnel
    from ._position_update import update_positions as _update_positions
except ImportError:  # pragma: no cover - la version compilée peut être absente
    _update_positions = None  # type: ignore[assignment]


def update_positions(
    positions: Sequence[float],
    vitesses: Sequence[float],
    delta_t: float = 1.0,
) -> list[float]:
    """Calcule les nouvelles positions en utilisant Cython si disponible.

    Parameters
    ----------
    positions: Sequence[float]
        Positions courantes des véhicules.
    vitesses: Sequence[float]
        Vitesses actuelles des véhicules.
    delta_t: float
        Pas de temps appliqué au déplacement.
    """
    if _update_positions is None:
        return [
            position + vitesse * delta_t
            for position, vitesse in zip(positions, vitesses)
        ]

    return list(_update_positions(positions, vitesses, delta_t))


__all__ = ["update_positions"]

