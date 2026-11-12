# FREQMED GEN-R2 — Couche matérielle acoustique en lecture seule

**AUCUNE ÉMISSION PHYSIQUE n’est possible avec l’exécutable GEN-R2.**

**R1 a compilé et réussi 13/13 tests sur le Mac Intel du propriétaire. R2 est candidat.**

Cette version progresse vers la génération physique sans émission prématurée : elle interroge réellement la sortie audio par défaut via **CoreAudio en lecture seule**, relève son nombre de canaux de sortie et sa fréquence nominale d'échantillonnage. L'information **n'est pas une mesure de pression acoustique ni une qualification**. Une sortie système peut être virtuelle ou non reliée à un transducteur.

## Architecture

- `src/generator_core.c` : commandes acoustiques/EM et Guardian durci OFF/BLOCK.
- `src/acoustic_probe_macos.c` : vérification matérielle **réelle**, API CoreAudio `AudioObjectGetPropertyData` uniquement ; aucun accès microphone, aucune sortie.
- `src/acoustic_macos.c` : code source d'un backend physique AudioQueue **non lié** et non autorisé, conservé pour revue ultérieure.
- `src/output_hard_denied.c` : seule implémentation du symbole public de sortie acoustique liée au binaire ; retourne toujours `-1`.
- `src/em_backend.c` : le pilote électromagnétique demeure BLOCKED sans instrument dédié qualifié.
- `RUN_GEN_R2_MAC_INTEL.command` : build Mac Intel, vérification des symboles natifs interdits, tests, état, sonde de sortie réelle.

## Commandes

`bash RUN_GEN_R2_MAC_INTEL.command selftest` : compile et vérifie le code, sans émission.

`bash RUN_GEN_R2_MAC_INTEL.command probe` : consulte l'interface audio **en lecture seule** puis affiche ses propriétés techniques non sensibles. Aucun UID, numéro de série ou marque.

`bash RUN_GEN_R2_MAC_INTEL.command status` : état de verrouillage.

Le probe ne certifie **ni le transducteur ni l'étalonnage**. Aucun contact fabricant obligatoire. Le design UI V5 Windows 11 × macOS reste gelé. Aucun nouveau CSV ni faux signal.

**NEVER_SIMULATION=ENFORCED ; REAL_OUTPUT=NOT_AUTHORIZED ; ACOUSTIC_EMISSION=NONE ; EM_EMISSION=NONE ; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED ; PRODUCTION=NOT_AUTHORIZED.**
