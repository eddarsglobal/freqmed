# Bureau FREQMED — GEN-R63 / candidate numérique non émetteur

Date : 23 novembre 2026 ; RoadMap référence : `eddarsglobal/freqmed/main/RoadMap.md`.

**B07 / DSP** — calcul numérique réel PCM float32, fenêtres de démarrage/fin, fréquence sous Nyquist, 1 s et 96 000 trames maximum ; les sorties ne constituent pas des mesures physiques. Contrôle logiciel Linux PASS, métrologie physique NOT PERFORMED.

**B09 / sécurité logiciel & UX** — le bloc transitoire est limité, effacé avant résultat, aucune donnée de signal dans HTTP ; session R59 et bail R60 + UID R62 + défaut R61 requis ; STOP contextualisé et ancienne aide masquée en IDLE. Contrôle logiciel Linux PASS ; Safari/macOS EN ATTENTE.

**B10 / sûreté** — interdiction physique inchangée, aucun démarrage audio/RF, pas de valeur de pression acoustique calculée à partir du niveau numérique, aucun interlock physique qualifié. Résultat : REMAIN BLOCKED pour les sorties.

**B04 / métrologie** — aucun banc, capteur ou étalonnage ; verdict NON ÉVALUÉ.

Ces mentions classent des vérifications effectuées par le modèle, **pas des certifications indépendantes signées**. `P0.01 IN_PROGRESS_REBASE_REVIEW`, `P0.02 PENDING`, `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`, `NEVER_SIMULATION=ENFORCED`.

Dépôt distant candidat : `candidate/gen-r63-digital-pcm-20261123` ; PR DRAFT #22. **Deux fichiers C + README seulement publiés jusqu'à la synchronisation du kit complet sur Mac.** Ne pas fusionner cette branche dans main avant qualification et réconciliation de provenance.
