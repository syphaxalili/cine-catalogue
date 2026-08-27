"""
Les URLs de l'API, générées par le DefaultRouter de DRF.

Le routeur regarde le viewset qu'on lui donne et fabrique automatiquement
toutes les URLs correspondantes. On n'écrit donc aucun path() à la main.

    router.register("films", FilmViewSet) produit :
        /api/films/          -> GET (list), POST (create)
        /api/films/<id>/     -> GET (retrieve), PUT/PATCH (update), DELETE (destroy)
        /api/films/statistiques/  -> notre @action personnalisée

Le DefaultRouter ajoute en plus une racine /api/ qui liste les ressources.
"""

from rest_framework.routers import DefaultRouter

from .views import FilmViewSet, RealisateurViewSet

router = DefaultRouter()
router.register("films", FilmViewSet, basename="film")
router.register("realisateurs", RealisateurViewSet, basename="realisateur")

urlpatterns = router.urls
