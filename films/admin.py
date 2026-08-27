"""
L'ADMIN Django : une interface CRUD générée automatiquement, dispo sur /admin/.

Le principe est toujours le même :
    1. on écrit une classe de configuration qui hérite de admin.ModelAdmin
    2. on la branche sur un modèle avec le décorateur @admin.register(MonModele)
"""

from django.contrib import admin

from .models import Film, Realisateur


class FilmInline(admin.TabularInline):
    """Permet d'éditer les films DIRECTEMENT dans la fiche du réalisateur.

    C'est possible uniquement parce que Film pointe vers Realisateur (ForeignKey).
    """

    model = Film
    extra = 1  # nombre de lignes vides proposées
    fields = ["titre", "annee_sortie", "genre", "duree_minutes", "note"]


@admin.register(Realisateur)
class RealisateurAdmin(admin.ModelAdmin):
    list_display = ["nom", "prenom", "nationalite", "nombre_de_films"]
    list_filter = ["nationalite"]
    search_fields = ["nom", "prenom"]
    inlines = [FilmInline]

    @admin.display(description="Nombre de films")
    def nombre_de_films(self, obj):
        """Une colonne calculée : l'admin appelle cette méthode pour chaque ligne."""
        return obj.films.count()


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ["titre", "realisateur", "annee_sortie", "genre", "duree_lisible", "note"]
    list_filter = ["genre", "annee_sortie", "realisateur"]
    search_fields = ["titre", "synopsis", "realisateur__nom"]  # __ = on traverse la relation
    autocomplete_fields = ["realisateur"]  # évite un <select> avec 10 000 options
    list_select_related = ["realisateur"]  # optimisation : 1 requête SQL au lieu de N+1

    fieldsets = [
        ("Identité du film", {"fields": ["titre", "realisateur", "annee_sortie"]}),
        ("Caractéristiques", {"fields": ["genre", "duree_minutes", "note"]}),
        ("Contenu", {"fields": ["synopsis"]}),
    ]
