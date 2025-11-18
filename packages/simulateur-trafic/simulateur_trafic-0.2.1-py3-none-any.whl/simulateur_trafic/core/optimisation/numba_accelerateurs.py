"""Accélérateurs basés sur Numba pour les calculs numériques."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

import numba

@numba.njit(cache=True, fastmath=True)
def _moyenne_numba(vitesses: np.ndarray) -> float:  
    """Version compilée avec Numba du calcul de moyenne."""
    total = 0.0
    taille = vitesses.shape[0]
    for index in range(taille):
        total += vitesses[index]
    return total / taille


def calculer_moyenne_vitesse_acceleree(vitesses: Iterable[float]) -> float:
    """Calcule la moyenne des vitesses en utilisant Numba si disponible."""
    vitesses_tuple: tuple[float, ...] = tuple(vitesses)
    if not vitesses_tuple:
        raise ValueError("Aucune vitesse fournie pour le calcul de moyenne.")
    tableau = np.ascontiguousarray(vitesses_tuple, dtype=np.float64)
    return float(_moyenne_numba(tableau))


