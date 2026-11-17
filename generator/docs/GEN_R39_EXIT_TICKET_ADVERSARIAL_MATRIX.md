# FREQMED GEN-R39 — Atomic Completion Ticket, Owner Alias & OS Failure Matrix

**Candidat source C11, aucune simulation d'interleavings ni callback OS exécuté.**

| Menace / question | Garde C39 visible | Limitation probatoire |
|---|---|---|
| Réutilisation de ticket | CAS `UNUSED→RESERVING` | La copie/réinitialisation externe n'est pas empêchée |
| Owner accessible avant admission | `fm36_try_enter` avant stockage | La validité réelle de owner relève des alias externes |
| Publication du ticket | Écritures `owner/userdata` puis `ACTIVE` release | Ne synchronise pas les autres données C31 non atomiques |
| Lecture d'owner | `ACTIVE` acquire | La mémoire doit rester vivante indépendamment |
| Admission rejetée | `REJECTED` et éventuelle sortie compensatrice | Erreurs de `fm36_leave` restent ouvertes |
| Deux sorties concurrentes du même ticket | CAS `ACTIVE→FINISHED` | **Au plus une**, seulement si ticket mémoire vivant |
| Oubli total de sortie | Aucun mécanisme extérieur de réclamation | **Exactly-once non démontré** |
| Ticket copié sur une autre pile | Aucun contrôle d'alias C global | Peut rompre l'exclusivité |
| `fm36_leave` échoue | Erreur retournée, FINISHED reste terminal | Compteur global et fin réelle non validés |
| `owner` libéré ailleurs | Aucun `free` dans C39 | Absence de `free` externe non prouvée |
| Callback output réel | C31 utilise `ctx` | C39 n'est pas raccordé à CoreAudio |
| Listener réel | C31 utilise `ctx` | C39 n'est pas raccordé à CoreAudio |
| Stop OS échoué | Aucun appel CoreAudio C39 | Quiescence et coupure physiques inconnues |
| Dispose OS échoué | Conservation contractuelle du propriétaire | Aucune postcondition de succès acquise |
| `seal` alors que callbacks entrent | `fm36_seal` ferme l'admission | Ne démontre pas terminaison OS |
| Liaison involontaire | `clang -c` et allowlist `nm` | La livraison réelle reste hors périmètre |
| Révision de preuves | SHA source + R16–R38 recalculés | Aucun théorème de concurrence formelle |
| Mesure médicale/physique | Aucune activité physique dans la chaîne | Aucune certification, aucun essai biologique |

### Mutations textuelles prévues

Les tests source-only tentent notamment de décaler la réservation, corrompre la publication d'owner, supprimer le CAS de fin et introduire un second appel `fm36_leave`. Ces tests ne sont **pas** des simulations scientifiques et ne démontrent pas qu'un système OS multi-thread serait sûr.

**Verdict final requis :** `AT_MOST_ONCE_SOURCE_CANDIDATE`, `EXACTLY_ONCE=NOT_PROVEN`, `OWNER_LIFETIME_IN_PRODUCTION=NOT_PROVEN`, `PHYSICAL_CUTOFF=NOT_PROVEN`.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
