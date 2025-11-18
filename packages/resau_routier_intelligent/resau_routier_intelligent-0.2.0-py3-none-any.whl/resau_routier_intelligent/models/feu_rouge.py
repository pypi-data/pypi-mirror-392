"""Module pour la gestion des feux rouges."""

from enum import Enum


class EtatFeu(Enum):
    """États possibles d'un feu rouge."""

    VERT = "vert"
    ORANGE = "orange"
    ROUGE = "rouge"


class FeuRouge:
    """Classe représentant un feu de circulation."""

    def __init__(self, cycle: float = 5.0, duree_orange: float = 1.0):
        """
        Initialise un feu rouge.

        Args:
            cycle: Durée totale d'un cycle complet (vert + orange + rouge) en minutes
            duree_orange: Durée de l'état orange en minutes
        """
        self.cycle = cycle
        self.duree_orange = duree_orange
        self.temps_ecoule = 0.0
        self._etat_actuel = EtatFeu.VERT

        # Calcul des durées pour chaque état
        # Vert et rouge ont la même durée, orange est plus court
        self.duree_vert = (cycle - duree_orange) / 2
        self.duree_rouge = (cycle - duree_orange) / 2

    @property
    def etat(self) -> str:
        """Retourne l'état actuel du feu ('vert', 'orange', 'rouge')."""
        return self._etat_actuel.value

    def avancer_temps(self, dt: float) -> None:
        """
        Fait avancer le temps et change l'état du feu si nécessaire.

        Args:
            dt: Intervalle de temps en minutes
        """
        self.temps_ecoule += dt

        # Réinitialiser si on dépasse le cycle complet
        if self.temps_ecoule >= self.cycle:
            self.temps_ecoule = self.temps_ecoule % self.cycle

        # Déterminer l'état selon le temps écoulé
        if self.temps_ecoule < self.duree_vert:
            self._etat_actuel = EtatFeu.VERT
        elif self.temps_ecoule < self.duree_vert + self.duree_orange:
            self._etat_actuel = EtatFeu.ORANGE
        else:
            self._etat_actuel = EtatFeu.ROUGE

    def reinitialiser(self) -> None:
        """Réinitialise le feu à l'état vert."""
        self.temps_ecoule = 0.0
        self._etat_actuel = EtatFeu.VERT
