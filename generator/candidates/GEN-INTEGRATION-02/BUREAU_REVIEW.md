# GEN-INTEGRATION-02 — Unified Generator Session Engine
Candidat préparatoire de la clause E, sans promotion de jalon. Le propriétaire a demandé le 24 novembre 2026 d'exploiter les OS disponibles (Windows, Linux, macOS) pour les futurs sous-systèmes physiques. Cette orientation est consignée ici comme exigence d'architecture proposée pour P5.02, sans modifier RoadMap.md ni les gates.

## Développement
Deux slots indépendants, un par canal. PREPARED signifie seulement que la forme de la requête est validée ; aucun état ACTIVE. Échéance logicielle, annulation, expiration, fermeture explicite, génération monotone des identifiants par canal, rejet des anciens identifiants, débordement contrôlé, détection du recul de l'horloge. Une erreur d'un canal ne modifie pas l'autre. Aucun stockage de commandes physiques ni pilote. L'API suppose un appelant sérialisé, des entrées stables, un token distinct des objets d'entrée et une initialisation unique par cycle de vie ; les tokens ne sont pas des autorisations de sécurité ni persistants.

Horloge native : GetTickCount64 sous Windows ; clock_gettime(CLOCK_MONOTONIC) sous Linux/macOS. Aucun thread autonome, aucun watchdog matériel : expiration à chaque tick explicite, pas un arrêt physique. L'adaptateur retourne un échec si l'horloge n'est pas lisible ; l'appelant ne doit pas substituer l'heure civile.

## Orientation des backends physiques (futur)
Cœur C11 partagé. Mac : CoreAudio pour l'acoustique ; Linux : ALSA ; Windows : WASAPI. EM : interfaces natives de découverte et transport seulement pour un instrument compatible identifié, pilote et protocole spécifiques. Les API système ne créent pas de capacité matérielle absente et ne constituent pas une qualification. Aucun accès radio intégré arbitraire ni émission dans ce candidat. Aucun SDK payant, aucune simulation, aucune revendication thérapeutique. Les API propriétaires de plateforme sont signalées, le cœur demeure libre.

## Qualification
Python 3, Git, compilateur C11 à interface GCC/Clang (Windows : environnement MinGW-w64 ou Clang compatible, non MSVC). Aucune installation automatique. Les trois commits historiques doivent être disponibles localement. 8 blobs Git épinglés ; 23 assertions de régression, 38 sessions, 9 horloge native. Les valeurs de test sont des vecteurs logiciels, non des mesures ou périphériques fictifs. Résultats par OS à établir séparément ; aucun PASS anticipé.

Revue technique proposée B04/B05/B07/B09/B10. Aucune certification indépendante ni autorisation physique. P0.01 reste en cours et P0.02 en attente. PR empilée sur GEN-INTEGRATION-01, main inchangée.
