# FREQMED GEN-R32 — Failure-case matrix, C11 ownership vs CoreAudio OSStatus

Cette matrice est **une liste d'obligations de revue**, non un jeu de tests simulés ni une qualification de matériels. Aucun cas OS en échec n'a été réellement déclenché.

| Incident | État que C31 peut constater | Ce que C31 ne démontre PAS | Obligation avant activation |
|---|---|---|---|
| Stop immédiat `noErr` | Appel d'arrêt synchrone déclaré réussi | Mesure de sortie physique nulle et absence de tous callbacks tardifs | Qualifier contrat OS, acquisitions de leases et mesure réelle indépendante |
| Stop immédiat `OSStatus != noErr` | Défaut, quarantaine, retour -1, file conservée | Arrêt physique, état/validité de queue, fin des callbacks | Confinement matériel indépendant et modèle exact de propriété OS |
| Portail fermé mais leases actives | Aucun nouvel accès admis par le gate | Absence d'entrées OS pouvant lire userdata avant le gate | Quiescence OS et durée de vie userdata |
| Retrait listener échoué | Flag `listener_remove_failed`, faute enregistrée | Fin des listeners déjà entrés | Revue des contrats d'erreur du retrait, arrêt et disposition |
| Dispose `OSStatus != noErr` | Référence C retenue, faute enregistrée | Validité physique de la référence C et ressources réellement détenues | Contrat post-échec et traitement des callback buffers |
| PCM enqueue sous verrou | `pcm_writer_gate` et gardeurs logiciels | Non-réentrance et temps réel borné | Preuve de concurrence, ordonnanceur et latence |
| Arrêt de processus ou quarantaine | Pas de nouveau travail admis dans le processus, selon code | Extinction physique de sorties externes ou partagées | Stratégie indépendante d'arrêt et d'alerte sans activation |

## Classification rigoureuse des preuves

- **OBSERVED_SOURCE** : présence et ordre de segments dans le candidat C31 épinglé SHA-256.
- **SOFTWARE_COMPILED_UNLINKED** : vérification compilateur sans lancement de l'objet audio.
- **OS_RUNTIME_FAILED_STOP** : **NOT_TESTED**.
- **C11_RACE_FREEDOM** : **NOT_PROVEN**.
- **PHYSICAL_OUTPUT_CUTOFF** : **NOT_PROVEN** ; aucun instrument de qualification disponible dans cette phase.
- **BUREAU_INDEPENDENT_SIGNATURE** : **NONE**.

Ne pas utiliser de génération de signal, simulation, callback actif ni activation physique pour acquitter artificiellement les preuves.

Sources de contrôle : https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29 et https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29 .

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
