# FREQMED GEN-R43 — Post-Closure, Ticket Binding & Capacity Threat Matrix

**Analyse sur sources réelles SHA-pinnées, sans simulation d'interleavings C11 ni exécution de callback OS.**

| Risque | Garde source C43 | Limite non résolue |
|---|---|---|
| Réservation après CLOSED | CAS CLOSED/reservations du même mot | Réservations antérieures subsistent |
| Autorisation après CLOSED | CAS CLOSED/authorizations du même mot | Autorisation antérieure peut sortir après close |
| Publication de `owner_out` après CLOSED | CAS autorisation précède l'écriture | **Non empêché** ; pas de transaction atomique C/pointeurs |
| Quiescence post-close | Aucune intégration OS | **NOT_PROVEN**, y compris callbacks tardifs |
| Ticket par indice public R41 | Ticket opaque C43 | Un pointeur connu reste copiable/forgé |
| Ticket et `userdata` usurpés | Comparaison des deux identités | Deux pointeurs connus ne sont **pas** une preuve d'authenticité |
| Type opaque C | Impossible de copier le struct par valeur via header | Pointeurs et casts restent possibles |
| Quatre permis à vie | Refus d'exhaustion et latch | Aucun recyclage, impossible flux non borné |
| Erreur d'admission après réservation | Phase REJECTED et fermeture locale | Permis et slot consommés définitivement |
| Owner nul après admission | `fm36_leave` compensateur, retour contrôlé | L'échec de leave demeure ouvert |
| Auth refusée après admission | Compensation et phase REJECTED | Synchronisation avec OS non prouvée |
| Fin répétée | CAS ACTIVE→FINISHED gagnant unique | Omission complète de fin toujours possible |
| Fin par détenteur non autorisé | Comparaison de pointeurs | Un détenteur du même couple peut gagner |
| Alias owner libéré ailleurs | Aucun `free` dans C43 | Absence de free externe non démontrée |
| Partage champs PCM/queue C31 | C31 inchangé | Happens-before global non prouvé |
| Échec `AudioQueueStop/Dispose` | C43 sans CoreAudio | Arrêt/coupure physique non certifiés |
| Liaison des candidats | `clang -c`, binaire hard-denied, `nm` | Aucun fonctionnement OS testé |
| Preuves du Bureau | Recalcul R16–R42 + 48 rapports | Onze veto historiques non levés |

**Conclusion limitée :** GEN-R43 améliore l'ordre de la décision d'autorisation de publication dans un mot atomique. **Ni l'exposition externe post-close, ni l'authentification, ni la capacité ne sont résolues.**

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
