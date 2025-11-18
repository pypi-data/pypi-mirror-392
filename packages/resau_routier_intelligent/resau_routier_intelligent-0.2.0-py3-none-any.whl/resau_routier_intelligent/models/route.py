from typing import Dict, List, Optional, Tuple

from .vehicule import Vehicule


class Route:
    """Classe représentant une route dans le réseau."""

    def __init__(self, nom: str, longueur: float, limite_vitesse: float = 50):
        self.nom = nom
        self.longueur = longueur  # km
        self.limite_vitesse = limite_vitesse  # km/h
        self.vehicules: List[Vehicule] = []
        self.routes_connectees: List["Route"] = []
        self.reseau: Optional["ReseauRoutier"] = None

        # Statistiques
        self.nb_vehicules_passes = 0
        self.temps_moyen_parcours = 0.0
        self.vitesse_moyenne = 0.0

        # NOUVEAU : Gestion des feux rouges
        self.feux_rouges: List[Tuple["FeuRouge", float]] = []

    def ajouter_vehicule(self, vehicule: Vehicule) -> None:
        """Ajoute un véhicule à la route."""
        if vehicule in self.vehicules:
            raise ValueError
        self.vehicules.append(vehicule)
        vehicule.route_actuelle = self
        self.nb_vehicules_passes += 1

    def retirer_vehicule(self, vehicule: Vehicule) -> None:
        """Retire un véhicule de la route."""
        if vehicule in self.vehicules:
            self.vehicules.remove(vehicule)

    def ajouter_feu_rouge(self, feu: "FeuRouge", position: float = None) -> None:
        """
        Ajoute un feu rouge à la route.

        Args:
            feu: Instance de FeuRouge
            position: Position du feu sur la route (en km).
                     Si None, place le feu à la fin de la route.
        """
        if position is None:
            position = self.longueur

        if position < 0 or position > self.longueur:
            raise ValueError(f"Position {position} invalide pour route de {self.longueur}km")

        self.feux_rouges.append((feu, position))
        # Trier par position pour faciliter les vérifications
        self.feux_rouges.sort(key=lambda x: x[1])

    def retirer_feu_rouge(self, feu: "FeuRouge") -> None:
        """Retire un feu rouge de la route."""
        self.feux_rouges = [(f, p) for f, p in self.feux_rouges if f != feu]

    def mettre_a_jour_vehicules(self, delta_t: float) -> None:
        """Met à jour tous les véhicules et feux présents sur la route."""
        # Mettre à jour tous les feux rouges
        for feu, _ in self.feux_rouges:
            feu.avancer_temps(delta_t)

        # Mettre à jour chaque véhicule
        for vehicule in self.vehicules[:]:
            # Vérifier si le véhicule doit s'arrêter à un feu rouge
            doit_arreter = self._vehicule_doit_arreter_au_feu(vehicule)

            if doit_arreter:
                # Arrêter le véhicule temporairement
                vitesse_originale = vehicule.vitesse_actuelle
                vehicule.vitesse_actuelle = 0
                vehicule.avancer(0)  # Juste pour mettre à jour l'historique
                vehicule.vitesse_actuelle = vitesse_originale
            else:
                # Avancer normalement
                vehicule.avancer(delta_t)

        self._mettre_a_jour_statistiques()

    def _vehicule_doit_arreter_au_feu(self, vehicule: "Vehicule") -> bool:
        """
        Vérifie si un véhicule doit s'arrêter à un feu rouge.

        Args:
            vehicule: Le véhicule à vérifier

        Returns:
            True si le véhicule doit s'arrêter, False sinon
        """
        if not self.feux_rouges:
            return False

        # Distance de sécurité avant le feu (50m = 0.05km)
        distance_securite = 0.05

        for feu, position_feu in self.feux_rouges:
            # Vérifier si le véhicule approche ce feu
            distance_au_feu = position_feu - vehicule.position

            # Le véhicule est avant le feu et suffisamment proche
            if 0 < distance_au_feu <= distance_securite:
                # Arrêter seulement si le feu est rouge ou orange
                if feu.etat in ["rouge", "orange"]:
                    return True

        return False

    def obtenir_info_feux(self) -> List[Dict]:
        """Retourne les informations sur tous les feux de la route."""
        return [
            {
                "position": position,
                "etat": feu.etat,
                "temps_ecoule": feu.temps_ecoule,
                "cycle": feu.cycle,
            }
            for feu, position in self.feux_rouges
        ]

    def calculer_densite_trafic(self) -> float:
        """Calcule la densité de trafic (véhicules par km)."""
        return len(self.vehicules) / max(self.longueur, 0.1)

    def connecter_route(self, route: "Route") -> None:
        """Connecte cette route à une autre route."""
        if route not in self.routes_connectees:
            self.routes_connectees.append(route)
        if self not in route.routes_connectees:
            route.routes_connectees.append(self)

    def _mettre_a_jour_statistiques(self) -> None:
        """Met à jour les statistiques de la route."""
        if self.vehicules:
            self.vitesse_moyenne = sum(v.vitesse_actuelle for v in self.vehicules) / len(
                self.vehicules
            )
        else:
            self.vitesse_moyenne = 0.0

    def obtenir_statistiques(self) -> Dict:
        """Retourne les statistiques de la route."""
        return {
            "nom": self.nom,
            "vehicules_actuels": len(self.vehicules),
            "vehicules_passes": self.nb_vehicules_passes,
            "densite_trafic": self.calculer_densite_trafic(),
            "vitesse_moyenne": self.vitesse_moyenne,
            "limite_vitesse": self.limite_vitesse,
            "longueur": self.longueur,
        }
