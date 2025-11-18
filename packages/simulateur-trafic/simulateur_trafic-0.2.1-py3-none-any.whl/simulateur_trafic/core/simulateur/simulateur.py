"""Simulation logic for loading a traffic network and running it."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from ..exceptions import (
    ConfigurationError,
    ConfigurationFileNotFoundError,
    ConfigurationFormatError,
    InvalidSimulationParameterError,
    RouteNotFoundError,
    SimulationError,
)
from ...models.reseau import ReseauRoutier
from ...models.vehicule import Vehicule


class Simulateur:
    """Pilote la simulation d'un réseau routier et centralise les statistiques."""

    def __init__(self, fichier_config: Optional[str] = None) -> None:
        """Crée un simulateur et charge éventuellement une configuration initiale.

        Parameters
        ----------
        fichier_config: Optional[str]
            Chemin vers un fichier JSON décrivant les routes et les véhicules
            à instancier avant de démarrer la simulation. Si ``None`` est
            fourni, le réseau reste vide.
        """
        self.reseau = ReseauRoutier()
        self.statistiques: list[Dict[str, Any]] = []
        self.tour_actuel = 0

        if fichier_config:
            self.charger_config(fichier_config)

    def charger_config(self, fichier_config: str) -> None:
        """Initialise le réseau routier à partir d'un fichier de configuration.

        Le fichier doit contenir deux listes ``routes`` et ``vehicules`` décrivant
        respectivement les tronçons routiers et les véhicules à ajouter.
        """
        chemin = Path(fichier_config)
        if not chemin.exists():
            raise ConfigurationFileNotFoundError(
                f"Fichier de configuration introuvable: {fichier_config}"
            )

        try:
            with chemin.open("r", encoding="utf-8") as fichier:
                config: Dict[str, Iterable[Dict[str, Any]]] = json.load(fichier)
        except FileNotFoundError as exc:
            raise ConfigurationFileNotFoundError(
                f"Fichier de configuration introuvable: {fichier_config}"
            ) from exc
        except JSONDecodeError as exc:
            raise ConfigurationFormatError(
                f"Le fichier {fichier_config} n'est pas un JSON valide."
            ) from exc

        try:
            routes = config["routes"]
            vehicules = config["vehicules"]
        except KeyError as exc:
            raise ConfigurationFormatError(
                "Le fichier de configuration doit contenir les clés 'routes' et 'vehicules'."
            ) from exc

        for route_data in routes:
            try:
                route = self.reseau.creer_route_depuis_config(route_data)
                self.reseau.ajouter_route(route)
            except (KeyError, InvalidSimulationParameterError) as exc:
                raise ConfigurationFormatError(
                    f"Définition de route invalide: {route_data}"
                ) from exc

        for vehicule_data in vehicules:
            try:
                self._creer_et_ajouter_vehicule(vehicule_data)
            except SimulationError:
                raise
            except KeyError as exc:
                raise ConfigurationFormatError(
                    f"Définition de véhicule invalide: {vehicule_data}"
                ) from exc

    def _creer_et_ajouter_vehicule(self, vehicule_data: Dict[str, Any]) -> None:
        """Instancie un véhicule et l'ajoute au réseau avec gestion d'erreurs."""
        vehicule = Vehicule(
            vehicule_data["identifiant"],
            vehicule_data.get("position", 0),
            vehicule_data.get("vitesse", 0),
        )
        nom_route = vehicule_data["route"]
        route = self.reseau.obtenir_route(nom_route)
        vehicule.changer_de_route(route)
        self.reseau.ajouter_vehicule(vehicule)

    def lancer_simulation(self, n_tours: int, delta_t: int) -> None:
        """Exécute la simulation sur un nombre de tours fixé.

        Parameters
        ----------
        n_tours: int
            Nombre d'itérations à exécuter.
        delta_t: int
            Pas de temps utilisé pour chaque itération (réservé pour de
            potentielles évolutions du modèle).
        """
        if n_tours <= 0:
            raise InvalidSimulationParameterError(
                f"Le nombre de tours doit être strictement positif (reçu: {n_tours})."
            )
        if delta_t <= 0:
            raise InvalidSimulationParameterError(
                f"Le pas de temps doit être strictement positif (reçu: {delta_t})."
            )

        try:
            for tour in range(n_tours):
                self.tour_actuel = tour
                self.reseau.mettre_a_jour_reseau(delta_t)

                statistiques_tour = {
                    "tour": tour,
                    "vehicules": len(self.reseau.vehicules),
                    "delta_t": delta_t,
                }
                self.statistiques.append(statistiques_tour)
        except SimulationError:
            raise
        except Exception as exc:  # pragma: no cover - sécurité supplémentaire
            raise SimulationError(f"Erreur inattendue lors de la simulation: {exc}") from exc
