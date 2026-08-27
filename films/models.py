"""
Les MODÈLES : la description de nos tables en base de données.

Un modèle Django = une classe Python = une table SQL.
Un attribut de la classe = une colonne de la table.

Ici on a deux modèles liés par une ForeignKey :

    Realisateur  1 ------- N  Film

Un réalisateur peut avoir plusieurs films, un film a un seul réalisateur.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Realisateur(models.Model):
    """Le « côté 1 » de la relation : la personne qui réalise des films."""

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    nationalite = models.CharField(max_length=100, blank=True)
    date_naissance = models.DateField(
        null=True,
        blank=True,
        help_text="Sert à vérifier qu'un film ne sort pas avant la naissance du réalisateur.",
    )

    class Meta:
        verbose_name = "réalisateur"
        verbose_name_plural = "réalisateurs"
        # Tri par défaut : dès qu'on fait Realisateur.objects.all(), c'est trié ainsi.
        ordering = ["nom", "prenom"]
        # Contrainte SQL : on ne peut pas créer deux fois la même personne.
        constraints = [
            models.UniqueConstraint(
                fields=["nom", "prenom"], name="realisateur_unique_nom_prenom"
            )
        ]

    def __str__(self):
        """Ce que Django affiche partout (admin, shell, templates) pour cet objet."""
        return f"{self.prenom} {self.nom}"

    @property
    def nombre_de_films(self):
        """Propriété calculée : pratique dans les templates et l'API.

        `self.films` existe grâce au `related_name="films"` déclaré sur Film.realisateur.
        """
        return self.films.count()


class Film(models.Model):
    """Le « côté N » de la relation : c'est lui qui porte la ForeignKey."""

    # TextChoices = liste fermée de valeurs autorisées.
    # En base on stocke le code court ("SF"), à l'écran on affiche le libellé.
    class Genre(models.TextChoices):
        ACTION = "ACTION", "Action"
        COMEDIE = "COMEDIE", "Comédie"
        DRAME = "DRAME", "Drame"
        SF = "SF", "Science-fiction"
        HORREUR = "HORREUR", "Horreur"
        ANIMATION = "ANIMATION", "Animation"
        DOCUMENTAIRE = "DOCU", "Documentaire"

    titre = models.CharField(max_length=200)

    # LA RELATION demandée par le cahier des charges.
    #   - on_delete=CASCADE : si on supprime le réalisateur, ses films partent avec lui.
    #   - related_name="films" : permet d'écrire `mon_realisateur.films.all()`.
    realisateur = models.ForeignKey(
        Realisateur,
        on_delete=models.CASCADE,
        related_name="films",
        verbose_name="réalisateur",
    )

    annee_sortie = models.PositiveIntegerField(
        "année de sortie",
        validators=[MinValueValidator(1895), MaxValueValidator(2100)],
    )
    duree_minutes = models.PositiveIntegerField(
        "durée (minutes)",
        validators=[MinValueValidator(1), MaxValueValidator(600)],
    )
    genre = models.CharField(max_length=20, choices=Genre.choices, default=Genre.DRAME)
    synopsis = models.TextField(blank=True)
    note = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Note sur 10, avec une décimale (ex: 8.5). Peut rester vide.",
    )
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-annee_sortie", "titre"]
        constraints = [
            # Un même réalisateur ne peut pas avoir deux films au titre identique.
            models.UniqueConstraint(
                fields=["titre", "realisateur"], name="film_unique_titre_par_realisateur"
            )
        ]

    def __str__(self):
        return f"{self.titre} ({self.annee_sortie})"

    @property
    def duree_lisible(self):
        """Convertit 142 minutes en « 2h22 » pour l'affichage HTML."""
        heures, minutes = divmod(self.duree_minutes, 60)
        return f"{heures}h{minutes:02d}" if heures else f"{minutes} min"

    @property
    def est_recent(self):
        return self.annee_sortie >= timezone.now().year - 5
