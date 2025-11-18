"""Hiérarchie d'exceptions spécifiques au simulateur de trafic."""

from __future__ import annotations


class SimulationError(Exception):
    """Classe de base pour toutes les erreurs du simulateur."""


class ConfigurationError(SimulationError):
    """Erreur liée à la lecture ou au contenu de la configuration."""


class ConfigurationFileNotFoundError(FileNotFoundError, ConfigurationError):
    """Erreur levée lorsque le fichier de configuration est introuvable."""


class ConfigurationFormatError(ConfigurationError, ValueError):
    """Erreur levée lorsque le fichier de configuration est mal formé."""


class InvalidSimulationParameterError(SimulationError, ValueError):
    """Erreur levée lorsque des paramètres de simulation invalides sont fournis."""


class RouteError(SimulationError):
    """Erreur générale liée à la gestion des routes."""


class RouteNotFoundError(RouteError, LookupError):
    """Erreur levée lorsqu'une route demandée n'existe pas dans le réseau."""


class RouteCapacityError(RouteError):
    """Erreur levée lorsqu'une route a atteint sa capacité maximale."""


class VehicleError(SimulationError):
    """Erreur générale liée à la gestion des véhicules."""


class VehicleAlreadyPresentError(VehicleError):
    """Erreur levée lorsqu'un véhicule est ajouté deux fois sur la même route."""


class InvalidVehicleStateError(VehicleError, ValueError):
    """Erreur levée lorsque l'état d'un véhicule est invalide."""


class AnalysisError(SimulationError):
    """Erreur générique soulevée lors des analyses et statistiques."""


class MissingDataError(AnalysisError):
    """Erreur levée lorsqu'une analyse nécessite des données indisponibles."""


class DivisionByZeroAnalysisError(AnalysisError, ZeroDivisionError):
    """Erreur levée lorsqu'un calcul statistique conduit à une division par zéro."""

