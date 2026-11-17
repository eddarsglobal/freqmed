# FREQMED — GEN-R25 Independent C11 Synchronization & Ownership Remediation Design

**État : PROPOSITIONS À EXAMINER, PAS CORRECTIFS C APPLIQUÉS.** Aucun fichier `generator/src/*` n'est modifié par ce jalon, aucun callback CoreAudio n'est exécuté et aucune sortie physique ou simulation scientifique n'est autorisée.

## Point de départ attesté sur Mac Intel

Témoin propriétaire du **15 novembre 2026** : GEN-R24, commit `78d6f8667de4c9834b4b89feb0c36ca39a5e3c87`, **477/477 tests Python PASS, 33/33 assertions natives C PASS, 128/128 sources SHA-256 PASS**. Le dossier privé de **dix rapports JSON/Markdown R20–R24** a été vérifié par SHA-256. La source `src/acoustic_macos.c` demeure inchangée depuis le pin R19. Les **19 champs de contexte / 112 références lexicales**, les **11 appels directs AudioQueue**, les **sept risques GEN-R24**, les **15 obligations GEN-R23** et les **11 portes du Bureau** restent le périmètre de preuve.

Ce nouveau dossier sort de la simple énumération : il propose des **modifications techniques ciblées**, avec délimitation de propriété et conditions d'acceptation, mais refuse de les présenter comme implémentées ou sûres sans revue C11/OS ultérieure.

## Volet A — Correction de la concurrence PCM (B09, B07)

| ID | Priorité | Cible et modification examinée | Critère indispensable |
|---|---|---|---|
| RM01 — Écrivain PCM unique | P1 | `fill_audio(ctx,b)` est appelé directement pendant le préremplissage du contrôleur ; le callback appelle également `fill_audio(ctx,buf)`. Examiner une architecture à propriétaire unique ou un verrou **partagé par les deux chemins**, jamais le seul verrou callback existant | Matrice C11 complète de toutes lectures/écritures de `phase`, `frames_written`, `queue` et preuve happens-before |
| RM02 — Couverture du verrou | P1 | Le `pcm_writer_gate` actuel fait acquire/release dans le callback, mais pas autour du préremplissage contrôleur. Examiner chaque sortie anticipée, la réentrance et le temps réel | Aucun écrivain non protégé ; pas de blocage non borné d'un callback audio |
| RM03 — Transfert de propriété PCM | P1 | Après la création AudioQueue et avant démarrage, séparer les phases de préremplissage et de callback ; ne pas inférer de leur ordre textuel la non-réentrance OS | Contrat explicite d'admission et publication des champs du contexte avant le premier callback |

**Aucune de ces propositions ne constitue un patch exécutable dans GEN-R25.** Même l'ajout naïf d'un spinlock au contrôleur ne résoudrait pas l'admission des callbacks ou les risques temps réel. Le futur correctif devra être isolé et réaudité en tant que nouvelle révision de source, non en autorisant l'ancienne.

## Volet B — Durée de vie des callbacks et du userdata (B07, B09)

| ID | Priorité | Cible et modification examinée | Critère indispensable |
|---|---|---|---|
| RM04 — Barrière d'admission | P1 | `output_callback` reçoit `ctx` avant d'incrémenter `active_output_callbacks`. Le compteur à zéro ne peut pas, à lui seul, empêcher une entrée ultérieure | Garantie OS ou autre mécanisme validé interdisant de nouveaux callbacks avant `free(owner_ctx)` |
| RM05 — Listener | P1 | Registration/removal de `queue_running_listener` ; distinguer callback lancé, callback en cours, désinscription réussie et résultat OS incertain | Preuve que les listeners ayant reçu userdata ont fini et ne peuvent plus revenir |
| RM06 — Disposition synchrone réussie | P1 | Le code utilise `AudioQueueDispose(ctx->queue,true)`, `dispose_confirmed`, les compteurs et `context_quiescent` ; ne pas considérer ce dernier comme preuve autonome | Contrat exact Apple applicable **au succès**, relation C11 adaptée et absence de références survivantes avant libération |

Apple décrit `AudioQueueDispose(..., true)` comme synchrone et indique qu'après disposition la file n'invoque plus de callbacks : https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose. Cette documentation est **une condition externe à intégrer dans une preuve**, pas une preuve du programme entier ni des comportements en cas de retour `OSStatus` négatif. La documentation `AudioQueueRemovePropertyListener` décrit la désinscription mais n'atteste pas une attente de chaque callback déjà actif : https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener.

## Volet C — Propriété mémoire en erreur OS et quarantaine (B07, B09, B10)

| ID | Priorité | Cible et modification examinée | Critère indispensable |
|---|---|---|---|
| RM07 — Rejet du binding / registration incertaine | P1 | Distinguer les états si `AudioQueueNewOutput`, la liaison de route ou l'inscription listener échouent ; un résultat d'erreur ne prouve pas l'absence de référence OS | Chaque retour OS correspond à un propriétaire du contexte et à une action terminale conservatrice |
| RM08 — Échec de libération finale | P1 | Si `AudioQueueDispose` ou l'enlèvement du listener échoue, conserver la queue et `owner_ctx`, mettre l'admission en quarantaine et exclure le retry | Aucune double libération, aucune réouverture et ressources retenues explicitement bornées |
| RM09 — Propriété du pointeur queue | P2 | `ctx->queue` est non atomique, utilisé dans plusieurs fonctions ; ne pas autoriser un effacement concurrent avec son utilisation callback | Modèle d'un propriétaire unique et preuves avant mise à NULL / libération |

### Machine d'état candidate — à ne pas confondre avec le code actuel

`UNPUBLISHED`, `QUEUE_PUBLISHED`, `SHUTDOWN_REQUESTED`, `LISTENER_UNREGISTERED`, `DISPOSAL_CONFIRMED`, `DISPOSAL_UNCERTAIN`, `QUARANTINED` sont **sept états proposés**. Neuf transitions proposées couvrent notamment l'échec avant publication, l'arrêt, l'absence d'un listener inscrit, les échecs de libération et la quarantaine. Les états terminaux interdisent une nouvelle admission. **Cette esquisse n'est ni exhaustive ni implémentée ; elle ne décrit pas toutes les branches de gestion des erreurs et ne règle pas la propriété des listeners à elle seule.**

## Protocole de qualification et de remise au Bureau

La seule sortie de GEN-R25 est une revue de plans et un registre des preuves : neuf propositions (huit P1, une P2), **zéro patch C appliqué**, zéro obligation acquittée. Le programme de vérification refait réellement la chaîne R16–R24 depuis les fichiers épinglés, reprend l'archive propriétaire R19 en lecture seule, contrôle les références aux lignes du C réel et bloque l'exécutable émetteur.

Une nouvelle révision remédiée devra avoir son propre commit/source pin, une analyse indépendante complète de C11 (écrivains/lecteurs et transitions), une confrontation aux contrats OS, une preuve explicite de quiescence avant libération, une revue de la quarantaine en cas d'erreur et une autorisation de qualification séparée. **Aucune émission ni expérimentation matérielle ou biologique n'est autorisée par ce dossier.**

**Cible GEN-R25 : 497 tests Python (477+20), 33 assertions C natives, 133 fichiers épinglés, douze rapports R20–R25 avec SHA-256, 9/9 remédiations PROPOSED_NOT_APPLIED, 15 obligations OPEN, 7 constats OPEN, 11 portes Bureau OPEN. Validation Mac Intel GEN-R25 PENDING.**

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
