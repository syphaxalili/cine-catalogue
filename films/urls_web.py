"""
Les URLs des pages HTML classiques (celles qui renvoient un template).

`app_name` crée un espace de noms : dans les templates on écrira
{% url 'films:detail_film' film.id %} et jamais l'URL en dur.
"""

from django.urls import path

from . import views

app_name = "films"

urlpatterns = [
    path("", views.liste_films, name="liste_films"),
    path("films/<int:pk>/", views.detail_film, name="detail_film"),
    path("realisateurs/<int:pk>/", views.detail_realisateur, name="detail_realisateur"),
]
