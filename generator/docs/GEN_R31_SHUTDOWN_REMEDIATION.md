# FREQMED GEN-R31 — Independent Critical Shutdown Path Remediation & Fail-Closed Ownership Design

**Base attestée : GEN-R30 Mac Intel 597/597 Python, 33/33 assertions C, 162/162 fichiers source et 22/22 rapports SHA-256.** Le commit R30 `468457c8b63ae124142922fce87f77d2d8a7c35d` reste un audit réussi, **pas** une preuve de sûreté CoreAudio.

## Correction C isolée

Nouveau `candidates/acoustic_macos_r31.c`, dérivé du candidat C29. Le changement est **strictement circonscrit** à un en-tête informatif et au bloc final de fermeture. Le backend `src/acoustic_macos.c`, les candidats R26 et R29 et le portail atomique R28 restent strictement inchangés. L'exécutable public continue de lier uniquement `output_hard_denied.c`.

Le chemin critique identifié en R30 était :

- Après `AudioQueueStart`, le contrôleur fermait l'admission par `fm_r28_gate_close`.
- Si le portail `closed_and_empty` n'était pas vide, il retournait avant `AudioQueueStop` et `AudioQueueDispose`, sans preuve d'arrêt d'une file déjà démarrée.
- La quarantaine atomique interdisait une nouvelle session mais **ne constituait pas** une coupure physique.

Le candidat GEN-R31 prend désormais un instantané de l'état d'admission, **tente un arrêt CoreAudio immédiat avant tout retour pour lease active**, puis différencie :

1. **`AudioQueueStop(ctx->queue,true)==noErr`, mais admission occupée** : conserver la file, le userdata et les ressources en quarantaine, interdire une autre session, ne pas disposer une file dont les accès peuvent être en cours. La réussite de l'appel OS ne prouve ni la quiescence globale ni l'arrêt physique mesuré.
2. **`AudioQueueStop(...,true)!=noErr`** : enregistrer un défaut, mettre le processus en quarantaine et retourner sans disposition ni libération. **RISQUE CRITIQUE** : la file peut encore être active ; aucun arrêt matériel n'est prouvé. Ce comportement ne saurait être autorisé pour une émission physique.
3. **Arrêt OS réussi et absence apparente de leases** : poursuivre les chemins historiques de retrait du listener et de disposition, lesquels restent **non certifiés**, notamment en cas d'erreur `OSStatus`.

**Attention :** le code est compilé comme objet C isolé et **jamais lié, chargé ou exécuté**. Ce jalon ne reproduit aucune race ni aucun callback et ne réalise aucune simulation scientifique, aucun essai instrumenté, aucune émission acoustique/EM.

## Contrats Apple et limites

- Apple documente `AudioQueueStop(queue,true)` comme arrêt synchrone **lorsque l'API réussit**, mais cette documentation ne fournit pas de garantie générale de coupure physique après échec.
- Apple documente `AudioQueueDispose(queue,true)` comme disposition immédiate/synchrone ; les postconditions en cas d'échec, les listeners déjà entrés et la durée de vie du pointeur `userdata` exigent une revue indépendante.
- Une lecture `closed_and_empty` n'élimine pas les callbacks tardifs qui accèdent à `userdata` avant le portail C11.
- `AudioQueueEnqueueBuffer` demeure sous le verrou PCM : ses garanties de réentrance et temps réel restent ouvertes.

Documentation primaire :
- https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29
- https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29
- https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29

## Preuves logicielles et admission

`audits/r31_critical_shutdown_review.py` recalcule le registre historique R16–R30, reconstruit **octet par octet** le candidat R29 à partir du C31 en annulant uniquement l'en-tête et le bloc de fermeture autorisés, puis vérifie les ancrages C31. Huit nouvelles obligations R31 restent `OPEN_NOT_PROVEN` (**deux critiques**). Les douze constats R30, dont deux critiques, **ne sont pas promus**.

`tests/test_r31_critical_shutdown_review.py` ajoute 20 tests Python source-only (contrôles de branches, mutations textuelles et preuve réelle d'archive). Le lanceur Mac Intel garde une compilation `clang -c` **non liée**, l'audit `nm`, les anciens tests et un dossier privé de **24 rapports R20–R31**.

**Cibles Mac Intel non encore exécutées : 617/617 Python ; 33/33 assertions C ; 169/169 fichiers intègres ; 24/24 rapports SHA-256.** Le succès logiciel éventuel ne pourra pas être utilisé comme autorisation physique.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
