# GEN-R14 — CoreAudio Lifetime Ownership & Failure-Path Hardening

## Delta technique

GEN-R13 a reçu le témoin Mac Intel : **255/255 tests Python PASS, 33/33 assertions C PASS**, les cinq objets de backend sont compilés mais non liés, aucune sortie physique. R14 reste un travail de source candidat.

GEN-R14 retire l'alias fragile du préprocesseur `#define ctx (*owner_ctx)` / `#undef ctx` et introduit `AcousticContext *ctx=owner_ctx` avec des accès explicites `ctx->...`, y compris l'adresse des membres atomiques `&ctx->...`, la file `&ctx->queue` et le pointeur de contexte `ctx` envoyé à CoreAudio. Le contexte demeure alloué sur le tas avec `calloc`, jamais dans une variable locale `AcousticContext ctx`. Cela réduit le risque de substitution imprévue par macros et améliore la revue de propriété mémoire ; il ne prouve pas l'absence de races.

### Conservation des chemins de défaillance

- Admission : `fm_context_quarantined` bloque les sessions suivantes si l'état OS n'est pas maîtrisé ; `fm_session_claim` est atomique et n'autorise qu'une session à la fois.
- Échec d'allocation : libération de la réservation uniquement, aucune création CoreAudio.
- Validation des paramètres de trames et d'enveloppe : libération du contexte pas encore remis à CoreAudio, puis libération de l'admission.
- Échec de création de file : arrêt logique et quarantaine sans `free(ctx)`, même quand `AudioQueueNewOutput` a rendu un pointeur de file nul.
- Échec d'association à la route : `AudioQueueDispose(queue,true)` vérifié ; si l'OS certifie un retour `noErr`, la mémoire est libérée ; sinon, quarantaine.
- Nettoyage normal et sur défaut : barrière logicielle, arrêt si nécessaire, retrait du listener, disposition synchrone, contrôle des compteurs actifs ; libération uniquement lorsque `dispose_confirmed` et `context_quiescent` sont vrais.
- Toute issue incertaine conserve la mémoire et refuse les nouvelles admissions, sans réessai automatique.

Les anciens tests R3–R13 qui vérifiaient des chaînes `ctx.` ou des macros ont été **adaptés** aux accès explicites plutôt que laissés en échec ; 20 nouveaux tests R14 couvrent le propriétaire mémoire. Exécution native du Mac Intel encore à obtenir.

### Bornes de la preuve

Apple indique que `AudioQueueDispose(queue,true)` effectue une disposition synchrone et que la file ne doit plus invoquer de callbacks après sa disposition. Cette garantie ne saurait être présumée si l'appel renvoie une erreur ; le bloc doit donc rester accessible. Documentation : https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose(_:_:).

Une compilation isolée et 275 tests éventuels ne sont pas une observation de l'API de sortie en fonctionnement, pas un délai de coupure matérielle, ni une qualification acoustique ou EM. Aucun son ni champ n'est émis ; aucune simulation scientifique, aucun banc fictif.

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
