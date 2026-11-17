# FREQMED GEN-R41 — Capacity / Index Aliasing / Error Containment Matrix

**Analyse statique de sources réelles SHA-pinnées ; aucune simulation scientifique ou interleaving C11 exécuté.**

| Risque | Mécanisme C41 source-only | Obligation encore ouverte |
|---|---|---|
| Copie d'un pointeur `FM40Ticket*` | Le C41 ne retourne plus de pointeur interne | Indice `FM41TicketRef` librement copiable et falsifiable |
| Capacité de quatre slots | Refus final et masque `FM41_FAULT_CAPACITY` | Pas d'architecture de capacité pour callbacks non bornés |
| Échec après réservation | Phase `REJECTED` terminale, sans recyclage | Admission réelle OS non évaluée |
| Owner sans alias exclusif | `fm36_try_enter` puis `owner_out` | Propriété et durée de vie externes non prouvées |
| Vérification des fautes concurrentes | Deux snapshots atomiques | Nouvelle faute peut arriver après le second snapshot |
| Owner nul après admission | `fm36_leave` compensateur et latch | Compteur incertain si `leave` échoue |
| Indice hors bornes | Rejet avant indexation du tableau | Authenticité d'un indice valide non établie |
| Double `complete` | Un gagnant CAS `ACTIVE→FINISHED` | Un indice forgé peut fermer un autre callback actif |
| Sortie jamais appelée | Aucun mécanisme de forcing | Exactly-once non démontré |
| `fm36_leave` renvoie erreur | `FM41_FAULT_LEAVE_FAILURE` persistant | Compteur global / OS toujours incertains |
| Enregistrement owner refusé | `FM41_FAULT_REGISTER` | Revendication C36 possiblement consommée à vie |
| `seal` refuse | `FM41_FAULT_SEAL` | Aucune preuve de `Stop`/quiescence CoreAudio |
| Données C31 partagées | Aucun changement C31 | Preuve C11 happens-before globale absente |
| Candidats compilés | `clang -c`, objets isolés | Aucune liaison CoreAudio autorisée |
| Binaire de contrôle | `output_hard_denied.c` et `nm` | Aucune preuve de sécurité physique |
| Validation du Bureau | Rapports R16–R41 recalculés | 11 portes historiques demeurent ouvertes |

**Le masque d'erreur ne doit pas être confondu avec une barrière de sécurité physique.** GEN-R41 décrit explicitement un échec logiciel terminal plutôt qu'une correction du flux CoreAudio.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
