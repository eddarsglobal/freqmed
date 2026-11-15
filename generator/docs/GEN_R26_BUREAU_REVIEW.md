# FREQMED GEN-R26 — Bureau indépendant C11, propriété du contexte et verrou d'émission

**Verdict autorisable pour le seul jalon logiciel : `ISOLATED_PATCH_REVIEW_REQUIRED_NO_EMISSION`.**

### Périmètre confié aux fonctions du Bureau

**B09 :** comparer les trois éditions C réelles à la source originale R19 et à GEN-R25. Vérifier le drapeau PCM partagé entre préremplissage contrôleur et callback ; recenser les autres chemins susceptibles de modifier `phase`, `frames_written`, `queue` et les buffers AudioQueue. L'opération atomique ne garantit pas seule l'absence de callback tardif, de data race ou de blocage sur le thread temps réel. Exiger une preuve d'accès/exclusion complète avant toute promotion.

**B07 :** confronter la durée de vie userdata et des listeners aux documents macOS. Une libération synchrone réussie `AudioQueueDispose(..., true)` peut apporter un contrat pour le chemin de succès, mais pas une qualification des échecs `OSStatus`. GEN-R26 retient le tas publié pour empêcher un `free` hasardeux ; cela **ne prouve ni la quiescence de l'OS ni la maîtrise des ressources à long terme**. Aucune activation CoreAudio n'est permise.

**B10 :** maintenir les sorties et l'admission fermées, interdire toute liaison de `candidates/acoustic_macos_r26.c` dans le programme, contrôler `nm`, l'absence d'émission et la conservation des preuves historiques en lecture seule. La source candidate doit rester isolée ; les rôles B07/B09/B10 ne correspondent pas à des personnes ou signatures indépendantes automatiquement obtenues.

### Critères GEN-R26 de non-régression et de clôture documentaire

La seule réussite possible pour ce jalon est l'intégrité des 139 sources, la vérification octet-à-octet des **trois modifications permises**, la compilation C candidate **uniquement en objet non lié**, 20 nouveaux tests Python statiques, 33 assertions C historiques et la création de 14 rapports JSON/Markdown R20–R26 contrôlés SHA-256 après succès des tests. Cela doit conserver la PR #1 **DRAFT**, `main` intacte et la source historique inchangée.

Aucun test n'exécute de callback CoreAudio ou de nouvelle fonctionnalité sonore/électromagnétique, aucune simulation scientifique ou mesure n'est présentée. Le code isolé peut encore comporter d'autres défauts. Ce jalon ne certifie ni race freedom C11, ni quiescence, ni erreur de dispose, ni sécurité matérielle, ni efficacité médicale.

### État de sortie maximal

`R26_CANDIDATE_C_EDITS=3`; `R26_ORIGINAL_C_EDITS=0`; `R26_ISOLATED_CANDIDATE_OBJECT=COMPILED_UNLINKED` (après exécution Mac réelle uniquement) ; **15 obligations R23 OPEN**, **7 constats R24 OPEN**, **11 portes Bureau OPEN**, 0 acquittée, 0 autorisation de sortie, `RoadMap P0.01=IN_PROGRESS`, `BUREAU_CERTIFICATION=PENDING`.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
