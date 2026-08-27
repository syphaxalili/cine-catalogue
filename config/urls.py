"""
Le routeur PRINCIPAL du projet : c'est la première chose que Django lit
quand une requête arrive. Il distribue ensuite vers les sous-fichiers d'URLs.

    /                     -> pages HTML          (films/urls_web.py)
    /admin/               -> administration Django
    /api/                 -> API REST            (films/urls_api.py)
    /api/token/           -> obtention du jeton JWT
    /api/token/refresh/   -> rafraîchissement du jeton
    /api-auth/            -> connexion/déconnexion de l'interface navigable de DRF
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from films.jwt import ConnexionJWTView

urlpatterns = [
    path("admin/", admin.site.urls),
    # --- API REST ---
    path("api/", include("films.urls_api")),
    # --- Authentification JWT ---
    # POST {"username": "...", "password": "..."} -> {"access": "...", "refresh": "..."}
    path("api/token/", ConnexionJWTView.as_view(), name="token_obtain_pair"),
    # POST {"refresh": "..."} -> un nouveau jeton d'accès sans redonner son mot de passe
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Boutons « Log in / Log out » de l'interface navigable de DRF (session, pas JWT).
    path("api-auth/", include("rest_framework.urls")),
    # --- Pages HTML (en dernier car "" attrape la racine) ---
    path("", include("films.urls_web")),
]
