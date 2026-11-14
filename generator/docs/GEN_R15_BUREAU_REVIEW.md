# FREQMED GEN-R15 — Bureau review request (NON CERTIFIED)

## Vérification demandée

**B09 : architecture, mémoire et concurrence**
- Revoir la double vérification d'admission avant/après acquisition de `fm_session_claim`, les barrières de mémoire atomiques et les courses entre admission et quarantaine.
- Inspecter tous les chemins de retour de `acoustic_output_impl`, la propriété de `owner_ctx` et les API OS pouvant conserver des callbacks.
- Examiner l'enregistrement et le retrait des listeners : l'OS peut signaler un échec sans garantir le résultat ; la politique GEN-R15 est volontairement pessimiste.
- Auditer les chemins `AudioQueueNewOutput`, `AudioQueueStop`, `AudioQueueRemovePropertyListener`, `AudioQueueDispose`, ainsi que le maintien explicite de `ctx->queue` lorsque dispose échoue.
- Vérifier que la **mise en quarantaine n'implique ni libération ni réessai**, et que toutes les suites R1–R15 passent sans modifier les refus d'émission.
- La revue statique ne certifie ni l'absence d'accès mémoire tardif ni la sûreté d'un composant CoreAudio actif.

**B04/B07 : acoustique et signal**
Aucune sortie autorisée, aucun transducteur, pression acoustique, fréquence de sortie, délai de coupure ou mesure physique indépendante. Ne pas confondre les compteurs logiciel et la sécurité acoustique.

**B05/B06 : matériel EM**
Aucun instrument réel qualifié. Le contrat documentaire GEN-R11 reste `PRESENT_UNVERIFIED` au mieux, jamais autorisant. Aucun pilote EM, aucune ouverture de port, aucune émission.

**B10 : sûreté, éthique, réglementation**
Aucun essai biologique. Aucun banc d'émission non biologique autorisé. Les coupe-circuits matériels indépendants et la métrologie réelle doivent faire l'objet d'une qualification distincte avant toute mise en service.

## Gouvernance et admission

GEN-R14 Mac Intel logiciel : 275/275 Python et 33/33 assertions C PASS, cinq objets isolés et aucune émission.
GEN-R15 vise **295 tests Python et 33 assertions C**, statut Mac propriétaire **PENDING** jusqu'au vrai journal.
`RoadMap P0.01=IN_PROGRESS`; `BUREAU_CERTIFICATION=PENDING`; PR #1 `DRAFT`, `main` inchangée.
`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
