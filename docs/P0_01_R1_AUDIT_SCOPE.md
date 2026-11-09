# FREQMED — P0.01-R1 : Cadrage de l'audit des instruments et logiciels de mesures réelles

**Date :** 2026-11-09  
**Base Git :** `fc84354e061abb2e73f1d94ea363fc625eb4196f` (`P0.00=CERTIFIED_GOVERNANCE_ONLY`)  
**Verdict :** `P0.01=IN_PROGRESS_DOCUMENTARY_ONLY` ; **aucun composant intégré**.

## Limites et politique scientifique

- **JAMAIS DE SIMULATION :** exclure simulateurs, générateurs de traces fictives, oscillateurs thérapeutiques, solveurs de champ, données artificielles ressemblant à des relevés, commandes d'émission.
- **100 % FOSS gratuit :** uniquement logiciels dont les licences libres autorisent réellement modification, réutilisation et redistribution ; aucun paiement, service ou compte propriétaire obligatoire. Les licences GPL sont libres mais requièrent une revue des obligations réciproques avant intégration ; absence de licence explicite = `BLOCK`.
- **Mesure empirique réelle seulement :** importer uniquement une donnée instrumentale vraie, garder le brut, l'horodatage, la configuration, l'incertitude, l'étalonnage et le SHA-256 ; refus d'affirmer une précision non calibrée.
- **Aucune autorisation matérielle :** pas de connexion ni commande d'oscilloscope, interface sonore, électrode, ultrason ou RF au stade de ce document. Aucun essai biologique ou humain, aucune promesse de traitement.

## Sources primaires examinées — candidats en attente d'audit complet

Les licences ci-dessous sont **pré-identifiées au niveau du projet amont**. Elles ne prouvent pas encore la compatibilité de la distribution, des dépendances transitives, de la version ni du matériel. `INTEGRATION=NONE`.

| Technologie | Usage envisagé | Licence amont observée | Statut et risque à auditer | Référence primaire |
|---|---|---|---|---|
| Python 3 standard (csv/json/hashlib/wave) | Inventaire et conservation de fichiers réels, SHA-256 | Licence Python/PSF ; distribution à examiner | Candidat initial sans ajout de paquet ; aucun capteur requis | https://docs.python.org/3/license.html |
| PyVISA | Interface d'instruments réels via VISA | MIT | À vérifier : version, paquets, valeur du backend ; exclure runtime NI-VISA propriétaire obligatoire | https://github.com/pyvisa/pyvisa/blob/main/LICENSE |
| PyVISA-py | Backend VISA en Python | MIT | Possibilité série/USB/réseau, dépendances optionnelles selon instrument ; **ne pas installer pyvisa-sim** | https://github.com/pyvisa/pyvisa-py |
| pySerial | Lecture d'instruments série | BSD-3-Clause | Analyse lecture seule, protocole matériel, permissions et compatibilité Mac Intel | https://github.com/pyserial/pyserial/blob/master/LICENSE.txt |
| PyUSB | Accès USB (si nécessaire) | BSD-3-Clause | Exige backend système comme libusb ; licences et drivers à vérifier ; pas d'accès appareil à ce stade | https://github.com/pyusb/pyusb/blob/master/LICENSE |
| python-sounddevice | Acquisition acoustique numérique via matériel audio | MIT | S'appuie sur PortAudio ; API de lecture sonore **interdite** à ce stade ; calibration micro non prouvée | https://pypi.org/project/sounddevice/ |
| NumPy | Statistiques et analyse de données déjà mesurées | BSD-3-Clause | Licences vendored, wheels et backends numériques à auditer ; jamais simulation d'effet physique | https://github.com/numpy/numpy/blob/main/doc/source/license.rst |
| SciPy | Analyse spectrale de fichiers réels | BSD-3-Clause | Dépendances binaires, licences bundlées et compatibilité architecture à contrôler | https://github.com/scipy/scipy/blob/main/LICENSE.txt |
| sigrok / libsigrok | Référence aux acquis instrumentaux réels | GPL-3.0-or-later | FOSS gratuit mais GPL et pilotes/firmwares parfois spécifiques ; revue juridique/matérielle avant éventuelle intégration | https://github.com/sigrokproject/libsigrok |
| PulseView | Référence externe d'interface oscilloscope | GPL-3.0-or-later | Pas d'intégration actuelle ; à distinguer d'un matériel et ses firmwares | https://github.com/sigrokproject/pulseview |

### Exclusions explicites

`pyvisa-sim`, MFEM, Meep, openEMS, k-Wave, scikit-fem, faux capteurs, simulateurs de patients : `EXCLUDED_BY_NEVER_SIMULATION`.  
NI-VISA, MATLAB, FL Studio, API payantes, pilotes propriétaires obligatoires, matériels non identifiés : `NOT_APPROVED_AS_DEPENDENCIES`.

## Séquence P0.01-R2 proposée (sans installation)

1. **Inventaire système Mac Intel en lecture seule :** versions de Git/Python, transports existants, composants installés, aucune ouverture de port, aucune émission.
2. **Audit SBOM documentaire** des versions candidates à épingler : code source, hash, SPDX, licences transitives, actifs, firmware et backend OS.
3. **Inventaire des instruments disponibles** : modèle, types d'interface, protocole de lecture, chaîne d'étalonnage et documents constructeur. Sans instrument utilisable, statut `MEASUREMENT_NOT_PERFORMED`.
4. **Gates de droits** : `PASS/REMEDIATE/BLOCK` par composant et par combinaison de dépendances ; absence de licence vérifiée = `BLOCK`.
5. **Tests d'intégrité documentaire seulement** (aucune mesure inventée ni pilotage matériel). Pour P0.01 certification, exiger un rapport de limites et d'écarts auditable.

## Conditions de sortie

`P0.00=CERTIFIED_GOVERNANCE_ONLY`  
`P0.01=IN_PROGRESS_DOCUMENTARY_ONLY`  
`INTEGRATED_DEPENDENCIES=0`  
`HARDWARE_CONNECTIONS=NONE`  
`PHYSICAL_MEASUREMENT=NOT_PERFORMED`  
`NEVER_SIMULATION=ENFORCED`  
`ZERO_COST_FOSS=ENFORCED`  
`BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`  
`PRODUCTION=NOT_AUTHORIZED`
