# FREQMED — Bureau B07/B09/B10 : revue de durée de vie CoreAudio/C11 (GEN-R22)

**Verdict maximal du logiciel : `REVIEW_REQUIRED_NO_EMISSION`.**

| Première lacune | Constat du code, non-certifiant | Exigence pour une qualification réelle |
|---|---|---|
| C11_CALLBACK_RACE_FREEDOM | Compteurs atomiques et `pcm_writer_gate` présents, champs PCM non atomiques et appel du contrôleur à `fill_audio` | Audit formel ou équivalent indépendant des accès concurrents, des relations happens-before et de tous les chemins d'échec |
| ACTIVE_COREAUDIO_LIFETIME | Compteurs à l'entrée/sortie ; fermeture et lecture à zéro ; preuve absente contre un callback tardif | Contrat documenté de l'OS, garantie vérifiée de non-réentrée et de quiescence avant `free` |
| FAILED_OS_DISPOSAL_BEHAVIOR | Quarantaine et conservation du tas en cas de retour de libération incertain | Observation système qualifiée d'échecs OS réels et absence de réutilisation / de contexte suspendu |

## Devoirs du Bureau

B09 doit conduire la revue C11 et du code natif et identifier les relations inter-thread non démontrées. B07 doit confronter les usages de l'API AudioQueue au contrat macOS exact, sans considérer l'incrément des compteurs comme une preuve de durée de vie. B10 supervise l'analyse de risques et maintient le verrou d'émission. Les noms des rôles ne désignent pas des personnes mandatées ; aucun expert réel n'a encore certifié ces fonctions.

La source `src/acoustic_macos.c` est épinglée et n'est jamais liée dans l'exécutable pour GEN-R22. Les API CoreAudio de création, démarrage, enqueue, stop, listener et dispose ne sont pas exécutées dans ce jalon. Même un PASS de 437 tests ne validerait ni le contrat réel d'AudioQueue après échec, ni la sûreté des émissions, ni une métrologie acoustique/EM.

## Preuves qui doivent rester distinctes

- **17 observations du source** : contrôles bornés (résultat logiciel), pas une preuve formelle.
- **3 risques ouverts** : décrits en JSON et Markdown, `REVIEW_REQUIRED`.
- **11 portes du Bureau** : toujours ouvertes, `0 RESOLVED`.
- **Archive privée R19** : quatre rapports historique, vérifiables par SHA-256, pas une archive signée ou immuable.
- **Témoin Mac Intel GEN-R22** : non encore produit, 437 tests attendus. Aucune activation acoustique, aucun dispositif EM, aucun essai biologique, aucune production.

`ROADMAP_P0_01=IN_PROGRESS` · `BUREAU_CERTIFICATION=PENDING` · `NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `ACOUSTIC_OUTPUT=LOCKED` · `EM_OUTPUT=LOCKED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
