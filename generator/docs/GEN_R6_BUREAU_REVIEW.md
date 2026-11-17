# FREQMED GEN-R6 — Document de travail pour le Bureau (NON CERTIFIÉ)

Objet : fondations d'un générateur électromagnétique commandant un **instrument physique distinct**, et non un lecteur de relevés ou une simulation.

B05 — Le contrat distingue l'interface série/USBTMC et les unités de consigne (V RMS, A RMS, dBm), mais ne suppose aucun protocole universel. Le futur équipement doit être identifié physiquement ; bande, unité réellement contrôlée, régime du signal, limites techniques, lois RF/EMC et conditions de banc devront être établis.

B09 — Le code C refuse les valeurs non finies, intervalles incohérents, unités incompatibles, identités non formatées et durées hors profil. Un identifiant SHA-256 textuel n'est pas une preuve de possession de l'instrument. Le module n'ouvre aucun port et son entrée d'émission retourne toujours -1, indépendamment des valeurs reçues. Le binaire livré n'intègre pas le module de commande EM.

B10 — Le futur pilote devra vérifier l'état matériel OFF et disposer d'une coupure de sécurité indépendante. Le code R6 ne permet aucune activation ; le contrôle des plages de consigne, même correctement implanté, ne prouve pas la sécurité d'un champ magnétique, électrique ou RF.

B04/B07 — Le backend acoustique R5 est conservé sans changement et sans émission. Le programme de vérification reste incapable d'enclencher AudioQueue.

**Décisions exigées avant pilote physique :** choix d'un équipement réel, preuves de fonctionnement, manuel de protocole, scénario de sortie non biologique autorisé, limites certifiées, coupure matérielle indépendante, vérification par mesure physique indépendante et revue réglementaire. Aucun partenariat fabricant obligatoire.

**État proposé : GEN-R6_CANDIDATE_CODE_READY_FOR_MAC_REVIEW ; CERTIFICATION_BUREAU=NOT_RECEIVED ; OUTPUT=BLOCKED.**
