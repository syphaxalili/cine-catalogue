"""
Les SÉRIALISEURS (DRF) : le traducteur entre les objets Python et le JSON.

    Objet Film  --- serializer ---> dict/JSON   (lecture : GET)
    JSON reçu   --- serializer ---> Objet Film  (écriture : POST/PUT, avec validation)

L'ordre de validation exécuté par DRF quand on appelle `serializer.is_valid()` :
    1. validation de type / champ par champ (max_length, entier, etc.)
    2. `validate_<nom_du_champ>(self, value)`  -> règle sur UN champ
    3. `validate(self, attrs)`                -> règle qui a besoin de PLUSIEURS champs
"""

from datetime import date

from rest_framework import serializers

from .models import Film, Realisateur

# Le premier film projeté publiquement : les frères Lumière, 1895.
PREMIERE_ANNEE_DU_CINEMA = 1895


class FilmSerializer(serializers.ModelSerializer):
    """Sérialiseur principal, avec les règles métier du projet."""

    # Champs "en lecture seule" : calculés côté serveur, jamais envoyés par le client.
    # source="..." dit à DRF où aller chercher la valeur sur l'objet.
    realisateur_nom = serializers.CharField(source="realisateur.__str__", read_only=True)
    genre_libelle = serializers.CharField(source="get_genre_display", read_only=True)
    duree_lisible = serializers.CharField(read_only=True)

    class Meta:
        model = Film
        fields = [
            "id",
            "titre",
            "realisateur",       # en écriture : on envoie l'id du réalisateur
            "realisateur_nom",   # en lecture : on récupère son nom complet
            "annee_sortie",
            "duree_minutes",
            "duree_lisible",
            "genre",
            "genre_libelle",
            "synopsis",
            "note",
            "date_ajout",
        ]
        read_only_fields = ["id", "date_ajout"]

    # ------------------------------------------------------------------
    # RÈGLE 1 — validation d'un seul champ : validate_<champ>
    # ------------------------------------------------------------------
    def validate_annee_sortie(self, value):
        """Un film ne peut pas être sorti avant l'invention du cinéma,
        ni plus de 5 ans dans le futur (les annonces trop lointaines n'ont pas de sens).
        """
        annee_max = date.today().year + 5
        if value < PREMIERE_ANNEE_DU_CINEMA:
            raise serializers.ValidationError(
                f"Le cinéma est né en {PREMIERE_ANNEE_DU_CINEMA} : "
                f"aucun film ne peut être sorti en {value}."
            )
        if value > annee_max:
            raise serializers.ValidationError(
                f"Année trop lointaine : on n'accepte pas au-delà de {annee_max}."
            )
        return value  # ⚠️ toujours renvoyer la valeur validée

    def validate_titre(self, value):
        """Nettoyage + refus d'un titre vide composé uniquement d'espaces."""
        titre = value.strip()
        if not titre:
            raise serializers.ValidationError("Le titre ne peut pas être vide.")
        return titre

    # ------------------------------------------------------------------
    # RÈGLE 2 — validation croisée : on a besoin de 2 champs à la fois
    # ------------------------------------------------------------------
    def validate(self, attrs):
        """Un film ne peut pas sortir avant la naissance de son réalisateur.

        Subtilité : en PUT partiel (PATCH), le client n'envoie pas forcément
        les deux champs. On retombe alors sur les valeurs déjà en base
        via `self.instance` (qui vaut None lors d'une création).
        """
        realisateur = attrs.get("realisateur") or getattr(self.instance, "realisateur", None)
        annee = attrs.get("annee_sortie") or getattr(self.instance, "annee_sortie", None)

        if realisateur and annee and realisateur.date_naissance:
            annee_naissance = realisateur.date_naissance.year
            if annee < annee_naissance:
                raise serializers.ValidationError(
                    {
                        "annee_sortie": (
                            f"{realisateur} est né(e) en {annee_naissance} : "
                            f"il/elle ne peut pas avoir réalisé un film en {annee}."
                        )
                    }
                )
        return attrs


class RealisateurSerializer(serializers.ModelSerializer):
    """Sérialiseur « liste » : léger, on ne renvoie pas tous les films."""

    nom_complet = serializers.CharField(source="__str__", read_only=True)
    nombre_de_films = serializers.IntegerField(read_only=True)

    class Meta:
        model = Realisateur
        fields = [
            "id",
            "nom",
            "prenom",
            "nom_complet",
            "nationalite",
            "date_naissance",
            "nombre_de_films",
        ]

    def validate_date_naissance(self, value):
        """Règle métier simple : on n'accepte pas une date de naissance future."""
        if value and value > date.today():
            raise serializers.ValidationError("La date de naissance ne peut pas être dans le futur.")
        return value


class RealisateurDetailSerializer(RealisateurSerializer):
    """Sérialiseur « détail » : le même, plus la liste imbriquée de ses films.

    C'est l'intérêt du `related_name="films"` : DRF sait le suivre tout seul.
    """

    films = FilmSerializer(many=True, read_only=True)

    class Meta(RealisateurSerializer.Meta):
        fields = RealisateurSerializer.Meta.fields + ["films"]
