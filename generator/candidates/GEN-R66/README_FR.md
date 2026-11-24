# FREQMED GEN-R66 — Audit indépendant de séquence PCM numérique, sans émission

**Version v0.9.1 | Candidat Mac Intel | 23 novembre 2026**

## Portée de la RoadMap

Suite préparatoire **P1.01 Frequency Command Core / P1.02 Acoustic Generator (source-only)** conformément à la clause E. Les jalons normatifs restent **P0.01 IN_PROGRESS_REBASE_REVIEW**, **P0.02 PENDING**, **P1.01/P1.02 PENDING** ; aucun PASS logiciel ne les certifie. Le développement reste sous revue des fonctions Bureau B07, B08, B09, B10 ; B04 métrologie NOT_EVALUATED. Ne rien fusionner dans `main`.

## Travail nouveau, réel, sans simulation scientifique

- Nouveau module **C11 indépendant** `native/acoustic_sequence_audit_r66.c/.h`. Il ne synthétise pas le signal : il **réinspecte la mémoire numérique éphémère** produite par l'ancien moteur R65. Il refuse tout segment non contigu, tronqué, excédentaire ou de mauvaise dimension, les différences entre canaux stéréo, valeurs non finies/hors borne numérique, extrémités non nulles, remplissage résiduel après un dernier segment partiel, pic annoncé incohérent et bilan incomplet.
- Audit **stateful fail-closed** : dès qu'une incohérence est trouvée, l'état C `FAILED` demeure non utilisable. Un `PASS` n'est disponible qu'après consommation **de la totalité** des trames prévues. L'état de l'audit est explicitement effacé dans `finally`, même en cas de refus.
- Contrôle des **87 blocs** de la consigne de référence (440 Hz, 500 ms, 0,01 numérique, Mac 44 100 Hz, stéréo). Limite inchangée : **256 trames/bloc**, 512 valeurs `float32`/2 KiB. **Ni l'auditeur ni le moteur n'appellent AudioQueue ou un émetteur matériel**. Valeurs numériques = consignes, jamais niveaux acoustiques mesurés.
- Correction trouvée par un test adversarial : pour les consignes numériques extrêmement courtes (ex. 1 ms à 8 kHz), l'enveloppe R65 devait garantir des valeurs strictement nulles aux deux extrémités même avec une rampe de moins d'une trame. Le correctif C préserve la consigne historique 500 ms et l'équivalence avec R63 sur celle-ci.
- UI **existante** maintenue : un seul bouton de blocs R65, statut enrichi `audit numérique R66 vérifié` dans 10 langues. L'API renvoie seulement des nombres/états, sans données PCM, UID ou mesure instrumentale. Le client exige `sequence_audit_r66=PASS_NATIVE_DIGITAL_SAMPLES_NO_PLAYBACK` avant d'afficher une réussite.
- `PHYSICAL OUTPUT=HARD_DENIED`, `PLAYBACK=NOT_PERFORMED`, Guardian OFF au lancement, contrôle d'UID CoreAudio réel, bail R60, faute R61, route R59, STOP inchangés. Les sorties EM restent indisponibles.

## Mac Intel : vérifier puis lancer

```bash
(
 set -e
 set -o pipefail
 cd "$HOME/Downloads"
 ZIP="FREQMED_GEN_R66_SEQUENCE_AUDIT_MAC_INTEL_20261123.zip"
 SHA="${FREQMED_GEN_R66_ZIP_SHA256:?Set the SHA256 provided with the download}"
 printf '%s  %s\n' "$SHA" "$ZIP" | shasum -a 256 -c -
 unzip -oq "$ZIP"
 KIT="$HOME/Downloads/FREQMED_GEN_R66_SEQUENCE_AUDIT_MAC_INTEL_20261123"
 bash "$KIT/SYNC_R66_GITHUB_MAC_INTEL.command" 2>&1 | tee "$HOME/Downloads/FREQMED_R66_GITHUB_SYNC.log"
 FREQMED_R58_FETCH_PINNED_GITHUB=YES bash "$KIT/RUN_GEN_R66_MAC_INTEL.command" 2>&1 | tee "$HOME/Downloads/FREQMED_R66_MAC_RUN.log"
)
```

**Attendu uniquement si confirmé sur Mac :** audit R66 prêt, CoreAudio réel disponible, aucun son, aucune route associée au lancement. Sélectionner le périphérique MacBook Pro, 440/500/0,01 et associer une session native ; utiliser le **même bouton « Préparer par blocs bornés · R65 »**. Le résultat attendu comprend « audit numérique R66 vérifié » et `HARD_DENIED`. Terminer par STOP. Tout refus doit être journalisé tel quel sans répétition automatique.

## Tests et gouvernance

Les tests Linux concernent le code C et des **consignes numériques déterministes**, pas des appareils simulés ni de fausses mesures. Une qualification locale Mac Intel reste séparée ; elle ne prouve ni un effacement mémoire indépendamment instrumenté, ni une protection physique contre une émission, ni une mesure acoustique. Seule la conformité de la consigne numérique est vérifiée. Licence Apache-2.0 du cœur ; CoreAudio Apple est une dépendance propriétaire de plateforme, sans coût logiciel imposé.

**JAMAIS SIMULATION, aucune exposition biologique, aucune production, aucune émission avant décisions du Bureau et sûreté du matériel.**
