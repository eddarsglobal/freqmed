# FREQMED — GEN-R65 : génération PCM numérique segmentée, sans émission

**Version 0.9.0 · Candidat de développement Mac Intel**. Préparation de P1.01 (Frequency Command Core) / P1.02 (Acoustic Physical Generator), conformément à la clause E de la RoadMap normative du dépôt. **P0.01 reste IN_PROGRESS_REBASE_REVIEW, P0.02 reste PENDING ; aucun jalon futur n'est certifié.**

## Nouveau fonctionnement technique

GEN-R63 produit et efface une consigne PCM complète ; GEN-R64 en vérifie numériquement les bornes et les extrémités. **GEN-R65 introduit une seconde voie, par segments**, qui laisse l'ancienne voie R63/R64 accessible dans l'interface pour vérifier l'équivalence :

- Un nouveau module C11 `native/acoustic_segment_r65.c/.h` émet des **échantillons numériques en RAM, jamais vers des haut-parleurs**. La consigne est divisée en segments de **256 trames au maximum**, avec un tampon fixe de 256 × 1 ou 256 × 2 nombres `float32` (2 KiB en stéréo), quelle que soit la durée totale autorisée.
- Un curseur C typé garde en mémoire la route et la commande **exactes** au début du calcul. Toute modification avant le segment suivant est refusée (session R59, device ID, nom, canaux, taux, fréquence, niveau, durée, nombre de trames). Les indices de segment doivent être contigus, ordonnés et exhaustifs ; le dernier segment est correctement tronqué.
- Le code C numérique vérifie les valeurs finies, la borne numérique et les trames extrêmes nulles. **Chaque tampon est effacé dans un bloc `finally`**, y compris en cas d'erreur ; le curseur C est également effacé en fin de traitement. Aucun tampon PCM, UID privé ou waveform n'est retourné à Safari, ni écrit sur disque.
- L'API authentifiée `POST /api/acoustic/pcm/prepare-segmented` exige les protections déjà en place : sortie CoreAudio réelle explicitement sélectionnée, R58 source-only isolé, R59 associé, R60 valide, R61 sans défaut et R62 UID vérifié. Avant **et après** le calcul numérique, la route réelle et le bail sont de nouveau vérifiés sous verrou logiciel ; aucun « PASS » ne peut être publié si ces contrôles échouent.
- Le bouton **« Préparer par blocs bornés · R65 »** est dans le panneau PCM existant, sans nouvel écran. Les dix langues sont conservées, et les contrôles R63/R64 précédents ne sont pas désactivés.

La préparation « segmentée » ne constitue pas une génération de son physique. Le niveau numérique 0,01 n'est pas un niveau de pression acoustique ni une limite de sûreté. Le `with self.lock` pendant le calcul ne représente pas un arrêt matériel indépendant : aucune sortie physique n'est disponible.

## Exemple vérifiable

Commande 440 Hz / 500 ms / niveau numérique 0,01 à 44 100 Hz, 2 canaux : **22 050 trames, 44 100 valeurs numériques, 87 segments** (86 × 256 + 34), tampon maximal **512 échantillons float32 / 2 048 octets**, ensuite effacé. La comparaison des valeurs C R65 avec C R63 est une vérification d'équivalence **numérique**, pas une simulation de mesure physique.

## Lancer sur Mac Intel

Vérifier SHA256 du ZIP externe reçu et l'extraire dans `~/Downloads`, puis :

```bash
FREQMED_R58_FETCH_PINNED_GITHUB=YES bash RUN_GEN_R65_MAC_INTEL.command
```

Le lanceur exécute une suite de **20 modules unittest isolés** puis démarre le serveur localhost. L'archive contient aussi `SYNC_R65_GITHUB_MAC_INTEL.command` pour préparer un worktree Git détaché et pousser uniquement la branche candidate GEN-R65, sans toucher au `main` de ton Mac.

**Précondition Mac** : `clang` Apple, Python 3, CoreAudio natif et source historique R58 disponible par empreintes épinglées. Ne jamais utiliser de données fabriquées pour valider le matériel.

## Parcours de vérification Safari (zéro émission)

1. Au lancement : sortie non sélectionnée, compteur 0, R65 « Aucun bloc R65 préparé ».
2. Sélectionner explicitement les Haut-parleurs MacBook Pro ; associer la commande numérique 440/500/0,01 ; vérifier R59–R62, sans demande de playback.
3. Cliquer sur **« Préparer par blocs bornés · R65 »** : si le matériel CoreAudio/UID et le bail sont confirmés, le bilan indiquera **22 050 trames / 2 canaux / 87 blocs / tous effacés** et `PHYSICAL OUTPUT: HARD_DENIED`.
4. Cliquer STOP ; vérifier route et session effacées, moniteur STOPPED, aucune émission. La préparation doit refuser un appel sans route active.

## Gouvernance

- `ZERO_COST_FOSS=ENFORCED`, cœur C et Python Apache-2.0, API CoreAudio Apple = **dépendance plateforme propriétaire explicitée**, pas un SDK payant imposé.
- `NEVER_SIMULATION=ENFORCED` (tests de structures C numériques uniquement, pas de faux appareils/mesures).
- `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
- B07 acoustique/DSP : équivalence numérique et enveloppe. B08 logiciel : déterminisme et ressources bornées. B09 sécurité/UX : états et API locale. B10 sûreté : défauts, zéro émission, fail-closed. B04 métrologie : **NOT_EVALUATED**. Ces fonctions ne sont pas des signatures de certification.
