# FREQMED GEN-R17 — Robustesse de l'audit statique et vérification indépendante des preuves

## Témoin de départ
Le journal du Mac Intel propriétaire pour GEN-R16 (commit `f547ca02bc23c53225a13fb84f46b38ae2ad5319`) atteste **315/315 tests Python PASS**, **33/33 assertions natives C PASS**, **25/25 contrôles statiques source PASS**, 87/87 fichiers intègres et cinq objets compilés **non liés**. Le programme exécutable garde toutes les sorties acoustiques/EM interdites. Aucun test actif CoreAudio, métrologie ni émission n'a été effectué.

## Travaux GEN-R17 : preuves et robustesse, sans simulation scientifique

1. `audits/r17_evidence_verifier.py` est indépendant des fonctions de l'auditeur R16. Il ne réutilise pas `r16_ownership_static_audit.audit()`. Il lit le **JSON réel** et inspecte lui-même le dépôt épinglé.
2. Il vérifie **chaque entrée SHA-256** de `KIT_SHA256SUMS.txt`, les chemins et la correspondance exacte entre l'arbre des fichiers du générateur et le manifeste, en excluant uniquement le manifeste et les caches Python non source. Les fichiers symboliques, entrées dupliquées ou chemins dangereux sont refusés.
3. La preuve R16 doit inclure le schéma, la méthode, les **25 identifiants de contrôles exacts**, une entrée par identifiant, `PASS`, les numéros de ligne réels et des compteurs cohérents. Une clé JSON dupliquée, un champ non reconnu ou une preuve tronquée provoque `FAIL_CLOSED`.
4. Le SHA-256 source du JSON doit correspondre aux octets de `src/acoustic_macos.c` et au manifeste. Les fonctions publiques `fm_acoustic_physical_output` et `fm_em_physical_output` sont revérifiées **indépendamment** : elles ne doivent faire que rejeter les commandes. Le bloc de liaison de l'exécutable natif doit contenir exactement six fichiers C autorisés, dont `output_hard_denied.c`, sans `acoustic_macos.c`.
5. Les huit réserves fondamentales du Bureau sont obligatoires dans le rapport : aucune preuve formelle C11 de non-concurrence, pas d'observation active des callbacks, pas de test réel d'un échec OS de disposition, pas d'interverrouillage indépendant, pas de mesure acoustique/EM ni qualification EM et aucune certification du Bureau.
6. Le vérificateur émet un **second JSON** `FREQMED_GEN_R17_INDEPENDENT_EVIDENCE_VERIFICATION`, avec les empreintes SHA-256 de la preuve canonique, du manifeste, du code, des auditeurs R16/R17 et du runner R17. Ce document n'est **pas** une signature externe, une attestation cryptographique d'identité, une preuve formelle C11 ou un certificat de sûreté.
7. Les **20 nouveaux tests R17** contrôlent d'abord la preuve réellement émise par R16 ; ils essayent ensuite des altérations **strictement logicielles** d'une copie de JSON (compteurs, méthodes, identifiants, SHA, lignes, réserves, revendications physiques) et de **copies temporaires de la source C** (libération prématurée, référence de file libérée, compteur de callback, défaut de confirmation, quarantaine neutralisée). Ces modifications ne sont **jamais appliquées aux sources officielles** et n'exécutent aucune API d'émission. Aucun signal synthétique, instrument fictif, modèle physique ou simulation scientifique.

## Chaîne vérifiable GEN-R17

`RUN_GEN_R17_MAC_INTEL.command selftest` → vérification  de toutes les empreintes sources → création de la preuve de l'auditeur R16 hors dépôt → vérificateur indépendant R17 → JSON R17 → compilation native de cinq objets isolés → audit `nm` du programme **non émetteur** → tests logiciels Python hérités et R17 → assertions natives C → statut final de refus d'émission.

À la livraison, la cible est de **335 tests Python (315 + 20)** et **33 assertions natives C** sur Mac Intel, validation propriétaire GEN-R17 encore **PENDING**. Cette chaîne reste fail-closed. Elle n'établit pas l'absence de races de callback réelles, ni un temps de coupure matérielle, ni une efficacité biomédicale.

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `ACOUSTIC_OUTPUT=LOCKED` · `EM_OUTPUT=LOCKED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
