"""Définition d'une route utilisée dans le réseau simulé."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from ...core.exceptions import (
    InvalidSimulationParameterError,
    RouteCapacityError,
    VehicleAlreadyPresentError,
)
from ...core.optimisation.cython_ext import update_positions

if TYPE_CHECKING:  # pragma: no cover - utilisé uniquement pour les types
    from ..vehicule import Vehicule
    from .feu_rouge import FeuRouge


class Route:
    """Représente un tronçon de route sur lequel circulent des véhicules."""

    def __init__(
        self,
        nom: str,
        longueur: float,
        limite_vitesse: float,
        capacite_max: Optional[int] = None,
    ) -> None:
        """Construit une route avec ses caractéristiques principales."""
        if longueur <= 0:
            raise InvalidSimulationParameterError(
                f"Longueur négative ou nulle ({longueur}) pour la route {nom}."
            )
        if limite_vitesse <= 0:
            raise InvalidSimulationParameterError(
                f"Limite de vitesse négative ou nulle ({limite_vitesse}) pour la route {nom}."
            )
        if capacite_max is not None and capacite_max <= 0:
            raise InvalidSimulationParameterError(
                f"Capacité maximale invalide ({capacite_max}) pour la route {nom}."
            )

        self.nom = nom
        self.longueur = longueur
        self.limite_vitesse = limite_vitesse
        self.capacite_max = capacite_max
        self.vehicules_presents: List["Vehicule"] = []
        self.feu_rouge: Optional["FeuRouge"] = None
        self.position_feu: Optional[float] = None

    def ajouter_vehicule(self, vehicule: "Vehicule") -> None:
        """Ajoute un véhicule à la route si celui-ci n'est pas déjà présent."""
        if vehicule in self.vehicules_presents:
            raise VehicleAlreadyPresentError(
                f"Le véhicule {vehicule.identifiant} circule déjà sur la route {self.nom}."
            )

        if self.capacite_max is not None and len(self.vehicules_presents) >= self.capacite_max:
            raise RouteCapacityError(
                f"La route {self.nom} a atteint sa capacité maximale ({self.capacite_max})."
            )

        if vehicule.route_actuelle is not self:
            vehicule.changer_de_route(self)

        self.vehicules_presents.append(vehicule)

    def ajouter_feu_rouge(self, feu: "FeuRouge", position: Optional[float] = None) -> None:
        """Ajoute un feu rouge sur la route et enregistre sa position."""
        if position is None:
            position = self.longueur / 2
        if position < 0 or position > self.longueur:
            raise InvalidSimulationParameterError(
                f"Position du feu ({position}) hors des bornes de la route {self.nom}."
            )
        self.feu_rouge = feu
        self.position_feu = position

    def mettre_a_jour_vehicules(self, delta_t: float = 1.0) -> None:
        """Demande à chaque véhicule présent de mettre à jour sa position."""
        if not self.vehicules_presents:
            return

        vehicules = list(self.vehicules_presents)

        for vehicule in vehicules:
            vehicule.verifier_deplacement(delta_t)

        if self._feu_rouge_actif():
            self._mettre_a_jour_avec_feu(vehicules, delta_t)
            return

        self._mettre_a_jour_vectorisee(vehicules, delta_t)

    def _mettre_a_jour_vectorisee(self, vehicules: List["Vehicule"], delta_t: float) -> None:
        """Met à jour les positions en tirant parti de l'extension Cython si disponible."""
        positions = [vehicule.position for vehicule in vehicules]
        vitesses = [vehicule.vitesse for vehicule in vehicules]
        try:
            nouvelles_positions = update_positions(positions, vitesses, delta_t)
        except Exception:  # pragma: no cover - fallback si extension indispo
            for vehicule in vehicules:
                vehicule.avancer(delta_t)
            return

        for vehicule, nouvelle_position in zip(vehicules, nouvelles_positions):
            vehicule.verifier_position(nouvelle_position)
            vehicule.position = nouvelle_position

    def _mettre_a_jour_avec_feu(self, vehicules: List["Vehicule"], delta_t: float) -> None:
        """Met à jour les véhicules en tenant compte du feu rouge actif."""
        assert self.position_feu is not None
        for vehicule in vehicules:
            prochaine_position = vehicule.calculer_position_future(delta_t)
            if vehicule.position < self.position_feu <= prochaine_position:
                continue
            vehicule.position = prochaine_position

    def _feu_rouge_actif(self) -> bool:
        """Indique si un feu rouge empêche actuellement les déplacements."""
        return (
            self.feu_rouge is not None
            and getattr(self.feu_rouge, "etat", None) == "rouge"
            and self.position_feu is not None
        )

    def update(self, dt: float = 1.0) -> None:
        """Met à jour le feu et les véhicules pour un pas de temps donné."""
        if self.feu_rouge is not None:
            avancer = getattr(self.feu_rouge, "avancer_temps", None)
            if callable(avancer):
                avancer(dt)
        self.mettre_a_jour_vehicules(dt)
