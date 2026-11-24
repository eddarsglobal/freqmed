# P0.01 — Consolidation G0 après GEN-R66
Date : 2026-11-24. Revue documentaire assistée par IA ; aucune signature ni certification indépendante.

## Norme et décision déjà exprimée
- RoadMap.md v1.0, blob Git `81024a17e9aeafdfb5319455dae30529d85d6a16` (main, relu le 24 novembre).
- README.md blob `41e503b6b3ccb13aa786a3868db80f043cdd9ced`.
- La déclaration du propriétaire `APPROVE_MISSION_V1_REBASE`, rapportée le 20 novembre 2026, visait main `90bd1e5177cc02f99805bfacedce42e0cbd378d0` et la même RoadMap. Le compte rendu antérieur indique JSON/SHA-256 PASS et identité non authentifiée cryptographiquement. Le reçu TTY original n'a pas été récupéré pendant cette revue. Reconnaître la décision rapportée, ne pas la faire ressaisir ; ne pas la convertir en certification ni inventer l'empreinte du reçu.
- La RoadMap reste seule normative : P0.01 IN_PROGRESS_REBASE_REVIEW, P0.02 PENDING, candidats préparatoires P1.01/P1.02/P2.01 autorisés sans émission par clause E.

## Reconnaissance des preuves techniques, sans adoption automatique
Les prototypes V4/V5 et R29–R32 demeurent historiques et non probants pour la génération physique. R43–R47 : candidats sources historiques, aucune certification d'arrêt physique. GEN-R63/R64/R65 : cycles fonctionnels Mac rapportés. GEN-R66 : moteur numérique segmenté et audit C11, kit SHA256 `e1a404911ab784c101fcb1866d0f2c8663bf9b0d4c626f27ee27902a19e80891`, PR #25 head `54fd4e6cd4a8106da12bb57fa8208ce569a4185b`, DRAFT. Rapport utilisateur du 24 novembre : [preuve enregistrée](https://github.com/eddarsglobal/freqmed/pull/25#issuecomment-7128270011), PASS_MAC_SOFTWARE_ONLY, 734 cas (733 réussis, 1 ignoré), 42/42 R66, 39/39 enregistrements de contrôle, 85/85 hashes, STOP et refus après STOP, serveur fermé, navigateur non ouvert. Le motif de skip a été vérifié dans le fichier exact tests/test_r62.py, blob `e474475d2ffb11ed967698d66fe8f871b1719f89` : « Linux-only OS isolation negative test ». Il ne constitue pas une preuve Mac ; ne pas le comptabiliser comme réussi. Le lanceur automatique séparé `FREQMED_R66_QUALIFY_20261124.py` a été relu en tant que fichier présent et son SHA256 calculé : `ea07d2c3aa63f78b6aaf0d2004073be52e345e9bf6c83a36ebb1f6ccf466d477`. Son intégration au dépôt demeure une action distincte.
Aucun nouveau test Mac demandé ; conserver les preuves exactes et utiliser le lanceur automatique pour les nouvelles régressions. La qualification R66 ne vaut ni preuve d'émission, ni arrêt matériel indépendant, ni preuve biologique.

## Droits G0 : six documents, inventaire revu
Le périmètre R51 est une proposition encore non adoptée ; les six fichiers main ont été relus, leurs six identifiants Git correspondent aux pins R51.
| Fichier | Blob | Constat |
|---|---|---|
| RoadMap.md | 81024a17e9aeafdfb5319455dae30529d85d6a16 | Texte de gouvernance du projet ; provenance/auteurs à attester |
| README.md | 41e503b6b3ccb13aa786a3868db80f043cdd9ced | Mission et règles du projet ; provenance/auteurs à attester |
| LICENSE | d645695673349e3947e8e5ae42332d0ac3164cd7 | Apache License 2.0 présente ; portée des droits à confirmer |
| docs/P0_00_R4_GOVERNANCE_CERTIFICATE.md | 83484a7629cb967e37fc2828b5d8f744dcfb9228 | Certificat de gouvernance historique uniquement ; provenance à attester |
| docs/P0_01_HOLD.md | 323c8861b7772ed6ca9df7605ea29430aafc53f8 | Rappel ancien, non normatif pour la mission refondue ; provenance à attester |
| docs/P0_01_R1_AUDIT_SCOPE.md | b3e92df90f9efd448e0bc095c88aa3d65c455d40 | Ancien inventaire, références/liens vers des tiers, sans adoption de leurs composants ; provenance du texte à attester |
Ne pas déduire de LICENSE l'autorisation de redistribuer chaque élément. Aucun nouveau composant adopté. Audit complet des dépendances, distribution, provenance et droits de tiers réservé à P0.03. CoreAudio et SDK Apple = dépendances de plateforme propriétaires, distinctes du cœur libre. G0_RIGHTS=PARTIAL_UNAPPROVED.

## Revue B09/B10 (fonctions, non signataires)
B09 : périmètre, architecture et séparation des missions cohérents ; désignation effective de l'autorité décisionnelle et validation de provenance non attestées. B10 : interdictions, limites du PASS numérique et séparation des gates conservées ; autorité et approbation indépendante non attestées. Aucune organisation externe commerciale imposée par cette revue. Aucun rôle présumé pourvu ; l'analyse IA est consultative, pas un certificat.
Verdict : REMEDIATE_G0_AUTHORITY_AND_RIGHTS_NO_CERTIFICATION. Maintenir P0.01 IN_PROGRESS_REBASE_REVIEW, P0.02 PENDING. Les suites de préparation ne doivent jamais contourner les gates. REAL_OUTPUT, BIOLOGICAL_EXPOSURE, PRODUCTION = NOT_AUTHORIZED. NEVER_SIMULATION=ENFORCED.
