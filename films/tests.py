"""
Quelques TESTS pour prouver que les points du cahier des charges fonctionnent.

Lancement :  python manage.py test

Django crée une base de données de test vide, exécute les tests, puis la supprime.
Aucune donnée réelle n'est touchée.
"""

from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Film, Realisateur


class BaseAPITestCase(APITestCase):
    """Classe parente : prépare les mêmes données pour tous les tests."""

    def setUp(self):
        self.utilisateur = User.objects.create_user("testeur", password="motdepasse123")
        self.realisateur = Realisateur.objects.create(
            nom="Villeneuve", prenom="Denis", date_naissance=date(1967, 10, 3)
        )
        self.film = Film.objects.create(
            titre="Arrival",
            realisateur=self.realisateur,
            annee_sortie=2016,
            duree_minutes=116,
            genre=Film.Genre.SF,
        )

    def authentifier(self):
        """Récupère un jeton JWT et le place dans l'en-tête des requêtes suivantes."""
        reponse = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testeur", "password": "motdepasse123"},
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        jeton = reponse.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {jeton}")


class TestPermissions(BaseAPITestCase):
    def test_lecture_publique(self):
        """N'importe qui peut lire la liste des films."""
        reponse = self.client.get("/api/films/")
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)

    def test_ecriture_refusee_sans_jeton(self):
        """Sans JWT, la création est refusée (401)."""
        reponse = self.client.post("/api/films/", {"titre": "X"}, format="json")
        self.assertEqual(reponse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ecriture_autorisee_avec_jeton(self):
        """Avec un JWT valide, la création passe (201)."""
        self.authentifier()
        reponse = self.client.post(
            "/api/films/",
            {
                "titre": "Dune",
                "realisateur": self.realisateur.pk,
                "annee_sortie": 2021,
                "duree_minutes": 155,
                "genre": "SF",
            },
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_201_CREATED, reponse.data)


class TestValidationMetier(BaseAPITestCase):
    def test_annee_avant_invention_du_cinema(self):
        """validate_annee_sortie refuse une année antérieure à 1895."""
        self.authentifier()
        reponse = self.client.post(
            "/api/films/",
            {
                "titre": "Film impossible",
                "realisateur": self.realisateur.pk,
                "annee_sortie": 1850,
                "duree_minutes": 90,
                "genre": "DRAME",
            },
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("annee_sortie", reponse.data)

    def test_film_avant_naissance_du_realisateur(self):
        """validate() croise deux champs : réalisateur né en 1967, film en 1950."""
        self.authentifier()
        reponse = self.client.post(
            "/api/films/",
            {
                "titre": "Film antidaté",
                "realisateur": self.realisateur.pk,
                "annee_sortie": 1950,
                "duree_minutes": 90,
                "genre": "DRAME",
            },
            format="json",
        )
        self.assertEqual(reponse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("annee_sortie", reponse.data)


class TestRelationEtPagesHTML(BaseAPITestCase):
    def test_realisateur_detail_contient_ses_films(self):
        """La ForeignKey se lit dans l'autre sens grâce à related_name='films'."""
        reponse = self.client.get(f"/api/realisateurs/{self.realisateur.pk}/")
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reponse.data["films"]), 1)
        self.assertEqual(reponse.data["films"][0]["titre"], "Arrival")

    def test_suppression_realisateur_interdite(self):
        """Le viewset réalisateur n'expose pas DELETE (405 Method Not Allowed)."""
        self.authentifier()
        reponse = self.client.delete(f"/api/realisateurs/{self.realisateur.pk}/")
        self.assertEqual(reponse.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_page_html_liste(self):
        """La page HTML affiche bien le titre du film."""
        reponse = self.client.get(reverse("films:liste_films"))
        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertContains(reponse, "Arrival")
