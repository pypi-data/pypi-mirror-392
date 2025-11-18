"""Entités et logique associées au réseau routier simulé."""

from __future__ import annotations

from typing import Any, Dict, List

from ...core.exceptions import RouteNotFoundError, VehicleError
from ..route import Route


class ReseauRoutier:
    """Représente le réseau routier composé de routes, intersections et véhicules."""

    def __init__(self) -> None:
        """Initialise les collections représentant l'état du réseau."""
        self.routes: List[Route] = []
        self.intersections: List[Any] = []
        self.vehicules: List["Vehicule"] = []

    def ajouter_route(self, route: Route) -> None:
        """Ajoute une route au réseau."""
        if route not in self.routes:
            self.routes.append(route)

    def creer_route_depuis_config(self, data: Dict[str, Any]) -> Route:
        """Construit une instance de ``Route`` à partir d'un dictionnaire."""
        return Route(
            data["nom"],
            data["longueur"],
            data["limite_vitesse"],
            data.get("capacite_max"),
        )

    def ajouter_intersection(self, intersection: Any) -> None:
        """Ajoute une intersection au réseau."""
        self.intersections.append(intersection)

    def ajouter_vehicule(self, vehicule: "Vehicule") -> None:
        """Référence un véhicule dans le réseau et la route associée."""
        route = vehicule.route_actuelle
        if route is None:
            raise VehicleError(
                f"Le véhicule {vehicule.identifiant} n'est associé à aucune route."
            )

        if route not in self.routes:
            raise RouteNotFoundError(
                f"La route {route.nom} du véhicule {vehicule.identifiant} est inconnue."
            )

        if vehicule not in self.vehicules:
            self.vehicules.append(vehicule)

        if vehicule not in route.vehicules_presents:
            route.ajouter_vehicule(vehicule)

    def mettre_a_jour_reseau(self, delta_t: float = 1.0) -> None:
        """Met à jour la position de tous les véhicules présents sur les routes."""
        for route in self.routes:
            route.mettre_a_jour_vehicules(delta_t)

    def obtenir_route(self, nom_route: str) -> Route:
        """Retourne une route par son nom ou lève une erreur si elle n'existe pas."""
        for route in self.routes:
            if route.nom == nom_route:
                return route
        raise RouteNotFoundError(f"La route {nom_route} est introuvable dans le réseau.")

    def obtenir_etat_reseau(self) -> Dict[str, int]:
        """Retourne un instantané des éléments suivis dans le réseau."""
        return {
            "nombre_routes": len(self.routes),
            "nombre_intersections": len(self.intersections),
            "nombre_vehicules": len(self.vehicules),
        }
