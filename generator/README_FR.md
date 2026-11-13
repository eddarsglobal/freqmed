# FREQMED GEN-R6 — Fondations logicielles du générateur électromagnétique

**Mission principale : produire, à terme, des fréquences physiques acoustiques et électromagnétiques à l'aide de matériels réels adaptés.** Le Bureau de la RoadMap définit et certifie les exigences scientifiques et de sécurité. Le design Windows 11 × macOS est conservé.

**AUCUNE ÉMISSION PHYSIQUE dans GEN-R6.** Ni le nouveau module EM ni le programme livré n'ouvrent de matériel, ne produisent de champs, ne génèrent d'ondes ou ne pilotent de radio. Il n'y a aucune simulation scientifique.

## Vrai développement GEN-R6

Le nouvel élément `src/em_device_contract.h/.c` définit un contrat de contrôle d'un générateur **physique identifié** : empreinte SHA-256 de son identité (forme seulement), transport série ou USBTMC, unité de sortie (tension efficace V RMS, courant efficace A RMS, ou puissance conduite dBm), limites minimales et maximales de fréquence et de commande, durée maximale autorisée par le profil, ainsi qu'un ensemble de refus stricts pour toute incohérence.

Ces limites doivent provenir de la qualification **d'un équipement réel**, jamais d'une valeur dite « sûre » universelle. Aucune marque ou partenariat commercial n'est obligatoire. Le code ne considère **jamais** qu'un fichier de profil ou une empreinte saisis par l'utilisateur prouvent l'existence, la conformité ou la sécurité d'un dispositif.

`src/em_instrument_driver_abi.h` spécifie les responsabilités d'un futur pilote **spécifique au matériel** : identification par lecture seule, vérification de l'état matériel OFF et coupure matérielle. Aucune commande d'activation, aucun protocole SCPI inventé, et aucun pilote réel ne sont intégrés ici. Le programme public maintient le refus de toute sortie EM.

**Important :** le contrat est un module de validation de commandes, et non un simulateur de générateur ni un générateur EM déjà opérationnel. Le raccordement physique attend l'identification d'un appareil, son protocole documenté, des contrôles indépendants et une décision du Bureau.

## État des deux générateurs

- **Acoustique :** les sources CoreAudio R5, la fixation explicite du périphérique et la surveillance de route sont conservées, sans modification. Trois objets compilés mais **jamais liés** dans le programme exécutable. R5 a obtenu 90/90 tests PASS sur le Mac Intel du propriétaire.
- **Électromagnétique :** nouveau contrat logiciel C compilé et testé, mais aucune source EM, aucun transducteur, appareil ou interface de sortie qualifiés. Le programme bloque toujours l'émission.

## Mac Intel — contrôle sans sortie

`bash RUN_GEN_R6_MAC_INTEL.command selftest`

`bash RUN_GEN_R6_MAC_INTEL.command probe` (optionnel, lecture seule de la sortie audio du Mac ; ne produit aucune fréquence).

Le lanceur vérifie toutes les empreintes SHA-256, compile les trois objets acoustiques et le module EM, exécute les assertions C et la suite Python, vérifie les symboles du binaire. Sans émetteur ni microphone.

Code projet sous Apache-2.0, sans dépendance externe au C et à la bibliothèque standard Python. Le framework CoreAudio est une dépendance propriétaire native du système macOS et n'est pas présenté comme du FOSS.

**Bureau demandé :** B05 pour la nature et le protocole de l'appareil EM, B09 pour la sûreté du pilote et les tests, B10 pour les interverrouillages matériels et la conformité applicable ; B04/B07 pour la chaîne acoustique.

**NEVER_SIMULATION=ENFORCED · ACOUSTIC_OUTPUT=NOT_AUTHORIZED · EM_OUTPUT=NOT_AUTHORIZED · BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED · PRODUCTION=NOT_AUTHORIZED.**
