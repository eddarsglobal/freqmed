# GEN-PLATFORM-03 — Native Hardware Binding Engine
Candidat préparatoire isolé clause E, P1.01/P1.02/P2.01, sans promotion de jalon. Branché sur GEN-PLATFORM-02. Aucun changement de main ou RoadMap.md.

## Réalisation
Réutilise réellement GEN-INTEGRATION-01 et 02 en C11. Sélection automatique du seul endpoint audio par défaut déclaré BUILT_IN ou USB, avec UID natif non vide, unique et métadonnées cohérentes. Aucun fallback automatique vers une autre sortie. Les autres transports, notamment VIRTUAL, ne sont pas candidats à cette sélection. Le choix est une politique logicielle conservatrice proposée, pas une preuve de présence d'un transducteur ni d'adéquation physique.

Le collecteur Mac réutilise CoreAudio, interroge l'UID natif et le transport, vérifie le défaut avant/après capture, puis compare deux observations. L'UID reste dans la mémoire locale, jamais dans le rapport. L'UID OS n'est pas une attestation cryptographique, une identité matérielle infaillible ni un identifiant persistant FREQMED. La collecte historique peut omettre des sorties non lisibles. Aucune atomicité de snapshot garantie.

Le moteur crée une session PREPARED (validation structurelle uniquement), réévalue identité/format/transport/défaut sur chaque refresh explicite, annule la préparation sur changement ou lecture invalide et ferme explicitement la session. La permutation de l'ordre d'énumération n'est pas un changement d'identité. Il n'y a ni thread de surveillance, ni détection continue, ni arrêt physique. Appelant sérialisé, entrées stables, sorties distinctes sans alias, initialisation unique par cycle de vie, état interne non muté par l'appelant. Pas d'IPC ou de stockage persistant.

Le cœur portable est prévu pour macOS/Linux/Windows. L'adaptateur d'identité native n'est implémenté que sur macOS. Linux/Windows sont explicitement ADAPTER_NOT_IMPLEMENTED, et l'association EM est NOT_AVAILABLE : VID/PID ou compte USBTMC ne suffisent pas à sélectionner un instrument. Aucun accès RF ou port.

## Vérification
115 assertions prévues : 70 régressions intégration et horloge, 45 liaison. Vecteurs logiciels artificiels seulement, aucune simulation physique. 16 blobs historiques épinglés. Le test natif macOS utilise deux captures CoreAudio réelles et une consigne de test structurelle jamais émise. STABLE_AT_REFRESH décrit seulement ces observations, pas une garantie continue. PASS_SOFTWARE_ONLY ne signifie pas que le test natif a trouvé un candidat. Python3, Git, C11 (Windows GCC/Clang compatible). Aucun téléchargement/install automatique. Résultats non confirmés avant exécution.

## Bureau
Revue proposée B04/B05/B07/B09/B10. Aucune certification indépendante, aucune mesure physique, aucun pilote d'émission ni autorisation. P0.01 en cours ; P0.02 en attente. Zéro coût logiciel, cœur libre, pas de simulation physique.