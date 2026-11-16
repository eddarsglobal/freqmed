# FREQMED GEN-R37 — Adversarial Callback Lease and Ownership Contract Matrix

**Document source-only, pas de simulation scientifique ni de callback OS exécuté.**

| Menace | Garde de code C37 | Limite du contrôle |
|---|---|---|
| Pointeur `userdata` non issu de l'ancre | R36 compare le jeton statique avant owner | C31 n'est pas raccordé |
| Accès propriétaire avant admission | `fm37_begin` appelle `fm36_try_enter` d'abord | La validité de owner dépend des alias externes |
| Listener et callback mélangés | `fm37_property_enter` / `fm37_output_enter` | Pas de signature ABI CoreAudio fournie |
| Baux actifs réutilisés | `FM37_LEASE_UNUSED` imposé à l'entrée | La phase du bail n'est pas atomique ; aucun partage autorisé |
| Fin appelée deux fois | `ACTIVE→FINISHED` avant decrement | Garantie locale uniquement, pas de concurrence |
| Fin oubliée après erreur | Aucun mécanisme de fermeture implicite | Preuve de couverture exhaustive des sorties requise |
| Erreur `fm36_prepare_once` | Refus et unique jeton consumé ou intact | Propriétaire doit rester conservé si revendication effectuée |
| Erreur `fm36_mark_exposed` | Refus ; pas de récupération/réinitialisation | Heap owner potentiellement retenu |
| `seal` pendant un callback | Phase C11 R36 fermée aux nouvelles entrées | Callback admis peut continuer ; OS non quiescent |
| Arrêt OS échoué | Aucun appel AudioQueue dans C37 | Coupure physique non démontrée |
| Dispose OS échoué | Aucune libération dans C36/C37 | Handle OS et callbacks tardifs non qualifiés |
| Liaison de C37 en production | Runner compilateur `-c`, `nm -u`, linker allowlist | Admission native/pipeline packaging à vérifier |
| Mutation retire `fm36_try_enter` | Audit source et tests adversariaux refusent | Scanner statique, pas modèle formel de C11 |
| Mutation réouvre `FINISHED` ou saute leave | Audit source et tests adversariaux refusent | N'infère aucune équivalence sémantique générale |

### Niveaux d'évidence

`SOURCE_PRESENT_SHA256` : identifiants de source et empreintes. `OBJECT_COMPILED_UNLINKED` : syntaxe et compilation C11 réelle mais non exécutée. `PROVEN_NO_OS_CALLBACK=NOT_CLAIMED` ; `GLOBAL_C11_HAPPENS_BEFORE=NOT_PROVEN` ; `REAL_OUTPUT=NOT_AUTHORIZED`.

**La prochaine étape après R37 doit être une revue indépendante des alias de propriétaire et des sorties de callbacks dans un futur candidat C isolé**, et non l'activation du code actuel.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
