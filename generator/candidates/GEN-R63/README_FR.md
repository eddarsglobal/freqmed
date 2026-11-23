# FREQMED GEN-R63 — moteur PCM numérique borné (sans émission)

Version **v0.8.0**. Développement préparatoire en référence à RoadMap.md / P1.01–P1.02 ; aucune certification ni émission autorisée.

**NOUVEAU :** un module C11 `native/acoustic_pcm_r63.c` qui calcule un bloc PCM float32 numérique mono/stéréo transitoire à partir d'une session réellement liée à CoreAudio. Garde native : session R59, bail R60 valide, défaut R61 absent, identité CoreAudio R62 relue, backend historique R58 toujours isolé. Arrêt immédiat si un prérequis échoue.

- Durée digitale max **1 s** ; 96 000 frames / 2 canaux ; niveau numérique borné à **0,01** (ceci n'est **PAS** une limite de pression acoustique ou de sûreté physique) ; fréquence digitale plafonnée par Nyquist (marge) ; fenêtres progressives de 5 ms.
- Le buffer PCM est **entièrement effacé en C avant la réponse HTTP**. Aucun fichier son/WAV, aucune lecture CoreAudio, aucun AudioQueue, aucune donnée PCM rendue à Safari.
- API locale authentifiée : `POST /api/acoustic/pcm/prepare` avec `{}` ; retourne uniquement le bilan **digital**, pas des mesures acoustiques.
- UX : texte STOP masqué lorsqu'il n'y a aucun bouton STOP, et panneau produit compact « Préparer le flux numérique ».

**Jamais de simulation scientifique :** la génération numérique est un vrai calcul de futurs échantillons de commande ; aucune sortie ni mesure physique prétendue. `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`.

## Mac Intel

```
FREQMED_R58_FETCH_PINNED_GITHUB=YES bash RUN_GEN_R63_MAC_INTEL.command
```

Mac a besoin de Python3, clang, sources exactes R58 locales ou récupération volontaire via gh. Tests Linux n'attestent pas Apple CoreAudio ; première qualification R63 sur Mac attendue.
