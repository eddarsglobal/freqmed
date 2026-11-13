# FREQMED GEN-R7 — Découverte du matériel électromagnétique (sans émission)

**Mission principale : développer des générateurs physiques de fréquences acoustiques et électromagnétiques, sous certification du Bureau.** Pas de simulation, pas de lecteur CSV prioritaire. Direction graphique approuvée Windows 11 × macOS maintenue et dix langues prévues.

**AUCUNE ÉMISSION PHYSIQUE dans GEN-R7.** La source de sortie acoustique et le contrat de commande EM sont conservés. Il n'existe toujours aucun pilote EM d'émission autorisé. Le binaire exécutable ne contient pas de fonctions AudioQueue de démarrage ni de fonction d'écriture vers un appareil. Tous les modes d'émission restent refusés.

## Nouveau développement

- `src/em_hardware_discovery_macos.c` : **interroge réellement** le registre IOKit macOS, en lecture seule, pour recenser les périphériques `IOUSBHostDevice`, les interfaces `IOUSBHostInterface` et les services `IOSerialBSDClient` dotés de nœuds d'appel `/dev/cu.*`.
- Il reconnaît uniquement les interfaces déclarant par des descripteurs USB la **classe FE / sous-classe 03, protocoles 00/01**, correspondant à USB Test and Measurement Class (USBTMC / USB488). Ce sont des descriptions de matériel, **pas** une preuve qu'un appareil est un générateur EM ni une qualification de sécurité.
- La sortie fournit des nombres réels et, uniquement pour les interfaces USBTMC repérées, les identifiants fabricant/produit numériques et le protocole quand le registre les expose. Les ports série sont **comptés sans afficher les noms ni les identifiants uniques**. Aucun port n'est ouvert et aucun transfert USB, commande SCPI, émission RF ni son n'est exécuté.
- Un recensement incomplet est signalé `UNAVAILABLE_OR_INCOMPLETE` avec nombres inconnus, et non maquillé en « zéro appareil ».

## Vérification Mac Intel

- `bash RUN_GEN_R7_MAC_INTEL.command selftest` : contrôle SHA-256, compilation native stricte, tests des composants, 22 assertions C du contrat EM R6, 11 assertions sur les codes USBTMC, suite Python et audit `nm` ; ne produit aucune sortie.
- `bash RUN_GEN_R7_MAC_INTEL.command em-discover` : **interroge le matériel réellement présent** par IOKit en lecture seule ; ne prétend pas qu'un port ou une interface correspond nécessairement à une machine de génération.
- `bash RUN_GEN_R7_MAC_INTEL.command probe` : lecture seule de la sortie audio par défaut, déjà validée en R6 (2 canaux, 44 100 Hz nominaux sur le Mac du propriétaire).

**GEN-R6 sur Mac Intel :** 111/111 tests Python PASS, 22/22 assertions C PASS, compilation stricte et audit natif PASS. Pas d'émission acoustique/EM. **GEN-R7 : qualification native sur Mac Intel encore à effectuer.**

## Bureau et suites

B05/B06 : examiner les classes physiques réellement observées et distinguer ports série, USBTMC et générateur EM disponible ; n'inventer aucun instrument. B09 : vérifier IOKit et permissions lecture seule. B10 : ne jamais convertir ce recensement en autorisation d'émission. La prochaine étape de pilote EM dépend de la présence d'un appareil vérifiable et de son protocole documenté. Aucun fabricant ou abonnement payant obligatoire.

**`NEVER_SIMULATION=ENFORCED` · `ACOUSTIC_OUTPUT=BLOCKED` · `EM_OUTPUT=BLOCKED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.**

Licence projet Apache-2.0 ; CoreAudio et IOKit sont des API système Apple propriétaires de plateforme, sans coût logiciel additionnel.
