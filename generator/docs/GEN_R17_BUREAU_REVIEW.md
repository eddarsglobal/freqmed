# FREQMED GEN-R17 — Revue indépendante du Bureau (aucune certification)

## Questions à B09 : architecture et sécurité logicielle
- Vérifier le manifeste réel de tous les fichiers et les deux preuves JSON, ainsi que le lien entre empreintes, source et commit. Une empreinte SHA-256 n'est pas une signature par un tiers.
- Inspecter les cas de falsification des JSON et les cinq tests d'altération de code qui ne modifient que des **copies de source C en mémoire locale temporaire**. Vérifier qu'ils font réellement échouer l'auditeur R16, sans exécuter le code de sortie.
- Réexaminer indépendamment les limites des deux moteurs de contrôle : le parseur R16 est lexical borné, le vérificateur R17 vérifie les empreintes et certaines API publiques ; **aucun n'est un vérificateur formel C11** et ils ne garantissent pas l'absence de races.
- Examiner le comportement de CoreAudio lors d'un `AudioQueueDispose(...,true)` qui échoue ; la rétention de mémoire ne prouve pas la quiescence du système d'exploitation.

## Questions à B04/B07 : acoustique
Aucune onde générée ni pression acoustique mesurée. Aucune autorisation de sortie d'un transducteur. Pas de preuve de fréquence acoustique physique ni d'arrêt indépendant. La compilation d'un objet CoreAudio sans liaison ne démontre pas les performances physiques.

## Questions à B05/B06 : EM et instruments
Les registres IOKit sont utilisés en lecture seule et aucune identification de classe USB ne certifie un instrument EM. Aucun pilote autorisé, port activé ni génération de champ.

## Questions à B10 : conformité et sécurité
Aucun essai biologique, clinique, humain ou animal ; aucune émission sur banc indépendant autorisée, aucune simulation scientifique. Les évaluations réglementaires et métrologiques restent à produire.

## Gouvernance conservée
- **GEN-R16 Mac Intel logiciel : PASS** avec 315 tests Python, 33 assertions natives C, 25 contrôles statiques.
- **GEN-R17 Mac Intel : PENDING**, objectif 335 tests Python, 33 C et vérification indépendante des deux JSON.
- **PR #1 DRAFT**, `main` non modifiée, RoadMap `P0.01=IN_PROGRESS`.
- `BUREAU_CERTIFICATION=PENDING`, `NEVER_SIMULATION=ENFORCED`, `ZERO_COST_FOSS=ENFORCED`, `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`.
