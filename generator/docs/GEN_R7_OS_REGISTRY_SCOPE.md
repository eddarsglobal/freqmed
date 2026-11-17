# GEN-R7 — Périmètre IOKit et classes USB

L'inventaire est construit à partir de registres réellement présents sur le Mac. Aucun fichier de résultats n'est généré avant le lancement du mode `em-discover` sur la machine réelle. Il n'existe pas de simulateur, fixture de matériel, échantillon d'onde, commande de port ou pilote d'émission.

- `IOUSBHostDevice` : nombre d'entrées USB hôte enregistrées par IOKit ; ne désigne pas uniquement des générateurs ni même des instruments.
- `IOUSBHostInterface` : nombre d'interfaces USB hôte ; une interface FEh/03h/protocol 00h ou 01h est reconnue comme **signature de classe USB Test and Measurement (USBTMC/USB488)**, pas comme preuve d'un générateur EM.
- `IOSerialBSDClient` : compte les services dont `IOCalloutDevice` est un chemin de forme `/dev/cu.*` ; les chemins sont lus puis effacés de l'état retourné (compteur uniquement). Un port Bluetooth ou virtuel reste possible.
- Périphériques USBTMC éventuellement observés : identifiants **génériques** fabricant/produit et protocole de l'interface, pas de numéro de série, pas d'identifiant propriétaire de machine.
- Inventaire borné à 4 096 entrées par classe et à 24 interfaces USBTMC affichées. Toute erreur d'énumération produit un statut « indisponible » plutôt qu'un faux zéro. Le dépassement des 24 candidats est marqué comme tronqué.
- L'absence de candidat n'établit pas qu'aucune source EM ne peut exister : certains appareils utilisent Ethernet, un protocole fabricant ou une interface non visible ici.

Références de spécifications publiques :
- USB-IF, Defined Class Codes : https://usb.org/defined-class-codes (FEh/03h/00h et FEh/03h/01h).
- Apple Developer, IOServiceGetMatchingServices : https://developer.apple.com/documentation/iokit/1514494-ioservicegetmatchingservices

Les API CoreAudio et IOKit font partie des composants propriétaires du système macOS ; aucun pilote ou module tiers payant n'est installé.

Ne pas confondre interface système détectée, générateur électromagnétique disponible, équipement qualifié et autorisation d'émettre. Pour le moment, seul le premier niveau est réalisé.
