"""
Les VUES : le code qui répond à une requête HTTP.

Ce fichier contient deux mondes bien distincts, ne pas les confondre :

  1. Les vues API (DRF)      -> renvoient du JSON            -> section « API REST »
  2. Les vues web (Django)   -> renvoient une page HTML       -> section « PAGES HTML »
"""

from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Film, Realisateur
from .serializers import FilmSerializer, RealisateurDetailSerializer, RealisateurSerializer

# ======================================================================
# 1. API REST (Django REST Framework)
# ======================================================================


class FilmViewSet(viewsets.ModelViewSet):
    """CRUD **complet** sur les films.

    Un ModelViewSet fournit d'un coup les 5 actions, que le routeur
    transformera en URLs :

        list      GET    /api/films/       -> lister
        create    POST   /api/films/       -> créer
        retrieve  GET    /api/films/3/     -> lire un film
        update    PUT    /api/films/3/     -> remplacer (PATCH = modifier partiellement)
        destroy   DELETE /api/films/3/     -> supprimer
    """

    queryset = Film.objects.select_related("realisateur")
    serializer_class = FilmSerializer
    # Lecture ouverte à tous, écriture réservée aux utilisateurs authentifiés (JWT).
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filtres simples passés en paramètres d'URL.

        Exemples : /api/films/?genre=SF  ou  /api/films/?recherche=matrix
        """
        queryset = super().get_queryset()

        genre = self.request.query_params.get("genre")
        if genre:
            queryset = queryset.filter(genre=genre.upper())

        recherche = self.request.query_params.get("recherche")
        if recherche:
            queryset = queryset.filter(titre__icontains=recherche)

        return queryset

    @action(detail=False, methods=["get"])
    def statistiques(self, request):
        """Route « bonus » ajoutée au viewset : GET /api/films/statistiques/

        `detail=False` = la route porte sur la collection, pas sur un objet précis.
        """
        return Response(
            {
                "nombre_de_films": Film.objects.count(),
                "nombre_de_realisateurs": Realisateur.objects.count(),
                "par_genre": list(
                    Film.objects.values("genre").annotate(total=Count("id")).order_by("-total")
                ),
            }
        )


class RealisateurViewSet(
    mixins.ListModelMixin,      # GET  /api/realisateurs/
    mixins.RetrieveModelMixin,  # GET  /api/realisateurs/3/
    mixins.CreateModelMixin,    # POST /api/realisateurs/
    viewsets.GenericViewSet,
):
    """Lecture + création seulement (pas de modification ni de suppression).

    On assemble ici les briques une par une (les « mixins ») au lieu de prendre
    le ModelViewSet complet : c'est exactement ce qu'il y a *dans* un ModelViewSet.
    """

    queryset = Realisateur.objects.prefetch_related("films")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Sérialiseur différent selon l'action : la fiche détaillée embarque les films."""
        if self.action == "retrieve":
            return RealisateurDetailSerializer
        return RealisateurSerializer


# ======================================================================
# 2. PAGES HTML (templates Django classiques, aucun JavaScript)
# ======================================================================


def liste_films(request):
    """Page d'accueil : le catalogue. URL -> /"""
    films = Film.objects.select_related("realisateur").all()

    # Le formulaire de la page envoie ?genre=SF&recherche=... en GET.
    genre_choisi = request.GET.get("genre", "")
    recherche = request.GET.get("recherche", "").strip()

    if genre_choisi:
        films = films.filter(genre=genre_choisi)
    if recherche:
        films = films.filter(titre__icontains=recherche)

    contexte = {
        "films": films,
        "genres": Film.Genre.choices,
        "genre_choisi": genre_choisi,
        "recherche": recherche,
        "total": films.count(),
    }
    # render(requête, chemin du template, dictionnaire de données)
    return render(request, "films/liste_films.html", contexte)


def detail_film(request, pk):
    """Fiche d'un film. URL -> /films/3/"""
    film = get_object_or_404(Film.objects.select_related("realisateur"), pk=pk)
    contexte = {
        "film": film,
        # Les autres films du même réalisateur, en excluant celui affiché.
        "autres_films": film.realisateur.films.exclude(pk=film.pk),
    }
    return render(request, "films/detail_film.html", contexte)


def detail_realisateur(request, pk):
    """Fiche d'un réalisateur et sa filmographie. URL -> /realisateurs/3/"""
    realisateur = get_object_or_404(Realisateur, pk=pk)
    return render(
        request,
        "films/detail_realisateur.html",
        {"realisateur": realisateur, "films": realisateur.films.all()},
    )
