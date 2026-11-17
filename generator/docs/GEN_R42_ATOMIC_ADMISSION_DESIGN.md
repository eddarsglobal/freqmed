# FREQMED GEN-R42 — Index Forgery, Admission Atomicity & Capacity Exhaustion Remediation

**Dernier témoin propriétaire réel : GEN-R41 Mac Intel logiciel PASS (817/817 Python, 33/33 assertions natives C, 236/236 sources SHA-256, 44/44 rapports SHA-256 ; 17 novembre 2026).** Cette qualification logicielle ne certifie ni les callbacks OS, ni la liberté des races C11 globale, ni la coupure physique.

## Conception C42 isolée

Les deux nouveaux fichiers `candidates/r42_admission_gate_ticket.h` et `.c` forment une proposition **C11 isolée, compilation seulement, jamais liée, chargée, exécutée ou appelée par CoreAudio**. Les C31/C36/C37/C39/C40/C41 et le moteur original demeurent inchangés.

1. **Indices falsifiables R41 :** l'API n'expose plus `FM41TicketRef{slot_id}` ; le client reçoit `FM42Ticket *`, un type opaque dont les adresses internes sont vérifiées **avant déréférencement**. Cette transformation élimine la surface d'attaque de l'indice entier arbitraire. **Elle ne rend PAS le pointeur authentifié : une adresse privée valide divulguée, devinée ou copiée peut encore conduire à une sortie prématurée.** Le candidat ne constitue aucune capacité de sécurité.
2. **Admission C11 linéarisable localement :** un même `atomic_uint fm42_gate` contient `FM42_CLOSED` (bit 31) et un compteur de permis à vie (16 bits inférieurs). `fm42_reserve_permit` effectue un CAS unique `state→state+1` tant que le bit CLOSED est absent et la capacité inférieure à 4. `fm42_latch` et `fm42_seal` placent CLOSED par OR atomique. **Dès que CLOSED est publié dans l'ordre de modification de ce mot atomique, aucun nouveau CAS de réservation ne peut réussir**. Les réservations déjà gagnantes **ne sont pas annulées atomiquement** et une publication de ticket peut encore suivre une fermeture concurrente.
3. **Capacité :** quatre emplacements statiques à usage unique, **jamais recyclés**, y compris après rejet. Aucune allocation de repli, aucun callback de production. Une cinquième tentative ferme localement l'admission et enregistre un défaut. **Quatre admissions à vie ne représentent pas une architecture capable de servir un flux CoreAudio continu**.
4. **Admission et compensation :** `fm42_begin` réserve un permis, puis un slot par CAS ; refuse les fermetures déjà observées, appelle `fm36_try_enter`, revérifie CLOSED avant publication, et sur annulation détectée appelle `fm36_leave` en contrôlant le retour. Les **quatre branches de rejet de slot** deviennent `FM42_REJECTED`, non recyclables. Le code ne garantit pas l'absence de faute après le dernier contrôle ni que `fm36_leave` réussisse.
5. **Données propriétaire :** `owner_out` reste un pointeur externe. La revendication one-shot `fm36_prepare_once` impose une rétention du propriétaire jusqu'à la fin du processus même si l'exposition échoue. La durée de vie de tous les alias demeure **NOT_PROVEN**.
6. **Sortie :** `fm42_complete` compare les adresses de slot sans déréférencer le pointeur fourni, puis CAS `ACTIVE→FINISHED` avant `fm36_leave` : **AT-MOST-ONCE seulement** pour un ticket vivant. Un pointeur valide usurpé peut terminer le ticket d'autrui ; un callback peut ne jamais appeler `complete`. **EXACTLY_ONCE=NOT_PROVEN**.
7. **Défauts :** `fm42_latch` met le bit CLOSED avant de publier la raison dans un second mot atomique. Ce registre représente un veto **local et logiciel**, pas une commande `AudioQueueStop`, une preuve de quiescence OS ou une sécurité matérielle.

## Livrables et discipline de preuve

- `audits/r42_index_forgery_admission_review.py` : **20 obligations OPEN_NOT_PROVEN, dont 6 CRITICAL** ; **40 témoins source SHA-pinnés** entre C31/C36/C37/C39/C40/C41/C42 et leurs en-têtes ; six contrats C11 ; recalcul exact des rapports R16–R41.
- `tests/test_r42_index_forgery_admission_review.py` : **20 tests Python source-only**, dont quatre mutations textuelles ; aucune simulation de concurrence ni invocation du module C42.
- `RUN_GEN_R42_MAC_INTEL.command` : compilation de C42 en **objet isolé `clang -c` non lié**, contrôle `nm`, exécutable `output_hard_denied.c`, chaîne des rapports historiques et **46 rapports SHA-256 R20–R42**, uniquement après succès total.
- `docs/GEN_R42_BUREAU_PROOF_GATES.md` et `docs/GEN_R42_FORGERY_CAPACITY_MATRIX.md` documentent les veto B07/B09/B10.

**Objectifs GEN-R42 Mac Intel encore PENDING : 837 tests Python, 33 assertions C natives, 244 sources SHA-256, 46 rapports SHA-256.** Le journal réel R42 n'existe pas encore. PR #1 doit rester DRAFT et non fusionnée. Bureau historique 11 OPEN, 0 levée.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
