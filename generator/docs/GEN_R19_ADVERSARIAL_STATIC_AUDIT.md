# FREQMED GEN-R19 — Adversarial Static Audit & Evidence Preservation

## Baseline réelle, sans émission

Sur Mac Intel, GEN-R18, commit `1d4b36fb6dcd5c4dab7155d5ee9fae3fd2623033`, a réussi **355/355 tests Python**, **33/33 assertions C**, R16 **25/25 contrôles**, vérificateur R17 PASS, preuve R18 **13 retours, 4 libérations heap, 6 restitutions de session** et les **97 empreintes sources**. Les cinq objets CoreAudio/EM ont été compilés isolément **sans liaison ni exécution**, `PHYSICAL_EMISSION=NONE`. Le Bureau reste non certifié.

## Développements réels GEN-R19

`audits/r19_adversarial_source_audit.py` est un auditeur Python standard-library qui vérifie de vrais octets `src/acoustic_macos.c` et `src/em_backend.c`, épinglés au SHA-256 de GEN-R18. Il réexécute l'enveloppe lexicale R18 et ajoute **13 contrôles ciblés** : absence de directives de préprocesseur dans les trois fonctions sensibles, absence d'assembleur ou de chargement dynamique non classé, conjonction complète des cinq critères de quiescence, comptage atomique symétrique des callbacks/listeners, garde d'écriture PCM, absence d'appels AudioQueue depuis les callbacks, interdiction de réinitialiser la quarantaine, inventaire des accès à la variable de quarantaine, maintien des 13 retours / 4 `free` / 6 restitutions, refus explicite des API publiques de sortie, et allowlist exacte des six sources C liées par le nouveau runner.

Le scellement strict SHA-256 de `acoustic_macos.c` et du backend EM signifie que **toute évolution de leur code exige une nouvelle revue et un nouveau commit de qualification** ; l'auditeur n'approuve aucune modification silencieuse. Les contrôles ne sont ni un compilateur C complet, ni une preuve formelle C11, ni un outil exhaustif de détection de toutes les attaques.

Les **20 tests supplémentaires** s'appuient sur les **vraies sources C**, sur des preuves R16/R17/R18 réellement recalculées et sur un binaire natif non émetteur lorsqu'il existe. Ils vérifient en particulier l'insertion de directives `#define`/`#if`, l'emploi de `dlopen` ou d'assembleur, l'appel direct de disposition de queue dans le callback, l'affaiblissement des clauses de quiescence et l'apparition de succès anticipé. Les modifications ne sont **que textuelles, en mémoire** ; le code modifié n'est ni compilé ni exécuté. Aucune simulation scientifique, mesure inventée ou instrument fictif.

## Préservation réelle des quatre preuves

`audits/r19_evidence_archive.py` recharge les vrais documents `GEN_R16_OWNERSHIP_EVIDENCE.json`, `GEN_R17_VERIFIED_EVIDENCE.json`, `GEN_R18_CONTROL_FLOW_EVIDENCE.json` et `GEN_R19_ADVERSARIAL_EVIDENCE.json`. Avant copie, il **recalcule les quatre audits** à partir du dépôt réellement épinglé, relie la chaîne SHA-256 des preuves et vérifie chaque fichier du manifeste. Il n'est exécuté **qu'après le succès du selftest complet natif** sur Mac Intel.

Une nouvelle archive locale propriétaire est alors créée dans `~/Downloads/FREQMED_GEN_R19_EVIDENCE_*` (nom unique, jamais réutilisé). Elle contient les quatre JSON, la copie exacte du manifeste `KIT_SHA256SUMS.txt`, `EVIDENCE_INDEX.json` et `EVIDENCE_SHA256SUMS.txt`. L'index contient les empreintes SHA-256 exactes, le commit transmis par le **bootstrap GitHub épinglé**, les limites et les restrictions de gouvernance. Permissions : dossier `0700`, fichiers `0600`. Une relecture finale vérifie le contenu, les sept noms de fichier, les décomptes et les empreintes. Une erreur bloque la sortie et supprime uniquement l'archive partielle créée par l'outil.

Les contrôles SHA-256 permettent de **détecter une modification par rapport au manifeste**. Ils n'empêchent pas le propriétaire ou un acteur disposant d'un accès en écriture de modifier/supprimer l'archive et de recalculer ses propres empreintes. Ce n'est **ni une archive immuable, ni une signature extérieure, ni un horodatage attesté**, ni une certification scientifique ou réglementaire. La valeur de commit vient du kit de téléchargement épinglé : sans confiance dans ce kit et son fournisseur, les hashes seuls n'authentifient pas l'auteur.

## Limites et admissibilité

Le code CoreAudio actif n'est ni lié ni exécuté. L'audit R19 n'établit **pas** la quiescence des callbacks OS, la sûreté de la libération réelle après échec `AudioQueueDispose`, le modèle mémoire C11 ni une mesure de pression acoustique ou de champ EM. Aucun dispositif de coupure indépendante n'est qualifié. Un rapport logiciel réussi ne débloque aucune émission.

**Cible de validation propriétaire GEN-R19 : 375 tests Python (355+20), 33 assertions natives C, R16/R17/R18/R19 PASS, conservation et relecture des preuves.** Jusqu'au vrai journal Mac Intel, GEN-R19 reste **PENDING**. RoadMap P0.01 IN_PROGRESS, PR #1 DRAFT, Bureau PENDING.

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `ACOUSTIC_OUTPUT=LOCKED` · `EM_OUTPUT=LOCKED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
