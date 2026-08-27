# 🎬 Ciné-Catalogue — API REST & backend web Django

Application de catalogue de films : deux modèles liés, une API REST complète (DRF),
une authentification JWT, et des pages HTML servies par des templates Django.

---

## 1. Installation (5 commandes)

```bash
# 1. Créer l'environnement virtuel
python -m venv .venv

# 2. L'activer
.venv\Scripts\activate        # Windows (PowerShell / CMD)
source .venv/bin/activate     # macOS / Linux

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer les tables de la base de données
python manage.py migrate

# 5. Lancer le serveur
python manage.py runserver
```

L'application est alors sur **http://127.0.0.1:8000/**

### Données de démonstration (optionnel mais recommandé)

```bash
python manage.py peupler          # 5 réalisateurs, 11 films, + un compte demo
python manage.py createsuperuser  # pour accéder à /admin/
```

Le compte créé par `peupler` : **demo / demo12345** (sert à tester l'écriture via JWT).

---

## 2. Les URLs du projet

| URL | Ce que c'est |
|---|---|
| `/` | Page HTML : catalogue des films, avec filtre par genre et recherche |
| `/films/<id>/` | Page HTML : fiche d'un film |
| `/realisateurs/<id>/` | Page HTML : fiche d'un réalisateur + sa filmographie |
| `/admin/` | Administration Django (les deux modèles y sont gérables) |
| `/api/` | Racine de l'API (interface navigable de DRF) |
| `/api/films/` | CRUD **complet** sur les films |
| `/api/realisateurs/` | Lecture + création sur les réalisateurs |
| `/api/films/statistiques/` | Route personnalisée : quelques compteurs |
| `/api/token/` | Obtention du couple de jetons JWT |
| `/api/token/refresh/` | Renouvellement du jeton d'accès |

---

## 3. Architecture des fichiers

```
Projet final/
├── manage.py                  ← le point d'entrée de toutes les commandes
├── requirements.txt
├── config/                    ← LE PROJET (configuration globale)
│   ├── settings.py            ← réglages : apps, base de données, DRF, JWT
│   └── urls.py                ← table des URLs principale, aiguille vers les sous-fichiers
└── films/                     ← L'APPLICATION (tout le métier est ici)
    ├── models.py              ← 1. les tables : Realisateur ─1──N─ Film
    ├── admin.py               ← 2. la configuration de l'interface /admin/
    ├── serializers.py         ← 3. JSON ↔ objets Python + validation métier
    ├── views.py               ← 4. les vues API (JSON) et les vues web (HTML)
    ├── urls_api.py            ← 5. le DefaultRouter qui génère les URLs de l'API
    ├── urls_web.py            ← 6. les URLs des pages HTML
    ├── jwt.py                 ← 7. la vue de connexion JWT
    ├── tests.py               ← 8. les tests automatiques
    ├── templates/films/       ← les pages HTML (base + 3 pages)
    └── management/commands/
        └── peupler.py         ← la commande `python manage.py peupler`
```

**Le trajet d'une requête API**, dans l'ordre :

```
Navigateur → config/urls.py → films/urls_api.py → films/views.py
          → films/serializers.py → films/models.py → base SQLite
          → et retour en JSON
```

**Le trajet d'une page HTML** :

```
Navigateur → config/urls.py → films/urls_web.py → films/views.py
          → films/models.py → templates/films/*.html → HTML
```

---

## 4. Le modèle de données

```
┌──────────────────────┐         ┌─────────────────────────┐
│     Realisateur      │ 1     N │          Film           │
├──────────────────────┤◄────────┤─────────────────────────┤
│ nom                  │         │ titre                   │
│ prenom               │         │ realisateur  (FK)       │
│ nationalite          │         │ annee_sortie            │
│ date_naissance       │         │ duree_minutes           │
└──────────────────────┘         │ genre (choices)         │
                                 │ synopsis / note         │
                                 └─────────────────────────┘
```

La `ForeignKey` porte `related_name="films"`, ce qui permet de remonter la relation
dans l'autre sens : `mon_realisateur.films.all()`.

---

## 5. Les règles de validation métier

Elles vivent dans `films/serializers.py` et se déclenchent à chaque POST/PUT/PATCH.

| Où | Règle |
|---|---|
| `validate_annee_sortie()` | L'année doit être entre **1895** (naissance du cinéma) et l'année courante **+ 5** |
| `validate_titre()` | Le titre est nettoyé et ne peut pas être vide |
| `validate_date_naissance()` | Une date de naissance ne peut pas être dans le futur |
| `validate()` (croisée) | **Un film ne peut pas sortir avant la naissance de son réalisateur** |

Exemple de refus renvoyé par l'API (HTTP 400) :

```json
{"annee_sortie": ["Denis Villeneuve est né(e) en 1967 : il/elle ne peut pas avoir réalisé un film en 1950."]}
```

---

## 6. Permissions

Réglées globalement dans `settings.py` (`IsAuthenticatedOrReadOnly`) et répétées
explicitement sur chaque viewset pour que ce soit lisible :

| Méthode HTTP | Anonyme | Connecté (JWT) |
|---|---|---|
| `GET` (lecture) | ✅ autorisé | ✅ autorisé |
| `POST` / `PUT` / `PATCH` / `DELETE` | ❌ 401 | ✅ autorisé |

---

## 7. Utiliser l'authentification JWT

### Étape 1 — obtenir un jeton

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d "{\"username\": \"demo\", \"password\": \"demo12345\"}"
```

Réponse :

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "access":  "eyJhbGciOiJIUzI1NiIs...",
  "utilisateur": {"id": 1, "username": "demo", "est_admin": false}
}
```

### Étape 2 — utiliser le jeton sur une requête protégée

```bash
curl -X POST http://127.0.0.1:8000/api/films/ \
     -H "Authorization: Bearer <COLLER_LE_JETON_ACCESS_ICI>" \
     -H "Content-Type: application/json" \
     -d "{\"titre\": \"Sicario\", \"realisateur\": 1, \"annee_sortie\": 2015, \"duree_minutes\": 121, \"genre\": \"ACTION\"}"
```

→ **201 Created**. Sans l'en-tête `Authorization`, la même requête renvoie **401 Unauthorized**.

### Étape 3 — renouveler le jeton d'accès quand il expire (1 h)

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
     -H "Content-Type: application/json" \
     -d "{\"refresh\": \"<LE_JETON_REFRESH>\"}"
```

---

## 8. Filtres disponibles sur l'API

```
GET /api/films/?genre=SF                 # filtrer par genre
GET /api/films/?recherche=dune           # rechercher dans le titre
GET /api/films/?page=2                   # pagination (10 par page)
```

---

## 9. Lancer les tests

```bash
python manage.py test
```

8 tests couvrent : la lecture publique, le refus d'écriture sans jeton, l'écriture
avec JWT, les deux règles de validation métier, la relation inverse, et la page HTML.

---

## 10. Correspondance avec le cahier des charges

| # | Exigence | Où c'est fait |
|---|---|---|
| 1 | Deux modèles liés par une `ForeignKey` | `films/models.py` — `Film.realisateur` |
| 2 | Admin fonctionnel sur les deux modèles | `films/admin.py` (avec un inline) |
| 3 | `ModelViewSet` + `DefaultRouter`, CRUD complet + lecture/création | `films/views.py`, `films/urls_api.py` |
| 4 | Sérialiseur avec validation métier | `films/serializers.py` — `validate_annee_sortie()` et `validate()` |
| 5 | Permissions lecture/écriture | `settings.py` + `permission_classes` des viewsets |
| 6 | Authentification JWT | `films/jwt.py`, `config/urls.py`, `SIMPLE_JWT` dans `settings.py` |
| 7 | Au moins une page HTML | `films/templates/films/` — 3 pages, zéro JavaScript |
| 8 | `README.md` | ce fichier |
