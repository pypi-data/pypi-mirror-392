"""Point d'entrée enrichi pour orchestrer la simulation de trafic.

Ce module propose plusieurs scénarios de simulation, une vérification explicite
de la disponibilité de l'extension Cython ainsi qu'un mini benchmark pour
comparer les mises à jour de positions vectorisées.
"""

from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path
from typing import Iterable, Optional

from .core import (
    Analyseur,
    ConfigurationError,
    MissingDataError,
    Simulateur,
    SimulationError,
)
from .core.optimisation import calculer_moyenne_vitesse_acceleree
from .core.optimisation.cython_ext import update_positions
from .interface import Affichage, Export


PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = PACKAGE_ROOT / "data" / "config_reseau.json"


def parse_arguments() -> argparse.Namespace:
    """Construit le parseur CLI pour piloter l'application."""
    parser = argparse.ArgumentParser(description="Simulateur de trafic routier.")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Fichier de configuration JSON à charger.",
    )
    parser.add_argument(
        "--tours",
        type=int,
        default=60,
        help="Nombre de tours pour le scénario principal.",
    )
    parser.add_argument(
        "--delta",
        type=int,
        default=60,
        help="Pas de temps (secondes) pour le scénario principal.",
    )
    parser.add_argument(
        "--scenario-sup",
        action="store_true",
        help="Lance un second scénario de simulation avec des paramètres alternatifs.",
    )
    parser.add_argument(
        "--skip-graphics",
        action="store_true",
        help="Désactive la génération des graphiques afin d'accélérer l'exécution.",
    )
    parser.add_argument(
        "--benchmark-cython",
        action="store_true",
        help="Exécute un benchmark simple pour évaluer l'accélération Cython.",
    )
    parser.add_argument(
        "--taille-benchmark",
        type=int,
        default=50_000,
        help="Taille des vecteurs utilisés pour le benchmark Cython/Numba.",
    )
    parser.add_argument(
        "--iterations-benchmark",
        type=int,
        default=5,
        help="Nombre d'itérations utilisées pour lisser le benchmark.",
    )
    return parser.parse_args()


def verifier_extension_cython(taille: int, delta_t: float) -> None:
    """Vérifie la disponibilité de l'extension Cython et affiche un exemple."""
    positions = [float(i) for i in range(taille)]
    vitesses = [1.5 + (i % 5) for i in range(taille)]

    try:
        resultat = update_positions(positions, vitesses, delta_t)
    except Exception as exc:  # pragma: no cover - diagnostic manuel
        print("[Cython] Échec du calcul avec l'extension :", exc)
        print("         Basculer vers la version Python ou recompiler l'extension.")
        return

    module_source = getattr(update_positions, "__module__", "inconnu")
    print(f"[Cython] Extension chargée depuis: {module_source}")
    print(f"[Cython] Exemple de mise à jour -> premières valeurs: {resultat[:3]}")


def benchmark_cython(taille: int, iterations: int, delta_t: float = 1.0) -> None:
    """Compare les performances Cython/Python en s'appuyant sur update_positions."""
    positions = [float(i) for i in range(taille)]
    vitesses = [0.75 + (i % 7) * 0.5 for i in range(taille)]

    def run_once() -> float:
        start = time.perf_counter()
        update_positions(positions, vitesses, delta_t)
        return time.perf_counter() - start

    mesures = [run_once() for _ in range(iterations)]
    moyenne = statistics.mean(mesures)
    ecart_type = statistics.pstdev(mesures)
    print(
        "[Cython] Benchmark update_positions "
        f"(taille={taille}, essais={iterations}) -> "
        f"{moyenne * 1e3:.2f} ms ± {ecart_type * 1e3:.2f} ms"
    )


def afficher_etat_initial(affichage: Affichage) -> None:
    """Affiche l'état initial du réseau sur la console."""
    print("=== État initial ===")
    affichage.afficher_console()
    affichage.afficher_vehicules()


def analyser_resultats(analyseur: Analyseur) -> None:
    """Affiche un résumé des indicateurs après la simulation."""
    print("\n=== Analyse finale ===")
    try:
        moyenne = analyseur.calculer_vitesses_moyennes()
        print(f"Vitesse moyenne: {moyenne:.1f} km/h")
    except MissingDataError as exc:
        print(f"Vitesse moyenne indisponible: {exc}")

    zones = analyseur.detecter_zones_congestion()
    if zones:
        print(f"Zones congestionnées: {', '.join(zones)}")
    else:
        print("Zones congestionnées: aucune (trafic fluide)")


def exporter_statistiques(export: Export, statistiques: Iterable[dict]) -> None:
    """Déclenche les exports standards utilisés par le simulateur."""
    export.exporter_csv("resultats_vehicules.csv")
    export.exporter_json("resultats_reseau.json")
    export.exporter_statistiques(statistiques, "statistiques_simulation.json")


def executer_scenario(
    fichier_config: str,
    n_tours: int,
    delta_t: int,
    description: str,
    afficher_graphique: bool,
) -> Optional[Simulateur]:
    """Charge la configuration et exécute un scénario donné."""
    print(f"\n>>> Lancement du scénario: {description}")
    try:
        simulateur = Simulateur(fichier_config=fichier_config)
    except ConfigurationError as exc:
        print(f"[ERREUR] Initialisation impossible ({description}): {exc}")
        return None

    affichage = Affichage(simulateur.reseau)
    analyseur = Analyseur(simulateur.reseau)
    export = Export(simulateur.reseau)

    afficher_etat_initial(affichage)

    try:
        simulateur.lancer_simulation(n_tours=n_tours, delta_t=delta_t)
    except SimulationError as exc:
        print(f"[ERREUR] Simulation interrompue ({description}): {exc}")
        return None

    analyser_resultats(analyseur)

    if afficher_graphique:
        print("\n=== Visualisations ===")
        affichage.creer_graphique()
    else:
        print("\n=== Visualisations ===")
        print("Graphiques désactivés (option --skip-graphics).")

    exporter_statistiques(export, simulateur.statistiques)
    return simulateur


def scenario_alternatif(simulateur: Simulateur, multiplicateur: float) -> None:
    """Exécute un calcul supplémentaire sur les statistiques en mémoire."""
    print("\n=== Analyse complémentaire ===")
    vitesses = [vehicule.vitesse for vehicule in simulateur.reseau.vehicules]
    if not vitesses:
        print("Aucun véhicule enregistré, pas d'analyse complémentaire.")
        return

    moyenne_acceleree = calculer_moyenne_vitesse_acceleree(vitesses)
    objectif = moyenne_acceleree * multiplicateur
    print(
        f"Vitesse moyenne (Numba) : {moyenne_acceleree:.2f} km/h "
        f"-> objectif hypothétique: {objectif:.2f} km/h"
    )


def run() -> None:
    """Point d'entrée principal appelé par la CLI."""
    arguments = parse_arguments()

    verifier_extension_cython(taille=min(10, arguments.taille_benchmark), delta_t=1.0)

    simulateur_principal = executer_scenario(
        fichier_config=arguments.config,
        n_tours=arguments.tours,
        delta_t=arguments.delta,
        description="Scénario principal",
        afficher_graphique=not arguments.skip_graphics,
    )

    if simulateur_principal is not None:
        scenario_alternatif(simulateur_principal, multiplicateur=1.15)

    if arguments.scenario_sup:
        executer_scenario(
            fichier_config=arguments.config,
            n_tours=max(10, arguments.tours // 2),
            delta_t=max(10, arguments.delta // 2),
            description="Scénario secondaire (rythme accéléré)",
            afficher_graphique=False,
        )

    if arguments.benchmark_cython:
        benchmark_cython(
            taille=arguments.taille_benchmark,
            iterations=arguments.iterations_benchmark,
        )


if __name__ == "__main__":
    run()
