# GEN-R12 — Contrat EM non régressé : qualification matérielle indisponible

Le générateur EM reste en développement documentaire sans activation physique.

- GEN-R7 : inventaire IOKit réel fourni par le propriétaire : 10 périphériques USB, 23 interfaces, 4 services série, 0 interfaces USBTMC. Aucune de ces observations ne certifie un instrument.
- GEN-R11 : contrôles sur la **forme** des dossiers fabricant/modèle/protocole/coupure indépendante/métrologie; résultat possible `PRESENT_UNVERIFIED` et jamais `AUTHORIZED`.
- GEN-R12 : les tests vérifient que cette qualification reste non autorisante, et que `em_backend.c` refuse toujours toute commande.
- Aucun protocole de commande universel, port série, périphérique RF ou appareil fictif n'est introduit.

Une décision future exige du matériel réellement identifié, un dossier constructeur réutilisable légalement, une interface contrôlable, des conditions de sûreté certifiées par le Bureau et une mesure physique indépendante dans un banc non biologique autorisé. Le code n'effectue aucune émission.

`EM_HARDWARE_QUALIFIED=NO` · `EM_OUTPUT=LOCKED` · `NEVER_SIMULATION=ENFORCED` · `PRODUCTION=NOT_AUTHORIZED`.
