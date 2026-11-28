# BENCH-06 R4 — Physical Backend Readiness & Independent Safety Evidence Consolidation

## Décision candidate (aucune certification)
RoadMap 1.1.0, main et précédents candidats préservés. Huit qualifications techniques propriétaire documentées sur PR #55–62 ; elles ne prouvent ni émission, ni mesure physique, ni arrêt indépendant, ni temps réel matériel. Les huit commentaires exacts et trois comptes rendus de remédiation sont conservés dans evidence.json ; ce sont des transcriptions de résultats propriétaire, non des attestations indépendantes. R4 ne lance aucun ancien test, compilation, programme natif ou flux.

## État consolidé
| Candidat | Preuve réutilisable | Limite |
|---|---|---|
| BENCH-01 | Inventaire audio/USB réel en lecture seule | Aucun instrument indépendant qualifié |
| BENCH-02 | Métadonnées de la paire acoustique | Synchronisation/latence réelles non mesurées |
| BENCH-03 FIX1 | Réservation, retrait 16 abonnements, refus DEVICE_BUSY puis PASS au repos | Pas de changement réel observé |
| BENCH-04 | Transport numérique privé | Aucun flux CoreAudio |
| BENCH-05 FIX1 | 29 assertions, 10000 blocs concurrents, contrat ABI refus | Aucun callback enregistré, aucune échéance garantie |
| BENCH-06 R1 | Descripteurs virtuels/physiques 44100 Hz, PCM Float32, mono/stéréo, 512 frames | Compatibilité descriptive seulement |
| BENCH-06 R2 | Gestionnaire ressources, retrait 9 abonnements, 2048 valeurs | Mono-propriétaire, pas de quiescence matérielle |
| BENCH-06 R3 | 28 assertions, arrêt logique, ABI refus, Guardian OFF | Arrêt physique indépendant non vérifié |

## Qualification documentaire automatisée
qualify.py vérifie le blob du manifeste, les huit commits présents localement et ancêtres de R3, le commit/blob exact de RoadMap, et la cohérence des trois journaux R1/R2/R3 avec les marqueurs et rapports retenus. Calcule les SHA-256 des journaux réellement disponibles, refuse les marqueurs absents/dupliqués et les changements de périmètre ; écrit un dossier JSON distinct sans écraser un ancien dossier. Les cinq étapes antérieures restent appuyées sur les comptes rendus GitHub et leur provenance, sans validation des journaux bruts correspondants dans R4. La vérification locale est une vérification de cohérence et d'intégrité, pas une signature des logs ni une preuve indépendante ; le SHA-256 nouvellement calculé ne prouve pas l'intégrité avant lecture. En cas de journal absent/incohérent, BLOCK documentaire sans relancer les moteurs. R4 ne peut délivrer aucune autorisation matérielle ; même PASS documentaire entraîne HARD_DENIED physique. Aucun logiciel historique relancé ; aucune dépendance additionnelle, Python standard et Git. Exécution du vérificateur sur les vrais journaux Mac reste à faire.

## Chemin court vers un backend physique
Travaux à distinguer, sans multiplier les requalifications numériques :
1. Ingénierie : terminer l'adaptateur natif de sortie et son cycle réel de ressources dans un candidat séparé, avec exclusion à la compilation de toute émission jusqu'aux gates ; définir les conditions de format, quiescence et arrêt, sans assimiler le refus ABI à un backend opérationnel. Pas de nouveau test des modules déjà validés, seulement des contrôles d'intégration nouveaux.
2. Bureau B04/B06/B07/B09/B10 : identifier le banc non biologique, transducteur, instrument de mesure indépendant étalonné, limites physiques et arrêt indépendant ; documenter l'analyse des risques. Les haut-parleurs et le microphone intégrés sont identifiés mais non qualifiés comme banc métrologique autonome. L'absence d'instrument qualifié ne signifie pas absence de tout équipement disponible ; aucun achat imposé.
3. Respecter le séquencement officiel : G0 revue/droits non attestés ; G2 profil/limites/interverrouillages ; G3 autorisation spécifique non biologique. Aucun essai physique avant les décisions exigées. Les premières mesures réelles et la quiescence matérielle nécessiteront des preuves distinctes après admission appropriée. P0.01 reste IN_PROGRESS ; P0.02/P0.04/P1.01/P1.02/P1.03 restent PENDING.
4. EM : chantier matériel distinct, pas de qualification EM ou promesse médicale dans BENCH-06.

Aucune prétendue approbation individuelle du Bureau, aucune certification, installation, émission, acquisition ou mesure physique. Pas de modification RoadMap ; aucun passage de jalon. Le dossier demande une décision explicite de l'autorité compétente ; il ne la remplace pas.
