# FREQMED GEN-R21 — Préparation du Bureau : 11 portes, aucun certificat

**Verdict documentaire maximal : EVIDENCE_GAPS_MAPPED_NOT_CERTIFIED**, compatible avec `REVIEWABLE_NOT_CERTIFIED` en R20. Il n'existe aucun avis indépendant signé, aucune validation clinique ou qualification d'émission autorisée.

| Porte non résolue | Responsables fonctionnels | État et preuve indépendante manquante |
|---|---|---|
| C11_CALLBACK_RACE_FREEDOM | B09 | NOT_PROVEN ; sûreté du modèle mémoire C11 et des interleavings OS vérifiée indépendamment |
| ACTIVE_COREAUDIO_LIFETIME | B07/B09 | NOT_TESTED ; durée de vie effective des callbacks du système |
| FAILED_OS_DISPOSAL_BEHAVIOR | B07/B09 | NOT_TESTED ; échec réel OS et libération sûre du contexte |
| INDEPENDENT_PHYSICAL_CUTOFF | B06/B10 | NOT_QUALIFIED ; coupure indépendante mesurée et sûre |
| ACOUSTIC_METROLOGY | B04/B07 | NOT_PERFORMED ; équipement d'étalonnage, pression et mesures réelles |
| EM_HARDWARE_AND_METROLOGY | B05/B06 | NOT_QUALIFIED ; appareil EM identifié, contrôle RF/EMC et instruments étalonnés |
| BIOLOGICAL_EXPOSURE | B01/B02/B10 | NOT_AUTHORIZED ; études interdites tant que protocole éthique/institutionnel absent |
| MEDICAL_EFFICACY | B01/B03 | NOT_ESTABLISHED ; aucune revendication thérapeutique basée sur ce logiciel |
| EXTERNAL_EVIDENCE_SIGNATURE | B09/B10 | ABSENT ; intégrité seule n'est pas signature d'auteur ni horodatage tiers |
| BUREAU_CERTIFICATION | B01–B10 | PENDING ; noms des examinateurs et leurs validations n'ont pas été fournis |
| PRODUCTION | B09/B10 | NOT_AUTHORIZED ; fermeture préalable des autres verrous et décision explicite |

Les références de code et leur ligne seront produites sur le Mac Intel par le nouveau rapport JSON. Ce tableau est un **registre des lacunes**, pas la preuve qu'une lacune est résolue. Le Bureau peut y adjoindre ultérieurement des preuves authentiques, mais ce jalon n'émet aucun son ou champ électromagnétique, n'exécute aucun modèle de simulation et n'autorise aucun essai biologique.

**Règles permanentes :** budget logiciel nul, composants FOSS admissibles, interdiction absolue de simulation scientifique, essais physiques futurs uniquement sur banc sécurisé et séparément autorisé, aucune exposition humaine/animale/cellulaire non autorisée. L'archive historique R19 reste locale, modifiable par son propriétaire et non signée ; son contrôle SHA-256 ne garantit pas la provenance extérieure.

La branche PR #1 reste DRAFT, `RoadMap P0.01=IN_PROGRESS`, `BUREAU_CERTIFICATION=PENDING`, `PRODUCTION=NOT_AUTHORIZED`. La validation du candidat R21 sur Mac Intel demeure PENDING.
