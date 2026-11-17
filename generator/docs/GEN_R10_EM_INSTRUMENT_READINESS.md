# GEN-R10 — Prérequis du générateur EM (documentation, aucune émission)

L'inventaire IOKit réel GEN-R7 (10 périphériques USB, 23 interfaces, 4 nœuds série, 0 USBTMC) ne permet de qualifier **aucun** générateur EM. Les ports série déclarés ne prouvent pas un instrument ou un protocole.

Une intégration future exige au minimum l'identification documentée du modèle matériel exact, une interface réellement disponible, un protocole officiel du constructeur, des droits compatibles avec le logiciel libre, des limites matérielles vérifiées, un dispositif physique d'arrêt indépendant, un protocole de mesure avec étalonnage et un accord préalable du Bureau pour un banc non biologique. Les radios du Mac ne sont pas des émetteurs universels arbitraires.

En R10, aucune commande EM n'est envoyée, aucun port ouvert et aucun appareil fictif ou protocole supposé n'est introduit. `EM_OUTPUT=BLOCKED_NO_QUALIFIED_EM_DEVICE` ; `NEVER_SIMULATION=ENFORCED` ; `PRODUCTION=NOT_AUTHORIZED`.
