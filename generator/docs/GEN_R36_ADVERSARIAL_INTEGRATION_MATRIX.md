# FREQMED GEN-R36 — Static Anchor Integration / Adversarial Proof Matrix

**NONEXECUTABLE DESIGN MATRIX — aucun callback CoreAudio, aucun interleaving simulé.**

| Cas / menace | Containment candidat R36 | Preuve encore nécessaire |
|---|---|---|
| Entrée tardive avec `userdata` valide | Adresse statique `&fm36_anchor` jamais libérée | Intégration réelle des deux callbacks et conformité de l'ABI OS |
| `ctx` déjà libéré par un autre alias | R36 ne libère pas `owner` | Analyse exhaustive des alias et de tous les chemins `free` hors R36 |
| Callback pré-admission au moment de `seal` | Phase atomique, seconde lecture et compteur | Preuve C11 d'absence d'UAF de `owner` et de sortie bornée |
| Deux callbacks admis simultanément | `atomic_uint admitted` | Appariement `enter/leave`, interdiction d'un double leave et preuve de publication |
| Réutilisation de l'adresse / ABA | Slot singleton non réutilisable avec `atomic_flag` | Politique de cycle de vie et refus après première revendication |
| Erreur de création de queue | Politique de conservation propriétaire | Contrat OS de publication partielle et de callbacks |
| Stop OS en échec | Phase SEALED peut refuser nouveaux admissions | **Arrêt matériel et OS non démontrés**, politique indépendante requise |
| Dispose OS en échec | Owner non libéré et ancre permanente | Validité handle, callbacks tardifs, ressource OS retenue |
| Listener encore actif | Ancre identique stable en futur raccordement | Preuve OS de fin de tous callbacks et conformité des arguments de retrait |
| Binaire exécutable lié par erreur au candidat | Runner contrôle allowlist et symboles `nm` | Validation indépendante de la chaîne de distribution |
| Dépassement de capacité singleton | Refus fail-closed | Aucune réouverture, fallback de heap non contrôlé ou réutilisation |
| Émission acoustique/EM physique | Aucune fonctionnalité de sortie dans R36 | Qualification instrumentale réelle future, **pas autorisée à ce stade** |

## Évidence et classification

- `SOURCE_PRESENT` : présence et ordre des ancrages dans les sources GitHub SHA-pinnées.
- `C11_OBJECT_COMPILED_UNLINKED` : compilation isolée, pas d'exécution du module.
- `R36_INTEGRATED_IN_CALLBACK=NO` : les callbacks existants passent toujours `ctx`, donc aucune correction réelle de leur durée de vie n'est revendiquée.
- `OS_CALLBACK_LIFETIME=NOT_PROVEN` ; `C11_RACE_FREEDOM=NOT_PROVEN` ; `PHYSICAL_STOP=NOT_PROVEN` ; `BUREAU_CERTIFICATION=PENDING`.

Le dossier R36 ne doit pas être traité comme une certification de qualité acoustique, un dispositif médical ou une démonstration de sûreté d'exposition.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
