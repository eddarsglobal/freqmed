# FREQMED GEN-R3 — Compilabilité native du générateur acoustique
**AUCUNE ÉMISSION PHYSIQUE** dans cette version. Mission : générer ultérieurement des fréquences réelles acoustiques et électromagnétiques par matériel adapté; Bureau chargé de la science et des certifications.
R2 FIX1 : 30/30 tests PASS sur Mac Intel; CoreAudio a déclaré 2 canaux et 44 100 Hz nominaux, sans sortie.
R3 : source AudioQueue adapté au taux d'échantillonnage nominal constaté et compilé comme objet isolé non exécutable. Aucun lien avec l'exécutable de contrôle. Le module EM reste bloqué.
Commande Mac Intel : `bash RUN_GEN_R3_MAC_INTEL.command selftest` puis `bash RUN_GEN_R3_MAC_INTEL.command probe`.
Aucun pilote, son, émetteur, microphone ni installation de bibliothèque. La vérification ne certifie pas le transducteur physique. Design Windows 11 × macOS inchangé. Apache-2.0 pour le code, frameworks macOS propriétaires déclarés.
NEVER_SIMULATION=ENFORCED; OUTPUT=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.
