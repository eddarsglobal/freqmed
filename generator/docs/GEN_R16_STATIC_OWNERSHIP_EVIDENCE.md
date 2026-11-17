# FREQMED GEN-R16 — CoreAudio Ownership Evidence & Static Concurrency Audit

## Contexte et résultat antérieur

GEN-R15 FIX1 a été validé logiciellement le 13 novembre 2026 sur le Mac Intel du propriétaire : **295/295 tests Python PASS**, **33/33 assertions C PASS**, 82 fichiers de génération intègres, cinq objets CoreAudio/EM compilés **non liés**, audit des symboles de sortie PASS. Aucun moteur n'a été exécuté pour émettre, aucun instrument n'a été qualifié, aucune simulation scientifique n'a été effectuée.

## Nouvelle méthode : analyse statique de vraies sources

Le nouveau script autonome `audits/r16_ownership_static_audit.py` analyse `src/acoustic_macos.c` à l'aide d'un lexer C borné qui **ignore les commentaires** et enregistre les lignes de source. Il identifie les définitions de fonctions et les branches `if/else` à accolades équilibrées. Il ne lance pas de code C. Il refuse les changements imprévus de structure ; un contrôle manquant ou échoué produit un verdict `REMEDIATE` ou `FAIL_CLOSED`.

Les preuves sont publiées dans un fichier JSON généré **hors du dépôt**, dans le répertoire temporaire `$WORK` du runner, au format `FREQMED_GEN_R16_STATIC_OWNERSHIP_EVIDENCE`. Le JSON contient SHA-256 du code effectivement lu, liste des contrats contrôlés, numéro de ligne, résultats, limites et raisons explicites d'incertitude. Il ne contient ni mesures physiques, ni donnée synthétique, ni mesure prétendument expérimentale.

### Contrats structurels audités
- Ordre : quarantaine initiale → revendication atomique d'unique session → seconde lecture de quarantaine → allocation heap.
- Nettoyage correct avant publication CoreAudio : échec de `calloc`, trames nulles et enveloppe nulle.
- Échec de création de file : mémoire retenue, barrière d'arrêt, absence de libération du contexte.
- Échec de binding : `AudioQueueDispose(true)`, compteurs des deux types de callbacks, quarantaine en cas de résultat incertain.
- Inscription/retrait des property listeners : défaut enregistré lorsque l'OS ne garantit pas l'état.
- Comptage des callbacks, écriture PCM exclusive, absence de `AudioQueueStop` depuis les callbacks.
- Ordonnancement : arrêt de la session puis retrait du listener puis disposition synchrone.
- Branches de disposition : échec sans `ctx->queue=NULL`, succès seul avec `dispose_confirmed=1` et suppression de la référence.
- Libération finale : seulement si disposition confirmée, absence d'incertitude de listeners et compteurs à zéro ; sinon quarantaine sans `free`.
- **Classification stricte des quatre sites** `free(owner_ctx)` de la fonction de contrôle ; toute nouvelle libération non classifiée bloque le verdict.
- Rejet inconditionnel des APIs publiques acoustiques et EM, et vérification que le runner relie uniquement `output_hard_denied.c`.

## Limites — à ne jamais extrapoler

Cet outil n'est **ni un compilateur C complet, ni une preuve formelle du modèle mémoire C11, ni un analyseur interprocédural prouvant l'absence de courses**. Une preuve lexicale ou une compilation isolée ne montre pas ce qui se passe après un retour d'erreur réel de CoreAudio. Les compteurs atomiques n'établissent pas seuls l'absence de callback tardif. La sûreté de `AudioQueueDispose` lors d'échec réel, la propriété de ressources OS, la coupure matérielle indépendante, la métrologie acoustique/EM, la qualification d'un instrument et la certification du Bureau demeurent **OUVERTES**.

Le seul exécutable lancé par le runner reste un binaire **hard-denied** ; le backend acoustique est compilé mais ni lié ni exécuté. Les tests ne simulent pas d'appareil, de mesure, de champ, de signal ou d'expérience.

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
