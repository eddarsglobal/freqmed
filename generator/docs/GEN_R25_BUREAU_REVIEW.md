# FREQMED — GEN-R25 Bureau : décisions sur synchronisation C11 et propriété CoreAudio

**Décision documentaire proposée : `REMEDIATION_PLANS_REVIEWABLE_NOT_APPLIED`.** Les neuf remédiations de GEN-R25 ne sont pas des corrections exécutées, ni des preuves formelles, ni une approbation du Bureau.

## Avis indépendant par fonction — non certifiant

**B09 — C11 : priorité P1.** Revoir le code source `src/acoustic_macos.c` et expliciter les lectures/écritures du contrôleur et de `output_callback` pour `phase`, `frames_written`, les champs PCM et le pointeur `queue`. Exiger la preuve de non-chevauchement ou un mécanisme de propriétaire unique réellement couvrant `fill_audio` sur les deux chemins. Un simple drapeau `pcm_writer_gate` dans le seul callback n'est pas une démonstration suffisante.

**B07 — Contrat CoreAudio et userdata : priorité P1.** Documenter le moment où les callbacks ne peuvent plus entrer, distinguer retour synchrone de `AudioQueueDispose(..., true)`, callbacks de sortie et listeners, et vérifier les éventuelles références qui survivent aux erreurs OS. Aucun membre de B07 n'est présumé nommé ni signataire.

**B10 — Gestion des échecs et admission : priorité P1.** Exiger un tableau de propriété pour tous les chemins `AudioQueueNewOutput`, binding, listener, stop, dispose et quarantaine. L'absence d'une preuve de libération sans UAF impose la conservation du contexte et le verrouillage du processus ; cette conservation est un confinement, pas une démonstration de sûreté en production.

## Matrice d'autorisation

| Objet | Décision GEN-R25 |
|---|---|
| Neuf propositions de remédiation | PROPOSED_NOT_APPLIED |
| Changements dans `generator/src/` | **Aucun** |
| Obligations de preuve GEN-R23 | 15 OPEN, 0 acquittée |
| Risques GEN-R24 | 7 OPEN |
| Portes du Bureau | 11 OPEN, 0 résolue |
| Vérification Apple de l'erreur `AudioQueueDispose` | NOT_TESTED |
| Preuve C11 absence de race | NOT_PROVEN |
| Garantie quiescence des callbacks | NOT_PROVEN |
| Signature / certification extérieure | NONE / PENDING |
| Émission acoustique/EM | NOT_AUTHORIZED |
| Exposition biologique / production | NOT_AUTHORIZED |

Un `PASS` logiciel ne peut **jamais** promouvoir automatiquement une ligne de ce tableau. Les propositions RM01–RM09 doivent être revues avant une phase distincte de correction native. Les neuf transitions d'une machine d'état constituent un **modèle documentaire de conception**, pas une simulation scientifique ni une validation des API macOS.

## Contrôle du candidat Mac Intel

La suite GEN-R25 doit relancer la chaîne R16–R24 avec le pin de l'archive R19 originale, vérifier les neuf propositions et leurs références, maintenir le binaire non émetteur, compiler les cinq objets candidats de manière isolée et conserver les 33 assertions natives. **Cible : 497 Python, 33 C, 133 sources intègres.** Un nouveau dossier de douze rapports JSON/Markdown R20–R25 doit être créé **après réussite réelle uniquement**. Les anciennes preuves et archives ne doivent jamais être réécrites.

La PR #1 doit rester **DRAFT**, `main` non fusionnée ; `RoadMap P0.01=IN_PROGRESS`, `BUREAU_CERTIFICATION=PENDING`, `NEVER_SIMULATION=ENFORCED`, `ZERO_COST_FOSS=ENFORCED`, `ACOUSTIC_OUTPUT=LOCKED`, `EM_OUTPUT=LOCKED`, `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`.
