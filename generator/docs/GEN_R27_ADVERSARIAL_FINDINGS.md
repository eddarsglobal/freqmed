# FREQMED — GEN-R27 Independent Native C11 Patch Adversarial & Ownership Review

**Périmètre strict : source C native isolée, aucune exécution CoreAudio ni simulation scientifique.** Le témoin réel GEN-R26 du 15 novembre 2026 sur Mac Intel établit **517/517 Python PASS**, **33/33 assertions C PASS**, **139/139 fichiers épinglés vérifiés**, et **14 rapports JSON/Markdown R20–R26 vérifiés SHA-256**. Le candidat `candidates/acoustic_macos_r26.c` a été compilé en objet natif mais jamais lié/chargé. Le C historique `src/acoustic_macos.c` demeure inchangé.

GEN-R27 examine adversarialement **les trois modifications C concrètes** de ce candidat (verrou d'écriture PCM partagé, quarantaine de la liaison, conservation du contexte après publication). Le nouvel auditeur `audits/r27_adversarial_ownership_review.py` revalide d'abord octet pour octet cette révision à partir du C original R19 épinglé ; il impose ensuite une série d'observations indépendantes par fonctions, ancrées dans les véritables lignes C et SHA-256 de la source.

## Neuf constats adversariaux — ouverts, non démontrés comme races

| ID | Priorité | Fait source vérifié | Preuve indépendante nécessaire |
|---|---|---|---|
| AD01 — Verrou commun sans preuve globale | P1 | `pcm_writer_gate` est acquis dans le contrôleur et le callback, tous deux appelant `fill_audio` | Recenser toutes les lectures/écritures PCM et établir les vrais liens *happens-before* |
| AD02 — Appel OS dans section PCM | P1 | `fill_audio` appelle `AudioQueueEnqueueBuffer`, y compris depuis la zone protégée par le drapeau | Démontrer l'absence de réentrance dangereuse, les limites de latence et la gestion d'une contention sans blocage du callback |
| AD03 — Pointeur de file non atomique | P1 | `fill_audio` lit `ctx->queue`; le contrôleur affecte `ctx->queue=NULL` après `AudioQueueDispose`, sans acquisition du drapeau PCM sur le chemin final | Prouver l'impossibilité d'accès concurrents et la quiescence du callback avant invalidation du pointeur |
| AD04 — Listener avant comptabilisation | P1 | Le listener récupère `ctx` avant d'incrémenter `active_property_listeners` | Prouver la barrière empêchant toute nouvelle entrée de listener après désinscription et disposition |
| AD05 — Callback avant comptabilisation | P1 | Le callback récupère `ctx` avant d'incrémenter `active_output_callbacks` | Contrat OS de fin d'admission et preuve mémoire empêchant l'accès tardif au userdata |
| AD06 — Échec de disposition | P1 | Échec de `AudioQueueDispose(ctx->queue,true)` : code de défaut enregistré, mémoire conservée ; devenir de la file inconnu | Documenter les issues OSStatus réelles et la propriété de la file et des buffers sur tous les retours d'erreur |
| AD07 — Rejet initial de liaison | P2 | Rejet de route suivi d'une tentative de disposition, avec quarantaine quel que soit le résultat | Distinguer erreur de liaison, succès/échec OS et références éventuellement survivantes |
| AD08 — Conservation permanente | P1 | Deux seuls `free(owner_ctx)` avant publication ; chemin final retourne `-1` et place le processus en quarantaine | Établir borne mémoire par processus, traitement des ressources OS et processus de fermeture, sans considérer la rétention comme une libération |
| AD09 — Retrait du listener | P1 | `AudioQueueRemovePropertyListener` précède le dispose final ; un échec de retrait est signalé | Obtenir une preuve spécifique de non-réentrance/fin des listeners déjà en cours avant toute manipulation de la file |

**Précision :** « HIGH » indique une **priorité de revue**, pas une faille exploitable ni une race reproduite. Les neuf constats exigent des preuves non encore obtenues ; aucune occurrence de callback réel n'a été observée.

## Méthode adversariale non simulée

- Recontrôle du hash du C historique, de la source candidate et de la reconstruction des trois edits exacts selon GEN-R26.
- Revue fonctionnelle séparée de `fill_audio`, `output_callback`, `queue_running_listener` et `acoustic_output_impl`. Le scanner d'accolades est **borné à la source épinglée** : ce n'est pas un parseur C11 complet ni un analyseur de threads.
- Chaque constat possède deux références à des lignes réelles du candidat, sous SHA-256. Neuf prédicats rejettent toute modification non revue de leur surface de preuve.
- Vingt tests Python supplémentaires analysent les contrats, les chaînes de provenance, les accès partagés et des **altérations de texte source** destinées à faire échouer les vérificateurs. Ces altérations ne génèrent ni exécution CoreAudio, ni ordonnanceur fictif, ni signal ou mesure scientifique.
- Le lanceur `RUN_GEN_R27_MAC_INTEL.command` refait réellement les audits historiques R16–R26 avec l'archive R19 originale en lecture seule, compile l'objet C GEN-R26 **avec `clang -c` uniquement**, conserve les cinq objets acoustiques/EM hors de l'exécutable, les 33 assertions C et l'audit `nm` des symboles de sortie.
- Seule une exécution propriétaire Mac Intel **réussie** créera un dossier privé de **16 fichiers JSON/Markdown R20–R27** avec leur manifeste SHA-256.

**Cible Mac GEN-R27 : 537 tests Python (517 + 20), 33 C, 144 fichiers vérifiés ; objet candidat compilé uniquement, non lié/non chargé. GEN-R27 Mac : PENDING.**

## Statuts inchangés

**9 nouveaux constats GEN-R27 OPEN_NOT_PROVEN**, **15 obligations GEN-R23 OPEN**, **7 constats GEN-R24 OPEN**, **9 plans GEN-R25 non intégrés**, **11 portes Bureau OPEN/0 résolue**. Aucune propriété de *race-freedom*, quiescence des callbacks ou véritable échec de disposition CoreAudio n'a été certifiée. Aucune signature indépendante réelle n'est présumée.

`RoadMap P0.01=IN_PROGRESS`; `BUREAU_CERTIFICATION=PENDING`; `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
