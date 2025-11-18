"""Outils d'analyse pour extraire des métriques du réseau simulé."""

from __future__ import annotations

from typing import List, Sequence

from ..exceptions import DivisionByZeroAnalysisError, MissingDataError
from ..optimisation import calculer_moyenne_vitesse_acceleree
from ...models.route import Route
from ...models.vehicule import Vehicule


class Analyseur:
    """Fournit des indicateurs de performance du réseau routier."""

    def __init__(self, reseau) -> None:
        """Crée un analyseur lié au réseau simulé."""
        self.reseau = reseau

    def calculer_vitesses_moyennes(self) -> float:
        """Calcule la vitesse moyenne actuelle de l'ensemble des véhicules."""
        vehicules: Sequence[Vehicule] = self.reseau.vehicules
        if not vehicules:
            raise MissingDataError(
                "Impossible de calculer la vitesse moyenne sans véhicules dans le réseau."
            )

        try:
            return calculer_moyenne_vitesse_acceleree(
                vehicule.vitesse for vehicule in vehicules
            )
        except ValueError as exc:
            raise MissingDataError(
                "Données insuffisantes pour calculer la vitesse moyenne."
            ) from exc
        except ZeroDivisionError as exc:
            raise DivisionByZeroAnalysisError(
                "Division par zéro lors du calcul de la vitesse moyenne."
            ) from exc

    def detecter_zones_congestion(self) -> List[str]:
        """Identifie les routes dont la charge dépasse le seuil de congestion."""
        zones_congestionnees: List[str] = []
        for route in self.reseau.routes:
            if len(route.vehicules_presents) > 5:
                zones_congestionnees.append(route.nom)
        return zones_congestionnees

    def calculer_temps_parcours(self, route: Route) -> float:
        """Estime le temps de parcours d'une route en supposant la vitesse limite."""
        if route.limite_vitesse <= 0:
            raise DivisionByZeroAnalysisError(
                f"Impossible de calculer un temps de parcours pour la route {route.nom} "
                "sans limite de vitesse positive."
            )

        return route.longueur / route.limite_vitesse
