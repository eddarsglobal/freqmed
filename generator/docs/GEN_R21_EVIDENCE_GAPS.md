# FREQMED — GEN-R21 Bureau Evidence Gap Review

## Mission et témoin réel antérieur

Le témoin **GEN-R20 FIX1** du 14 novembre 2026, commit `0812ac4a3756e795ba411ffe61a52f7f6f32e130`, a établi sur Mac Intel **397/397 Python PASS, 33/33 assertions C PASS, 108/108 sources SHA-256 intègres**, audits R16-R19 PASS, relecture de l'archive R19 historique (103 fichiers et 4 JSON), dossier R20 produit sans émission. Les deux avertissements Python liés à l'échappement Markdown ont disparu. Le verdict du Bureau était et reste `REVIEWABLE_NOT_CERTIFIED`.

## Travail source-only GEN-R21

`audits/r21_bureau_evidence_gaps.py` s'appuie sur le manifest actuel, les cinq **rapports réels R16, R17, R18, R19 et R20**, les rapports de l'archive historique R19 déjà revérifiés par R20 et les **11 statuts originaux** de `r20_bureau_archive_review.UNRESOLVED`.

Pour chacun des onze verrous, l'audit fournit :
- identifiant exact et état inchangé (`NOT_PROVEN`, `NOT_TESTED`, `NOT_QUALIFIED`, `NOT_AUTHORIZED`, `NOT_ESTABLISHED`, `ABSENT` ou `PENDING`);
- responsabilité des fonctions B01–B10 du Bureau (leur désignation ne présume pas de personnes nommées) ;
- classification du type de qualification manquante, référence **réelle** à une ligne du code C ou de la documentation avec SHA-256 contrôlé, description de la **preuve supplémentaire** requise et absence explicite de certification ;
- une règle irréversible pour cette phase : **11 OPEN, 0 RESOLVED**, même si tous les tests logiciels PASS.

Cet audit compare de nouveau les cinq JSON aux calculs des auditeurs sur les sources et l'archive R19 épinglées, vérifie le lien du binaire no-output, et refuse les changements de statut, les sources retirées, les ancrages cassés ou les preuves JSON incohérentes. Il est **documentaire et lexical** : il n'exécute pas le backend d'émission, n'ouvre aucun appareil et ne simule aucune fréquence ou mesure physique.

Le nouveau runner `RUN_GEN_R21_MAC_INTEL.command` conserve la chaîne source-only R16→R21, la compilation de cinq objets natifs **isolés et non liés**, les **33 assertions C**, le binaire refusant les émissions, puis les tests Python complets. Après un selftest PASS seulement, le propriétaire reçoit dans `~/Downloads/FREQMED_GEN_R21_BUREAU_GAPS_*` les JSON et Markdown R20 et R21 avec leur manifeste SHA-256. L'archive R19 d'origine n'est jamais modifiée.

**Cible de validation native GEN-R21 : 417 tests Python (397+20), 33 assertions C**, 113 fichiers générateur épinglés, les 11 lignes référencées, cinq preuves actuelles R16-R20 recroisées, R21 11/11 états OPEN. GEN-R21 reste PENDING jusqu'au journal Mac Intel réel.

## Limites scientifiques

Une référence à une fonction C ne prouve pas la concurrence C11, la quiescence des callbacks actifs, les erreurs réelles de l'OS, un interrupteur matériel indépendant, un niveau acoustique, un champ EM mesuré, la conformité RF/EMC, une autorisation biologique, une efficacité médicale ou une signature extérieure. Aucune sortie, même sur un banc non biologique, n'est autorisée par ce dossier.

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `ACOUSTIC_OUTPUT=LOCKED` · `EM_OUTPUT=LOCKED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
