# FREQMED GEN-R15 — Failure-Path Completeness & Resource Ownership Audit

**Statut : préparation du code seulement ; validation native Mac Intel et certification scientifique en attente.**

## Contexte confirmé
Le propriétaire a validé **GEN-R14** sur Mac Intel : 275/275 tests Python, 33/33 assertions natives C, 78/78 sources intègres, cinq objets de backend compilés **non liés**, aucune émission acoustique/EM. Cette preuve n'exerce jamais le backend CoreAudio actif.

## Inventaire concret des issues (source GEN-R15)

| Chemin | Risque de propriété mémoire | Politique GEN-R15 |
|---|---|---|
| Commande invalide / route inexistante / paramètres invalides | Aucun contexte publié | Rejet avant `calloc`, sans ressource CoreAudio |
| Quarantaine déjà publiée | Retenter un ancien contexte incertain | Rejet avant admission |
| Session concurrente | Deux sessions de sortie dans un processus | Rejet atomique par `fm_session_claim` |
| Quarantaine publiée entre prélecture et réservation | Admission après un défaut concurrent | **Seconde vérification après acquisition du verrou**, rejet + libération de la réservation non exposée |
| `calloc` échoué | Aucun contexte publié | Relâchement du verrou de session |
| Total des trames nul / enveloppe invalide | Contexte alloué mais non remis à CoreAudio | `free(owner_ctx)` + relâchement du verrou |
| `AudioQueueNewOutput` échoué, même référence de file nulle | OS peut détenir des ressources / userdata incertaines | Barrière de fermeture, contexte retenu, quarantaine irréversible ; aucune émission |
| Binding de route rejeté | File OS créée, arrêt non démarré | Arrêt logique + `AudioQueueDispose(true)` et vérification du résultat |
| Binding rejeté, disposition réussie | Callback potentiellement en vol | **Libération seulement avec les deux compteurs de callback/listener à zéro** ; sinon quarantaine |
| Binding rejeté, disposition échouée | Ressource OS incertaine | Aucun `free`, quarantaine |
| `AudioQueueAddPropertyListener` échoué | État d'inscription ambigu | **`listener_registration_uncertain=1` et défaut mémorisé** ; sortie uniquement en quarantaine |
| Listener inscrit puis retrait échoué | Callback de propriété potentiellement actif | **`listener_remove_failed=1`, défaut mémorisé**, interdiction de libérer même si disposition déclare succès |
| Arrêt ou vidange interrompus / erreur d'enqueue / watchdog | File créée et démarrage potentiellement actif | Barrière, tentative d'arrêt contrôlée, retrait listener, disposition ; aucune réadmission sans quiescence |
| `AudioQueueDispose(true)` échoué | OS peut conserver la file et ses callbacks | **Ne pas effacer `ctx->queue`**, mémoriser défaut, conserver mémoire, refuser réessai |
| `AudioQueueDispose(true)` réussi | L'OS déclare la disposition réussie | Marquer `dispose_confirmed=1`, effacer référence ; exiger EN PLUS absence d'ambiguïté de listener et compteurs à zéro |
| Quiescence finale non confirmée | Risque de pointeur vers ressource libérée | Contexte retenu en quarantaine ; retour en échec |
| Quiescence entièrement confirmée | Contexte local non utilisé | Libération heap, relâchement session ; le code ne devient pas autorisé en production |

Les causes internes `FM_FAULT_LISTENER_REGISTRATION` et `FM_FAULT_LISTENER_REMOVAL` enrichissent la trace d'échec. Il n'y a aucune commande de démarrage, réarmement ou émission supplémentaire.

## Limites essentielles

Ce tableau décrit des décisions **source-only**, pas une exécution forcée des échecs Apple ni un certificat de synchronisation. Les compteurs atomiques seuls ne prouvent pas l'absence de callback tardif. Si l'API OS retourne un échec, conserver le contexte empêche de le libérer prématurément, mais ne répare pas une ressource OS, ne coupe pas un signal physique et peut consommer volontairement de la mémoire pendant toute la vie du processus. Le backend source CoreAudio est compilé en objet **isolé et non lié** ; l'exécutable testable refuse toute émission.

L'EM reste dépourvu d'instrument qualifié : contrôle documentaire non autorisant, aucune ouverture de port, aucune consigne de fréquence ni transmission. Aucune simulation scientifique, aucun dispositif fictif ou relevé physique inventé.

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
