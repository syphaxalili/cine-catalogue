"""
L'AUTHENTIFICATION JWT (JSON Web Token), fournie par `djangorestframework-simplejwt`.

Rappel du principe, sans magie :

  1. Le client envoie une fois son login/mot de passe sur /api/token/.
  2. Le serveur lui renvoie deux jetons signés : `access` (courte durée)
     et `refresh` (longue durée).
  3. Pour chaque requête protégée, le client met le jeton d'accès dans l'en-tête :
         Authorization: Bearer <jeton_access>
  4. Le serveur vérifie la signature du jeton. Aucune session n'est stockée
     côté serveur : c'est ce qu'on appelle une authentification « stateless ».

La classe ci-dessous n'est PAS obligatoire : `TokenObtainPairView` de simplejwt
suffirait. On la personnalise juste pour renvoyer aussi le nom de l'utilisateur,
ce qui évite un aller-retour supplémentaire côté client.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class ConnexionJWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # `super().validate()` vérifie le mot de passe et fabrique les deux jetons.
        donnees = super().validate(attrs)
        # On enrichit la réponse (pas le jeton lui-même) avec quelques infos utiles.
        donnees["utilisateur"] = {
            "id": self.user.id,
            "username": self.user.username,
            "est_admin": self.user.is_staff,
        }
        return donnees


class ConnexionJWTView(TokenObtainPairView):
    serializer_class = ConnexionJWTSerializer
