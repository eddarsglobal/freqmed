# FREQMED — GEN-R23 : C11 Happens-Before & Callback Quiescence Proof Obligations

**Type de travail : revue statique du véritable code source, pas une simulation ni un essai CoreAudio.** Le témoin utilisateur GEN-R22 Mac Intel du 15 novembre 2026 a confirmé **437/437 tests Python**, **33/33 assertions C**, **118/118 sources SHA-256**, dix-sept observations statiques et trois risques encore non prouvés ; le dossier de six fichiers de revue R20–R22 a été vérifié. Aucune sortie.

## Critère de revue

La génération GEN-R23 doit créer un registre de **15 obligations de preuve ouvertes**, chacune liée à **deux véritables lignes du code C épinglé** et à une compétence du Bureau. L'intégrité des fichiers, les tests textuels et l'ordre des instructions sont des **indices documentaires** : ils ne sont ni un ordre de synchronisation mémoire C11 ni la preuve de quiescence d'un callback macOS. Les obligations de preuve ne doivent être considérées comme acquittées que par des démonstrations techniques indépendantes appropriées, non par la réussite automatique des tests.

### Groupe A — Five C11/PCM happens-before obligations (B09, B07)

| ID | Observation du code source | Justification nécessaire pour acquitter |
|---|---|---|
| HB01 | `AudioQueueNewOutput` précède le préremplissage du contrôleur ; `AudioQueueStart` le suit | Garantie effective que le callback ne peut pas écrire durant le préremplissage après création de la file, ou introduction d'une synchronisation commune |
| HB02 | `phase` et `frames_written` sont non atomiques | Graphe complet des accès concurrents et des relations *happens-before* pour toutes les écritures/lectures de ces champs |
| HB03 | `output_callback` utilise le `pcm_writer_gate` avec acquire/release | Preuve que ce verrou couvre tous les écrivains pertinents, pas seulement les callbacks |
| HB04 | Le contrôleur appelle `fill_audio(ctx,b)` sans acquisition du même verrou | Preuve d'absence de chevauchement contrôleur/callback ou modification future revue, sans activation de sortie ici |
| HB05 | Initialisations atomiques avant publication du pointeur à `AudioQueueNewOutput` | Contrat OS et preuve de visibilité sûre du contexte côté callbacks |

### Groupe B — Five callback-lifetime / quiescence obligations (B07, B09)

| ID | Observation | Preuve manquante |
|---|---|---|
| Q01 | Contexte alloué sur le tas, userdata partagé avec callback de sortie et listener | Garantie de propriétaire vivant pour chaque référence potentielle |
| Q02 | Compteurs incrémentés après réception du pointeur userdata | Preuve empêchant une nouvelle entrée tardive entre lecture à zéro et libération |
| Q03 | Le code consulte les deux compteurs avant la libération finale | Barrière d'admission OS réelle, pas seulement des lectures acquire |
| Q04 | Suppression du listener avant dispose final | Garanties de fin de dispatch et comportement des erreurs de suppression |
| Q05 | Succès dispose synchrone enregistré avant l'évaluation de quiescence | Validation du contrat OS pour tous les callbacks et cohérence mémoire avant `free` |

### Groupe C — Five failed-disposal / owner-retention obligations (B07, B09, B10)

| ID | Observation | Preuve manquante |
|---|---|---|
| D01 | Échec du binding suivi d'un dispose et de la quarantaine conditionnelle | Conduite réelle de l'OS si le dispose échoue durant ce chemin précoce |
| D02 | Échec du dispose final : défaut enregistré et aucun `free` dans la branche d'erreur | Confirmation de la propriété du contexte encore accessible à l'OS, sans UAF ni retry |
| D03 | Échec d'inscription du listener déclaré incertain | Contrat réel lorsque l'inscription retourne une erreur mais qu'un callback peut déjà avoir été préparé |
| D04 | Échec de suppression du listener empêchant `context_quiescent` | Sort réel des callbacks et références après erreur de suppression |
| D05 | Fermeture et quarantaine au niveau du processus | Preuve que l'absence de réadmission et la conservation du tas valent pour tous les chemins concurrents et terminaux |

**Point de vigilance déterminant :** `AudioQueueDispose(queue, true)` est documenté par Apple comme synchrone dans le chemin de succès (https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose). Cette documentation ne qualifie pas les conséquences d'un échec réel de `AudioQueueDispose` sur une instance non liée à l'exécutable, et n'établit pas à elle seule toutes les relations happens-before C11. Les acquire/release C11 sont des relations spécifiques de synchronisation, pas une garantie universelle sur tout le code (https://en.cppreference.com/w/c/atomic/memory_order).

## Méthode de vérification documentaire

Le nouveau `audits/r23_happens_before_obligations.py` réexamine le code `src/acoustic_macos.c` inchangé depuis GEN-R19 et revalide le JSON réel GEN-R22 contre R16→R21 et l'archive historique R19 conservée en lecture seule. Quinze contraintes lexicales bornées, leurs références SHA-256 et la liste explicite des justifications absentes alimentent le nouveau dossier JSON/Markdown. **20 tests Python supplémentaires** contrôlent sources, registres, refus de fausse certification et altérations textuelles ; ils ne créent aucun événement CoreAudio ni ordonnanceur artificiel d'interleavings.

Le lanceur `RUN_GEN_R23_MAC_INTEL.command` reconduit la compilation de cinq objets natifs isolés non liés, **33 assertions C**, l'audit `nm` du binaire sans sortie, les tests Python puis, uniquement après succès, un dossier privé contenant **huit fichiers JSON/Markdown des revues R20–R23** et leur manifeste SHA-256. La source C native n'est pas modifiée ; aucun appel API de sortie n'est exécuté.

**Cible GEN-R23 Mac Intel : 457 tests Python (437+20), 33 assertions C, 123 sources épinglées. Quinze obligations OPEN, zéro acquittée, onze portes du Bureau OPEN. Résultat Mac GEN-R23 : PENDING.**

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `ACOUSTIC_OUTPUT=LOCKED` · `EM_OUTPUT=LOCKED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
