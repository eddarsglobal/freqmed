# FREQMED GEN-R2 FIX1 — Rapport de remédiation SDK CoreAudio

- Incident: compilation de la version R2 échouée sur Mac Intel, 3 diagnostics `-Werror,-Wdeprecated-declarations` (lignes 19, 29, 39)
- Preuve: journal fourni par le propriétaire le 12 novembre 2026 (R2 ZIP et manifeste PASS, build FAIL)
- Cause: `kAudioObjectPropertyElementMaster` déprécié dès SDK macOS 12; le SDK indique `kAudioObjectPropertyElementMain` comme remplacement.
- Correctif: changement de la constante sur les 3 adresses CoreAudio ; signatures, scopes et lecture des propriétés inchangés. Pas de suppression de `-Werror`.
- Autotest supplémentaire: code source doit contenir exactement 3 occurrences `kAudioObjectPropertyElementMain` et zéro ancienne constante.
- Contrôle sécurité: `acoustic_macos.c` reste hors compilation de l'exécutable R2; seul le stub `output_hard_denied.c` est lié. Vérification par `nm` native avec blocage si indisponible. Le module EM refuse toute sortie.
- Limites: les tests multiplateformes peuvent vérifier la structure du code mais **pas** la compilation CoreAudio avec le SDK du Mac, ni le matériel. Le test Mac Intel doit être exécuté.
- Verdict provisoire: FIX1_PATCHED_READY_FOR_MAC_RETEST; REAL_OUTPUT=NONE; PRODUCTION=NOT_AUTHORIZED.
