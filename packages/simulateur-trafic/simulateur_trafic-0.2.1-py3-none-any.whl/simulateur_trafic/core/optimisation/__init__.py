"""Outils d'optimisation de performance pour le simulateur."""

from __future__ import annotations

from typing import Iterable

try:  # pragma: no cover - dépend de l'environnement d'exécution
    from .numba_accelerateurs import calculer_moyenne_vitesse_acceleree
except Exception:  # pragma: no cover - fallback pur Python

    def calculer_moyenne_vitesse_acceleree(vitesses: Iterable[float]) -> float:
        """Calcule la moyenne en Python pur si l'accélération n'est pas disponible."""
        vitesses_tuple = tuple(vitesses)
        if not vitesses_tuple:
            raise ValueError("Aucune vitesse fournie pour le calcul de moyenne.")
        return sum(vitesses_tuple) / len(vitesses_tuple)


__all__ = ["calculer_moyenne_vitesse_acceleree"]
