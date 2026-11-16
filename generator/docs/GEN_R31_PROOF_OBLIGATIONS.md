# FREQMED GEN-R31 — Matrice des obligations de preuve C11 / OS / fermeture

**Tous les contrôles ci-dessous sont `OPEN_NOT_PROVEN`.** L'absence d'appel physique et les tests statiques ne remplacent pas une validation OS/hardware indépendante.

| ID | Sévérité | Constat de code | Preuve encore requise |
|---|---|---|---|
| SH31_01 | CRITICAL | C31 tente `AudioQueueStop(...,true)` avant le retour admission occupée | Prouver la terminaison synchrone réelle et le chemin d'erreur OS |
| SH31_02 | CRITICAL | `AudioQueueStop` peut échouer ; quarantaine ≠ arrêt | Stratégie sûre si l'arrêt OS échoue, prouvée avant toute activation |
| SH31_03 | HIGH | Baux de callbacks encore actifs | Quiescence complète et propriété des buffers |
| SH31_04 | HIGH | Contrôleur appelle stop sur `ctx->queue` | Exclusivité des références et happens-before de tous les accès |
| SH31_05 | HIGH | Listener et `AudioQueueDispose` | États `OSStatus` échoués, callbacks déjà entrés et durée de vie OS |
| SH31_06 | HIGH | Userdata avant `try_enter` | Contrat de publication et exclusion des callbacks tardifs |
| SH31_07 | HIGH | `AudioQueueEnqueueBuffer` dans le verrou PCM | Réentrance, latence, absence de deadlock et preuve C11 |
| SH31_08 | HIGH | Conservations de file/contexte après erreur | Borne ressources, politique process-lifetime et sûreté physique |

## Conditions de progression

1. **R30 reste historique :** 12 constats ouverts (dont 2 critiques), aucun acquittement implicite.
2. **R31 prouve seulement une modification de l'ordre source :** aucune trace de CoreAudio réel, aucun statut d'OSStatus observé, aucune mesure physique, aucune simulation scientifique.
3. **Une mise en production est interdite.** Requiert une preuve indépendante de l'arrêt de sortie même après erreur, du contrat C11, et de la propriété complète des ressources ; faute de quoi abandonner le chemin d'émission.
4. **Témoin Mac Intel :** 617 tests Python, 33 C, 169 sources SHA-256, 24 rapports SHA-256 sont des cibles, non des résultats à anticiper.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
