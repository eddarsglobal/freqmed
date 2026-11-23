# GEN-R63 — Réalisation et provenance

Source parent exacte : `FREQMED_GEN_R62_FIX2_IDLE_STOP_CLARITY_MAC_INTEL_20261123.zip`, SHA256 `98e7c625af30ba207b72dcac2cfd63893a78ebb5376c3dc031cdf547b3417404`.

RoadMap officielle `eddarsglobal/freqmed/README.md` / `RoadMap.md` ; développement préparatoire de P1.01/P1.02, G0 non certifié. Aucun changement des modules C antérieurs ; nouveau module numérique à sortie mémoire uniquement. Licence source Apache-2.0. GitHub main non fusionné ; ne pas requalifier comme produit physique.

Le code actuel rend une première fenêtre numérique **transitoire** via C11, et la détruit ; tout espoir de lire des Hz physiques nécessite plus tard un matériel qualifié et une métrologie indépendante.
