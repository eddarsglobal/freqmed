# GEN-R42 — Index Forgery, Atomic Admission & Capacity Exhaustion Matrix

**Audit source-only des octets C réels ; aucune exécution de callback, aucun interleaving simulé, aucune émission scientifique.**

| Vecteur / menace | Garde candidate C42 | Limite restant à prouver |
|---|---|---|
| Indice entier R41 inventé | API opaque `FM42Ticket*`, pas de `slot_id` public | Pointeur privé connu/copied/forgé encore valide |
| Pointeur illégal | Comparaison d'adresse avant déréférence | Authentification d'une vraie adresse privée absente |
| Pointeur alias partagé | CAS `ACTIVE→FINISHED` unique | Sortie prématurée d'un autre callback possible |
| Fermeture et réservation simultanées | `atomic_uint gate` CLOSED/count et CAS | Réservation déjà gagnante peut toujours poursuivre |
| Fermeture après dernier contrôle | Revérification CLOSED après R36 admission | Publication après fermeture non exclue |
| Cinquième réservation | Refus, latch CAPACITY, gate CLOSED | Capacité quatre à vie inadaptée au flux OS |
| Trois autres réservations consommées puis rejet | Slots permanents non réutilisés | Exhaustion prématurée possible |
| Échec de `fm36_try_enter` | Rejet du slot et gate CLOSED | Quiescence CoreAudio non établie |
| Owner nul après admission | `fm36_leave` compensateur, retour contrôlé | Échec compensation reste ouvert |
| Fermeture observée après admission | Compensation R36 et `REJECTED` | Compteur peut rester incohérent si `leave` échoue |
| Owner remis au consommateur | Admission préalable, phase ACTIVE | Tous les alias externes restent incontrôlés |
| Appel `complete` manquant | Aucun mécanisme externe de forcing | Exactly-once non prouvé |
| Double appel `complete` | Un seul CAS gagnant par ticket | Pas de preuve de fin effective du vrai callback |
| Erreur `fm36_leave` | Latch fermé et statut d'erreur | Admission globale/OS non certifiés |
| Erreur d'inscription | Ancre R36 one-shot | Owner doit rester vivant malgré rejet |
| Erreur `AudioQueueStop/Dispose` | Aucun appel CoreAudio C42 | Arrêt et coupure physique non prouvés |
| C11 HB du vrai `ctx` | Aucun champ PCM C31 modifié | Global race freedom non prouvée |
| Preuve de non-liaison | `clang -c`, `nm`, CLI hard-denied | Aucune certification matérielle |
| Bureau | R16–R42 recalculés, veto conservés | 11 portes historiques toujours ouvertes |

L'innovation R42 concerne **uniquement l'ordre de nouvelles réservations et la fermeture locale d'un mot atomique**, **pas** une solution de capacité, d'authenticité du ticket ou de terminaison de callback.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
