# FREQMED — Bureau GEN-R23 : relations happens-before, quiescence, échec OS

**État : `PROOF_OBLIGATIONS_OPEN_NO_EMISSION`.** Seize slogans de sécurité ne sont pas une preuve : le registre de GEN-R23 doit montrer **quinze obligations de preuve explicitement ouvertes**, pas quinze contrôles de sûreté accomplis.

## Revue B07 / B09 / B10

**B09 — Concurrence mémoire C11.** Exiger une matrice de tous les champs partagés et des opérations concurrentes, identifier les accès non atomiques à `phase` et `frames_written`, établir les faits *sequenced-before*, synchronizes-with et happens-before avec preuve de publication des userdata. Les chemins d'exécution contrôleur/callback doivent être couverts par une obligation commune. Un verrou protégeant seulement les callbacks ne suffit pas, à lui seul, à établir la sérialisation avec le préremplissage contrôleur.

**B07 — Durée de vie AudioQueue.** Exiger les garanties documentées de création, callback, listener, retrait, stop et dispose ; délimiter exactement le cas de succès de `AudioQueueDispose(queue,true)`. Une lecture de compteurs actifs à zéro ne prouve pas qu'aucune entrée tardive ne surviendra. Les erreurs de listener et de libération restent non qualifiées.

**B10 — Fermeture et propriété en cas d'échec.** Revoir tous les retours OS d'erreur en distinguant fermeture logique, mémoire encore potentiellement référencée, références CoreAudio non libérées et absence de nouvelle admission. Toute preuve manquante bloque la certification ; aucune émission ne doit être tentée pour combler une lacune documentaire.

## Conditions de sortie du présent jalon logiciel

- Le registre de quinze obligations doit exister et chacune doit être reliée à deux lignes du source avec SHA-256.
- Les trois portes historiques restent `C11_CALLBACK_RACE_FREEDOM=NOT_PROVEN`, `ACTIVE_COREAUDIO_LIFETIME=NOT_TESTED` (la revue R22 qualifie sa preuve `NOT_PROVEN`), `FAILED_OS_DISPOSAL_BEHAVIOR=NOT_TESTED`. Aucune contradiction de statuts ne doit être camouflée.
- Le dossier de GEN-R23 doit transporter la chaîne R20–R23 et les empreintes locales ; la revue de l'archive originale R19 est en lecture seule.
- La validation logicielle Mac Intel nécessite **457/457 Python et 33/33 C**, sans liaison de `src/acoustic_macos.c` à l'exécutable. Aucun PASS logiciel n'acquitte une obligation de preuve formelle C11 ou une validation OS.
- Le Bureau conserve **11 portes OPEN, zéro résolue**, P0.01 IN_PROGRESS, ses membres non présumés nommés, aucun certificat indépendant, aucune signature extérieure.

**Interdits permanents :** `NEVER_SIMULATION=ENFORCED`, `ZERO_COST_FOSS=ENFORCED`, `ACOUSTIC_OUTPUT=LOCKED`, `EM_OUTPUT=LOCKED`, `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`.
