# FREQMED GEN-R1 — Développement des générateurs physiques

**AUCUNE ÉMISSION PHYSIQUE dans cette version.** Il s'agit du premier code des moteurs acoustique et EM, pas d'une lecture CSV ni d'une simulation. Toutes les commandes de sortie sont bloquées, y compris si des drapeaux d'autorisation sont falsifiés.

Le module src/generator_core.c gère les consignes typées et les blocages du Guardian. Le backend macOS src/acoustic_macos.c contient une première implémentation AudioQueue vers du matériel audio réel, non raccordée et non qualifiée ; ce backend doit encore être compilé et revu sur Mac Intel. Le module src/em_backend.c est une interface fail-closed : il n'existe aucun pilote EM sans appareil dédié qualifié.

Commande sûre : bash RUN_GEN_R1_MAC_INTEL.command selftest (compile et teste, sans lancer ni son ni RF). Le mode status ne fait qu'imprimer le statut.

Le Bureau B04/B05/B07/B09/B10 doit examiner matériel, mesure indépendante de sortie, interverrouillages, dangers d'exposition et code avant tout banc physique non biologique. Aucun contact fabricant obligatoire.

Zéro dépendance payante. Code FREQMED Apache-2.0 ; frameworks macOS propriétaires déclarés. Dix langues UI prévues, design Windows 11 × macOS conservé.

NEVER_SIMULATION=ENFORCED ; REAL_OUTPUT=NOT_AUTHORIZED ; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED ; PRODUCTION=NOT_AUTHORIZED.
