# **Projet de groupe : Énoncé**

## **Consigne générale**

L'objectif de ce projet personnel est d'appliquer les compétences clés du développement d'une API REST et d'un backend web en construisant une application complète de catalogue de films.

## **Cahier des charges technique**

Ce socle reprend exactement les compétences vues du lundi au mercredi :

1. **Au moins deux modèles Django liés** par une relation (`ForeignKey` au minimum).
2. **Admin Django** fonctionnel sur les deux modèles.
3. **API REST via DRF** : au minimum un `ModelViewSet` + `DefaultRouter` avec CRUD complet sur une ressource, lecture + création au minimum sur la seconde.
4. **Un sérialiseur avec validation métier** (`validate_<champ>` ou `validate()`) : une règle qui a du sens pour votre domaine.
5. **Permissions** : lecture publique ou authentifiée (à votre choix), écriture réservée aux utilisateurs authentifiés (`IsAuthenticatedOrReadOnly` ou équivalent).
6. **Authentification JWT** fonctionnelle (obtention du jeton, utilisation sur une requête protégée).
7. **Au moins une page HTML** (template Django classique) qui affiche des données de votre modèle, pas de framework frontend requis.
8. **Un `README.md`** expliquant comment lancer le projet (setup, migrations, lancement du serveur).

## **Ce qui n'est PAS demandé**

- Pas de frontend JavaScript.
- Pas de déploiement en production.
- Pas de tests automatisés exhaustifs exigés (les tests sont bienvenus, mais ce n'est pas un critère de notation en soi).
- Pas besoin de notions avancées (pagination avancée, WebSockets, tâches asynchrones...).