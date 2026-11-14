# FREQMED — GEN-R18 : examen indépendant du Bureau (NON CERTIFIÉ)

## B09 — Architecture C et garde de sortie

Examiner les 13 retours lexicaux de `acoustic_output_impl`, leurs gardes exactes et les étapes de propriété mémoire. Vérifier indépendamment que les quatre `free(owner_ctx)` et les six relâchements atomiques de la réservation ne permettent aucune libération de userdata avant fermeture OS confirmée. Le rapport `GEN_R18_CONTROL_FLOW_EVIDENCE.json` ne couvre qu'un **sous-ensemble borné** du C réel : il ne revendique aucune preuve complète de concurrence, de préprocesseur ou de graphe de flot de contrôle.

Revoir les séquences `AudioQueueNewOutput`, `AudioQueueAddPropertyListener`, `AudioQueueStart`, `AudioQueueRemovePropertyListener`, `AudioQueueDispose`, les branches de résultat OS et les interdictions de réessai après erreur. Les ordres atomiques et compteurs ne prouvent pas à eux seuls la quiescence CoreAudio.

## B07/B04 — Acoustique

Aucun transducteur réellement alimenté, aucun niveau sonore mesuré, aucune fréquence physique certifiée, aucune coupure matérielle indépendante. Objet backend acoustique **compilé uniquement, non lié**. Aucun essai d'émission autorisé.

## B05/B06 — EM

Aucun générateur EM réellement qualifié, aucun port activé, aucune commande de fréquence/champ ; contrat d'instrumentation strictement documentaire et non autorisant. Les seules opérations OS exécutées sont les lectures de registre permises et les logiciels de refus de sortie.

## B10 — Sécurité / droits / gouvernance

Interdiction permanente de simulation scientifique. Aucun sujet humain, animal ou biologique exposé. Vérifier les licences directes et transitives de toute dépendance ajoutée (GEN-R18 : Python standard library seulement). La chaîne SHA-256 garantit la cohérence du contenu vérifié mais ne constitue ni une signature externe ni une certification d'efficacité médicale.

GEN-R17 logiciel : 335/335 Python, 33/33 assertions C et 25/25 contrôles R16 PASS sur Mac Intel. **GEN-R18 Mac Intel PENDING** ; cible 355 tests Python, 33 assertions C, trois preuves JSON liées et 13/4/6 sorties/ressources contrôlées.

`RoadMap P0.01=IN_PROGRESS` · PR #1 `DRAFT` · `BUREAU_CERTIFICATION=PENDING` · `NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
