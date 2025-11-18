"""Spécifie le comportement d'un véhicule dans le réseau simulé."""

from __future__ import annotations

from typing import Optional

from ...core.exceptions import InvalidVehicleStateError


class Vehicule:
    """Modélise un véhicule se déplaçant sur une route."""

    def __init__(
        self,
        identifiant: str,
        position: float = 0,
        vitesse: float = 50,
        route_actuelle: Optional["Route"] = None,
    ) -> None:
        """Initialise un véhicule avec son état courant."""
        self.identifiant = identifiant
        self.route_actuelle = route_actuelle
        self.vitesse = vitesse
        self.position = position

        self._valider_vitesse()
        self._valider_position(position)

    def _valider_vitesse(self) -> None:
        if self.vitesse < 0:
            raise InvalidVehicleStateError(
                f"Vitesse négative ({self.vitesse}) pour le véhicule {self.identifiant}."
            )

    def _valider_route(self) -> None:
        if self.route_actuelle and self.route_actuelle.longueur <= 0:
            raise InvalidVehicleStateError(
                f"Route {self.route_actuelle.nom} de longueur nulle ou négative."
            )

    def _valider_delta(self, delta_t: float) -> None:
        if delta_t <= 0:
            raise InvalidVehicleStateError(
                f"Le pas de temps doit être positif (reçu: {delta_t})."
            )

    def _valider_position(self, position: float) -> None:
        if position < 0:
            raise InvalidVehicleStateError(
                f"Position négative ({position}) pour le véhicule {self.identifiant}."
            )
        if self.route_actuelle and position > self.route_actuelle.longueur:
            raise InvalidVehicleStateError(
                f"Le véhicule {self.identifiant} dépasse la longueur de la route "
                f"{self.route_actuelle.nom} ({self.route_actuelle.longueur})."
            )

    def calculer_position_future(self, delta_t: float = 1.0) -> float:
        """Calcule la prochaine position en vérifiant tous les prérequis."""
        if self.route_actuelle is None:
            raise InvalidVehicleStateError(
                f"Le véhicule {self.identifiant} n'est associé à aucune route."
            )

        self.verifier_deplacement(delta_t)

        nouvelle_position = self.position + self.vitesse * delta_t
        self._valider_position(nouvelle_position)
        return nouvelle_position

    def verifier_deplacement(self, delta_t: float = 1.0) -> None:
        """Valide que le véhicule peut avancer avec le pas de temps fourni."""
        self._valider_delta(delta_t)
        self._valider_vitesse()
        self._valider_route()

    def verifier_position(self, nouvelle_position: float) -> None:
        """Vérifie qu'une position cible est cohérente avec l'état du véhicule."""
        self._valider_position(nouvelle_position)

    def avancer(self, delta_t: float = 1.0) -> None:
        """Fait progresser le véhicule le long de sa route actuelle."""
        if self.route_actuelle is None:
            return

        nouvelle_position = self.calculer_position_future(delta_t)
        self.position = nouvelle_position

    def changer_de_route(self, nouvelle_route: "Route") -> None:
        """Positionne le véhicule sur une nouvelle route et réinitialise la position."""
        if nouvelle_route is None:
            raise InvalidVehicleStateError(
                f"Le véhicule {self.identifiant} doit être associé à une route valide."
            )
        self.route_actuelle = nouvelle_route
        self._valider_route()
        self.position = 0
