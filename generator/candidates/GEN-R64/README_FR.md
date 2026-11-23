# FREQMED — GEN-R64 : cohérence des états et contrôle numérique PCM

**v0.8.1**, Mac Intel — candidat préparatoire non émetteur, rattaché uniquement aux travaux logiciels **P1.01/P1.02**, conformément à la clause E de RoadMap.md. **P0.01 non certifié ; P0.02 en attente.**

## Fonctionnalités réellement développées

1. **États natifs cohérents avant association** : une simple sélection de sortie ou une validation de commande ne transforme plus le bail R60 `UNBOUND` en `REVOKED`, ni l'UID R62 `UNBOUND` en `INVALIDATED`. Dès qu'une session active R59/R60/R62 existe, une nouvelle sélection/commande invalide réellement le contrat, efface l'UID et révoque le bail. Un STOP opérateur reste `STOPPED` jusqu'à la reprise explicite autorisée du moniteur. Le défaut R61 mémorisé n'est jamais acquitté automatiquement.
2. **Intégrité numérique C11 des blocs PCM** : nouveau module `native/acoustic_integrity_r64.c/.h`, sans CoreAudio playback, qui lit le tampon déjà calculé par GEN-R63 et exige l'absence de NaN/Inf, niveaux numériques au plus 0,01, canaux mono/stéréo, tampon de durée bornée et **zéro sur les premiers/derniers échantillons de chaque canal**. Une erreur refuse la publication du bilan. Le tampon est **toujours** remis à zéro par GEN-R63 en `finally`, même en cas de refus R64 ; aucune donnée PCM n'est renvoyée en HTTP.
3. **UI 10 langues** : « Validation C de commande » est identifiée comme une action **indépendante** de « Préparation PCM ». Le résultat PCM indique aussi « enveloppe numérique vérifiée ». Le texte STOP reste masqué au repos ; la direction Windows/macOS et le choix libre du périphérique sont conservés.
4. **Lanceur Mac** : correctif des marqueurs R62/R63 initialement concaténés dans le script R63 ; tous les marqueurs distincts en R64.

**Important** : les données PCM sont de vraies **consignes numériques calculées**, **pas des mesures physiques** ni une simulation scientifique. Le plafond numérique 0,01 ne prouve aucune sûreté acoustique ou limite SPL. Aucune onde sonore/EM n'est produite, aucun AudioQueue n'est disponible, aucun instrument EM qualifié. `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`.

## Installation Mac Intel

Installer le ZIP exact sous `~/Downloads`, vérifier son SHA-256 externe et exécuter :

```bash
FREQMED_R58_FETCH_PINNED_GITHUB=YES bash RUN_GEN_R64_MAC_INTEL.command
```

Le lanceur vérifie les tests avant de démarrer le serveur Safari localhost. Sur Mac, les tests et le lien natif CoreAudio doivent réussir avant toute qualification fonctionnelle ; aucune absence de son ne vaut certification physique.

## Parcours témoin proposé

1. **Au lancement** : R60 NON LIÉ, R62 NON LIÉE, surveillance EN ATTENTE, compteur 0, aucune émission.
2. **Après sélection explicite des Haut-parleurs MacBook Pro** : surveillance OS LIVE, R60/R62 **toujours NON LIÉS** tant qu'aucune session C n'est liée. Il s'agit de la principale correction UX/native R64.
3. **Après association 440 Hz / 500 ms / 0,01** : R59 lié, R60 confirmé, R61 NORMAL, R62 UID OS confirmé.
4. **Après un clic Préparer le flux numérique** : 22050 trames × 2 canaux = 44100 échantillons, **enveloppe numérique vérifiée**, mémoire effacée, sortie HARD_DENIED.
5. **Après STOP** : route libérée, session non liée, R60/R61/R62 ARRÊTÉ(S), moniteur STOPPED, préparation refusée sans nouvelle route.

## GitHub

Le script `SYNC_R64_GITHUB_MAC_INTEL.command` synchronise le kit complet dans **un worktree Git distinct** sur la branche candidate `candidate/gen-r64-integrity-20261123` ; il n'efface ni ne fusionne le `main` local. Le code préparatoire est proposé uniquement via PR DRAFT, sans autorisation de fusion tant que RoadMap/Bureau n'ont pas qualifié les étapes requises.
