# GEN-PLATFORM-07 — Native Acoustic Output Readiness Engine
Candidat isolé de préparation P1.01/P1.02 sous clause E. P0.01 IN_PROGRESS_REBASE_REVIEW ; P0.02, P0.04, P1.02 et P1.03 PENDING. Aucun changement de main ou RoadMap.md.

## Collecte native
CoreAudio, lecture seule du périphérique de sortie par défaut. Identité UID locale non exportée, transport déclaré, nombre de canaux de sortie, fréquence nominale, plages de fréquences d'échantillonnage nominales déclarées, disponibilité, DeviceIsRunningSomewhere, taille actuelle du buffer et plage de tailles déclarée. Aucun AudioUnit, AudioQueue, flux ou changement de propriété. Les lectures de taille variable sont bornées et vérifient les octets effectivement retournés. Une propriété indisponible reste inconnue. L'état d'activité décrit une observation OS, pas la garantie que la sortie restera libre.

Le moteur C11 compare deux captures successives et exige un candidat par défaut intégré ou USB selon la politique existante, des métadonnées cohérentes, un périphérique déclaré disponible et non actif. Les taux nominaux ne sont ni des fréquences acoustiques ni des garanties de bande passante physique. Les plages sont celles déclarées par l'OS, pas des formats testés ni une mesure de latence. Une plage peut contenir des valeurs dont la prise en charge effective reste inconnue. Un changement de l'ordre des plages est traité conservativement comme modification. Les captures ne sont pas atomiques ; pas de surveillance continue dans cette étape. PASS_READONLY_METADATA est un verdict de cohérence de métadonnées uniquement. Aucun raccordement à une sortie active et aucune nouvelle autorité.

## Qualification
28 blobs historiques épinglés, 262 assertions prévues (227 régressions et 35 nouvelles assertions de préparation). Vecteurs C uniquement logiciels. Qualification macOS par deux captures réelles, sans répéter la fenêtre passive de PLATFORM-06. La preuve événementielle native demeure PENDING_NOT_REPLAYED. Les adaptateurs natifs Windows/Linux de cette étape ne sont pas implémentés ; le cœur C11 est portable. Python3, Git, C11 et frameworks système ; aucune installation automatique.

## Prérequis du banc physique
Arrêt indépendant NOT_VERIFIED ; limites physiques NOT_MEASURED ; mesure indépendante NOT_AVAILABLE_IN_THIS_TEST ; autorisation NONE. Ces champs sont des constats de non-validation, pas des contrôles matériels implémentés. physical_ready=false et hardware_qualified=false, même si les métadonnées sont cohérentes. Le backend d'émission et l'arrêt physique indépendant ne font pas partie de cette révision. Aucune émission, simulation physique, exposition ou mesure.

## Bureau
Revue B04/B07/B09/B10 proposée. Certification indépendante non délivrée. Cœur FOSS, aucun coût logiciel ni dépendance cloud ajoutée. Aucune promotion de jalon.
