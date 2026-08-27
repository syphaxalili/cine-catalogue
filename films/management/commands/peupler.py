"""
Une COMMANDE PERSONNALISÉE, appelable avec :  python manage.py peupler

Django détecte automatiquement tout fichier placé dans
`<app>/management/commands/<nom>.py` qui contient une classe `Command`.
Pratique pour remplir la base avec des données de démonstration.
"""

from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from films.models import Film, Realisateur

REALISATEURS = [
    # (prénom, nom, nationalité, date de naissance)
    ("Denis", "Villeneuve", "Canadienne", date(1967, 10, 3)),
    ("Bong", "Joon-ho", "Sud-coréenne", date(1969, 9, 14)),
    ("Céline", "Sciamma", "Française", date(1978, 11, 12)),
    ("Hayao", "Miyazaki", "Japonaise", date(1941, 1, 5)),
    ("Greta", "Gerwig", "Américaine", date(1983, 8, 4)),
]

FILMS = [
    # (titre, prénom du réalisateur, année, durée, genre, note, synopsis)
    ("Arrival", "Denis", 2016, 116, "SF", 8.0,
     "Une linguiste est recrutée par l'armée pour communiquer avec des extraterrestres."),
    ("Blade Runner 2049", "Denis", 2017, 164, "SF", 8.0,
     "Trente ans après le premier film, un blade runner découvre un secret enfoui."),
    ("Dune", "Denis", 2021, 155, "SF", 8.0,
     "Paul Atreides rejoint la planète désertique Arrakis, source de l'épice."),
    ("Parasite", "Bong", 2019, 132, "DRAME", 8.5,
     "Une famille pauvre s'infiltre méthodiquement au service d'une famille riche."),
    ("Snowpiercer", "Bong", 2013, 126, "SF", 7.1,
     "Les derniers humains survivent dans un train qui tourne autour d'une Terre gelée."),
    ("Portrait de la jeune fille en feu", "Céline", 2019, 122, "DRAME", 8.1,
     "Une peintre doit réaliser en secret le portrait de mariage d'une jeune femme."),
    ("Petite Maman", "Céline", 2021, 72, "DRAME", 7.3,
     "Après la mort de sa grand-mère, une fillette rencontre une enfant de son âge."),
    ("Le Voyage de Chihiro", "Hayao", 2001, 125, "ANIMATION", 8.6,
     "Une fillette se retrouve prisonnière d'un monde peuplé d'esprits."),
    ("Princesse Mononoké", "Hayao", 1997, 134, "ANIMATION", 8.3,
     "Un jeune prince tente de rétablir la paix entre les hommes et la forêt."),
    ("Lady Bird", "Greta", 2017, 94, "COMEDIE", 7.4,
     "La dernière année de lycée d'une adolescente à Sacramento."),
    ("Barbie", "Greta", 2023, 114, "COMEDIE", 6.8,
     "Barbie quitte Barbie Land pour découvrir le monde réel."),
]


class Command(BaseCommand):
    # Texte affiché par `python manage.py help peupler`
    help = "Remplit la base avec un jeu de films de démonstration."

    def add_arguments(self, parser):
        """Options en ligne de commande : python manage.py peupler --reset"""
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime les films et réalisateurs existants avant d'insérer.",
        )

    def handle(self, *args, **options):
        """Le code réellement exécuté par la commande."""
        if options["reset"]:
            Film.objects.all().delete()
            Realisateur.objects.all().delete()
            self.stdout.write("Base vidée.")

        realisateurs = {}
        for prenom, nom, nationalite, naissance in REALISATEURS:
            # get_or_create = « récupère s'il existe, sinon crée » : la commande
            # peut être relancée plusieurs fois sans créer de doublons.
            objet, cree = Realisateur.objects.get_or_create(
                nom=nom,
                prenom=prenom,
                defaults={"nationalite": nationalite, "date_naissance": naissance},
            )
            realisateurs[prenom] = objet
            if cree:
                self.stdout.write(f"  + réalisateur : {objet}")

        for titre, prenom, annee, duree, genre, note, synopsis in FILMS:
            film, cree = Film.objects.get_or_create(
                titre=titre,
                realisateur=realisateurs[prenom],
                defaults={
                    "annee_sortie": annee,
                    "duree_minutes": duree,
                    "genre": genre,
                    "note": note,
                    "synopsis": synopsis,
                },
            )
            if cree:
                self.stdout.write(f"  + film : {film}")

        # Un compte de démonstration pour tester l'écriture via JWT.
        if not User.objects.filter(username="demo").exists():
            User.objects.create_user("demo", password="demo12345")
            self.stdout.write("  + utilisateur : demo / demo12345")

        self.stdout.write(
            self.style.SUCCESS(
                f"OK — {Realisateur.objects.count()} réalisateurs, {Film.objects.count()} films."
            )
        )
