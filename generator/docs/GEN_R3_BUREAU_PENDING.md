# GEN-R3 — Revue du Bureau, aucune certification
B04 : transducteur, pression acoustique réelle, chaîne d'étalonnage non qualifiés. Les 2 canaux et 44 100 Hz constatés par macOS ne sont que des métadonnées OS.
B05 : aucun équipement EM qualifié, aucune émission EM ni pilote opérationnel.
B07 : le code candidat suit la cadence nominale observée plutôt qu'une constante 48 kHz; fréquence physique, distorsion et stabilité non mesurées.
B09 : compilation de source AudioQueue en objet isolé; seul un exécutable sans API de démarrage audio est accessible. Audit nm en blocage strict.
B10 : sortie OFF; aucune autorisation d'émission, aucune coupure matérielle indépendante, aucune exposition biologique.
Risques ouverts : sélection et fixation du périphérique physique, changements dynamiques, arrêt matériel indépendant, niveau réel, conformité EM/radio.
VERDICT=REVIEW_REQUIRED; EMISSIONS=NONE; CERTIFICATION=NONE.
