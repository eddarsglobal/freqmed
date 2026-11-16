# FREQMED — GEN-R34 Independent Callback Userdata Lifetime & OS Ownership Proof Review

**Source de départ validée sur le Mac Intel : GEN-R33 (657/657 tests Python, 33/33 assertions C natives, 181/181 sources SHA-256, 28/28 rapports SHA-256).** Cette réussite ne représente pas une preuve formelle de concurrence ni une autorisation d'émission.

## Problème précis : entrée OS avant admission C11

Dans `generator/candidates/acoustic_macos_r31.c`, `output_callback(void *ptr,...)` et `queue_running_listener(void *data,...)` convertissent l'argument OS en `AcousticContext *ctx`, vérifient `ctx != NULL`, puis exécutent `fm_r28_gate_try_enter(&ctx->queue_admission)`. **La conversion du pointeur n'est pas en elle-même une déréférence**, mais l'accès à `ctx->queue_admission` en est une ; il suppose que `ctx` pointe encore vers un objet vivant **avant** que la première admission atomique ait été évaluée.

Un callback tardif qui entre du côté OS avec un `userdata` invalide ne serait **pas** protégé par le compteur d'admission : il doit déjà toucher la mémoire pour lire le gate. Il s'agit d'un **risque source et d'une obligation de preuve**, pas d'une violation C11 ou d'un use-after-free effectivement reproduit.

## Documentation Apple vérifiée

- `AudioQueueDispose(queue, true)` dispose la queue immédiatement (synchrone), ses buffers et arrête ses callbacks après disposition. Le résultat `OSStatus` doit être examiné. Ce texte ne permet **pas** de prétendre que l'opération a réussi malgré un retour d'erreur.
- `AudioQueueStop(queue, true)` demande l'arrêt synchrone ; dans certaines situations matérielles, le périphérique reste utilisé par d'autres services audio. Ce contrat ne fournit pas de preuve d'arrêt physique indépendante après un échec.
- `AudioQueueRemovePropertyListener` retire un callback associé au `userdata` donné. La page ne démontre pas la fin de tous les callbacks déjà entrés sur un statut d'échec.

Sources Apple :
https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29
https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29
https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29

## Frontières de durée de vie

1. **Prépublication OS :** les deux `free(owner_ctx)` prépublication sont observés et restent source-only ; aucun `free(owner_ctx)` n'apparaît après `AudioQueueNewOutput`. Cela ne prouve pas tous les chemins d'erreur du système.
2. **Publication OS :** `AudioQueueNewOutput` reçoit `ctx` comme `userdata`, le listener reçoit également `ctx`. Leurs erreurs de création ou d'installation ne fournissent pas de preuve positive de quiescence.
3. **Pré-admission :** les deux callbacks utilisent `ctx->queue_admission` pour entrer, donc l'absence de leases acceptées n'exclut pas un callback OS qui vient d'arriver et n'a pas encore atteint cet accès.
4. **Admission et exécution :** les compteurs `active_output_callbacks` et `active_property_listeners` sont incrémentés seulement après `try_enter`. Ils n'observent pas les entrées pré-admission rejetées.
5. **Fermeture OS :** le chemin de succès de `AudioQueueDispose(...,true)` est une garantie OS documentée, mais les callbacks déjà entrés, l'ordre C11 et la qualification des codes `OSStatus` ne sont pas déchargés par ce simple audit statique. Les chemins d'échec demeurent non certifiés.
6. **Quarantaine :** le contexte publié reste retenu. Cette rétention réduit certains risques de libération prématurée mais n'est ni un arrêt matériel ni une preuve de sûreté globale.

Le dossier GEN-R34 définit **11 phases documentaires et 14 obligations ouvertes, dont 4 critiques**. Elles ne constituent pas un automate de contrôle en exécution et ne peuvent entraîner aucune promotion de permission.

## Livrables et limites de test

- `audits/r34_userdata_lifetime_review.py` : analyse structurée des deux fonctions de callback, de l'ordre d'admission, des compteurs, de l'ordre publication/stop/dispose, des sites C et de la chaîne authentique R16–R33 ; deux ancrages source SHA-256 par obligation et rapports JSON + Markdown.
- `tests/test_r34_userdata_lifetime_review.py` : 20 nouveaux contrôles source-only, dont cinq mutations lexiques et une preuve de provenance historique. **Aucune simulation scientifique, aucune exécution CoreAudio, aucun essai acoustique/EM.**
- `RUN_GEN_R34_MAC_INTEL.command` : nouveaux rapports R34, conservation des objets C candidats **compilés mais non liés**, garde `unittest.TestCase.run`, `nm` du CLI non émetteur et dossier de **30 rapports R20–R34 vérifiés SHA-256** uniquement si tous les tests réussissent.

**Cibles GEN-R34 Mac Intel non exécutées : 677/677 tests Python, 33/33 assertions C, 187/187 sources SHA-256, 30/30 rapports SHA-256.** Un PASS atteste l'audit logiciel, non la sûreté physique.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
