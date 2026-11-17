# FREQMED — GEN-R20 : dossier de préparation du Bureau

**Statut maximal attendu : `REVIEWABLE_NOT_CERTIFIED`.** Aucun contrôle logiciel, rapport JSON, résultat de test ou signature de commit ne peut modifier ce statut sans validation humaine externe et distincte selon le RoadMapGuardian.

| Porte de revue | État requis tant que non démontré |
|---|---|
| Absence de races C11 dans CoreAudio | NOT_PROVEN |
| Durée de vie des callbacks actifs | NOT_TESTED |
| Comportement réel après échec AudioQueueDispose | NOT_TESTED |
| Coupure matérielle indépendante | NOT_QUALIFIED |
| Métrologie acoustique réelle | NOT_PERFORMED |
| Matériel EM et métrologie | NOT_QUALIFIED |
| Exposition biologique | NOT_AUTHORIZED |
| Efficacité médicale | NOT_ESTABLISHED |
| Signature extérieure des preuves | ABSENT |
| Certification du Bureau | PENDING |
| Production | NOT_AUTHORIZED |

Le Bureau doit examiner les quatre documents source R16/R17/R18/R19, les décomptes de couverture statique, la liste des limites, les codes C des fonctions sensibles et la chaîne d'empreintes. La propriété matérielle et les obligations de sécurité/éthique n'ont pas été qualifiées. Un dossier marqué PASS pour l'intégrité logicielle **ne constitue pas l'autorisation d'effectuer des émissions, même sur un banc non biologique**.

### Exigences de preuve
- Relecture de l'archive R19 **réelle** sous `~/Downloads/FREQMED_GEN_R19_EVIDENCE__63dtqxs`, avec son manifeste épinglé de 103 fichiers et ses quatre rapports. Aucun transfert automatique ou écriture dans ce dossier.
- Vérification exacte du commit et de la SHA-256 du manifeste R19, distinct du manifeste plus récent R20.
- Relecture du JSON GEN-R20 et de la grille Markdown générés uniquement après la réussite du selftest Mac Intel.
- Révision indépendante des cas que le lexer borné R16–R19 ne couvre pas, notamment préprocesseur, appels interprocéduraux, comportement OS réel et règles de mémoire concurrente.
- Maintien des restrictions permanentes : **zéro coût FOSS**, **jamais de simulation scientifique**, **aucune exposition biologique**, **aucune sortie acoustique/EM**, **aucune mise en production**.

**Baseline réelle : GEN-R19 Mac Intel 375/375 Python, 33/33 C, 103/103 fichiers, preuve R19 archivée PASS.** GEN-R20 cible 395 tests Python et 33 C, à attester par le propriétaire. La préparation du Bureau ne certifie ni l'efficacité médicale ni la sécurité physique ; elle organise les preuves et lacunes.

`BUREAU_CERTIFICATION=PENDING` · `RoadMap P0.01=IN_PROGRESS` · `NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
