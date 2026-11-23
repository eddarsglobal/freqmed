# Bureau FREQMED — GEN-R64 : dossier candidat (23 novembre 2026)

## Objet
Corriger la sémantique des **états réels C** avant première liaison et ajouter une barrière de vérification **numérique** entre le calcul PCM GEN-R63 et le bilan HTTP, sans générer d'onde physique ni remplacer la métrologie indépendante.

## Tests et fonctions
- **B07 DSP** : inspecter l'enveloppe numérique, la borne maximale normalisée, le début/fin à zéro par canal, les cas non finis ; aucune prétention de pression acoustique.
- **B08 logiciel scientifique** : vérifier cohérence trames/échantillons et refus des données invalides ; le PCM numérique n'est pas une observation expérimentale.
- **B09 architecture/UX** : états natifs R60/R62 conservent UNBOUND au premier usage, STOP sticky ; libellés de validation C distincts du compte rendu PCM, 10 langues et RTL ; UID non exposé.
- **B10 sûreté** : statut R61 et STOP fail-closed, effacement natif avant réponse HTTP même sur échec, aucun AudioQueue/driver d'émission, plafond 0,01 numérique non qualifiant.
- **B04 métrologie** : NOT_EVALUATED, aucun banc acoustique, transducteur certifié ni coupure physique attestés.

Ces vérifications sont des **contrôles de développement**, pas des certificats ou avis signés d'experts indépendants. **Statuts P0.01/P0.02 inchangés.**

## Preuves de développement
Voir `tests/test_r64.py`, tous les tests hérités et `SHA256SUMS.txt`. Les tests logiciels doivent passer sur une extraction ZIP neuve ; le relevé macOS Intel, la liaison Apple et le parcours Safari sont des preuves ultérieures distinctes.

## Interdictions persistantes
`REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`, `NEVER_SIMULATION=ENFORCED`. `main` non modifié, PR DRAFT non fusionnée.
