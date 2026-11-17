# FREQMED GEN-R40 — Copy Prevention & Callback Completion Adversarial Matrix

**SOURCE ONLY. Aucun callback actif, interleaving simulé, appareil ou expérience scientifique.**

| Chemin ou menace | Garantie locale candidate C40 | Preuve manquante |
|---|---|---|
| Copie par valeur de `FM40Ticket` | Type incomplet dans header ; `clang -fsyntax-only` doit refuser | Autres usages arbitraires C, ABI OS non revue |
| Copie d'un `FM40Ticket*` | **Non interdite** | Contrat d'unique propriétaire côté appelant |
| Copie d'un `owner_out` | **Non interdite** | Preuve de vie de tous les alias propriétaire |
| `memcpy` avec cast dangereux | Aucun contrôle absolu en C | Absence de code malformé et confinement des sources |
| Admission double sur un slot | CAS `UNUSED→RESERVED` | Durée de vie du ticket/ownership externe |
| Emplacements épuisés | Refus sans allocation | Flux de callbacks OS non borné, **architecture non utilisable telle quelle en production** |
| Admission R36 refusée | `REJECTED` final, non recyclé | Conservation du propriétaire pendant toutes les erreurs |
| Admission avec owner nul | `fm36_leave` compensateur | Erreur de compensation et compteur non certifiés |
| `ACTIVE` publié | release de phase après écriture du token | Relations HB des autres champs du contexte |
| Double sortie d'un ticket | Un gagnant CAS `ACTIVE→FINISHED` | Événement de sortie au moins une fois |
| Aucune sortie `complete` | Aucune réparation | Vérification exhaustive des parcours vrais OS |
| `fm36_leave` renvoie erreur | Retour d'erreur, phase reste FINISHED | Compteur global et OS pas certifiés |
| Ticket forgé | Comparaison des adresses **avant déréférence** | Contrôle des appels arbitraires, typage C |
| `userdata` expiré avant admission | Ancre statique R36 attendue | C31 transmet toujours `ctx`, et non C40 |
| Listener CoreAudio | Pas de callback ABI | Contrat de retrait et terminaison OS |
| Dispose/Stop en échec | Aucun appel AudioQueue C40 | Quiescence et coupure physique non prouvées |
| Chaîne du binaire | Objet C40 `clang -c` non lié, `nm` | Distribution réelle non autorisée |
| Essais physiques | Aucun dans R40 | Qualification future instrumentale et autorisation de gouvernance |

### Verdict prudent

L'API opaque ajoute un **obstacle concret à la copie par valeur du ticket** pour les consommateurs qui respectent le système de types C. Elle ne transforme pas la terminaison **AT-MOST-ONCE** en **EXACTLY-ONCE**, n'assure aucune durée de vie propriétaire externe et n'est pas intégrée au backend acoustique. Les 18 obligations R40 (5 critiques) doivent rester **OPEN_NOT_PROVEN**.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
