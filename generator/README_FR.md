# FREQMED GEN-R5 — Périphérique acoustique explicitement fixé

Cette étape développe le véritable code du **générateur acoustique**, sans produire de signal et sans modification du design approuvé Windows 11 × macOS.

**AUCUNE ÉMISSION PHYSIQUE.** L'exécutable GEN-R5 n'émet absolument aucun son et ne pilote aucun émetteur EM.

## Changement technique significatif

L'ancienne version R4 surveillait uniquement la sortie audio *par défaut*. Si un autre périphérique devenait la sortie par défaut entre deux vérifications, le backend préparé pouvait être ambigu. R5 ajoute, dans le **source du backend non lié**, la fixation de la queue AudioQueue à un périphérique précis, par `kAudioQueueProperty_CurrentDevice` et son identifiant CoreAudio UID. L'UID est utilisé uniquement en mémoire ; il n'est ni imprimé ni sauvegardé.

Le code vérifie ensuite par lecture de retour : même UID, nombre de canaux, fréquence d'échantillonnage nominale, et route initiale inchangée. En cas d'échec, le backend prévu détruit la queue sans démarrer.

Ces vérifications assurent une *meilleure préparation logicielle*, pas un contrôle matériel de sûreté. Elles ne garantissent ni émission réelle, ni fréquence acoustique produite, ni SPL sûr.

## Test sur Mac Intel

`bash RUN_GEN_R5_MAC_INTEL.command selftest` — compile trois composants CoreAudio comme objets séparés, sans les lier à l'exécutable, effectue des tests logiciels et un audit `nm` strict des symboles.

`bash RUN_GEN_R5_MAC_INTEL.command probe` — consulte seulement les propriétés OS de la sortie audio par défaut.

Aucune installation, aucune simulation scientifique, aucun accès microphone, aucune émission physique, aucune synchronisation automatique GitHub.

**L'état R4 réel déjà observé** : 70/70 tests sur Mac Intel, deux canaux, 44 100 Hz nominaux. Ce ne sont pas des fréquences acoustiques émises.

Logiciel Apache-2.0, avec API CoreAudio propriétaire de plateforme. B04/B05/B07/B09/B10 doivent valider les profils matériels et la sécurité avant tout futur essai de sortie. Le générateur EM reste bloqué faute de matériel qualifié.

`NEVER_SIMULATION=ENFORCED` · `ACOUSTIC_OUTPUT=NOT_AUTHORIZED` · `EM_OUTPUT=BLOCKED` · `PRODUCTION=NOT_AUTHORIZED`.
