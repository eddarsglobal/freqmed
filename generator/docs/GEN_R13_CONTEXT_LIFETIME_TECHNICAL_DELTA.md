# GEN-R13 — CoreAudio Context Lifetime & Failed-Disposal Containment

## Problème réellement identifié
Dans GEN-R12, `AcousticContext ctx` était une variable de pile transmise à `AudioQueueNewOutput` et au listener. Un retour de `AudioQueueDispose(queue,true)` en échec ne garantit pas que CoreAudio ne puisse plus accéder à cette mémoire après le retour de fonction. Les compteurs R12 ne suffisaient pas à empêcher un pointeur pendant.

## Changement d'ingénierie GEN-R13
- `owner_ctx = calloc(1,sizeof(*owner_ctx))` remplace le stockage sur la pile, sans relier le backend à l'exécutable.
- L'alias de préprocesseur local `#define ctx (*owner_ctx)` préserve les expressions membres R9–R12 analysées par les tests ; `#undef ctx` est limité à la fin de la fonction. **Dette technique à retirer lors d'une future refonte lisible des accès par pointeur** ; elle n'augmente aucune autorisation.
- Le drapeau atomique global `fm_session_claim` n'autorise qu'un contexte à la fois. `fm_context_quarantined` devient un verrou de processus permanent après un cycle de vie incertain.
- Avant l'enregistrement CoreAudio, un refus de trames ou de durée libère normalement le bloc et relâche le drapeau.
- Échec de création de file : contexte conservé et accès futur refusé, sans s'appuyer sur une garantie non prouvée de callback.
- Échec de pinning de la route : `AudioQueueDispose(true)` vérifié ; le bloc n'est libéré que si la disposition réussit ; sinon, stockage mis en quarantaine.
- Chemin normal ou défaut : fermeture R11, retrait du listener R9, `AudioQueueDispose(true)`, puis vérification `dispose_confirmed` et compteurs R12. **Libération du contexte seulement en présence de disposal confirmé ET zéro callback/listener actif.**
- En cas de disposal incertain ou compteur actif, conservation volontaire de **maximum un bloc par processus**, refus de nouvelles sessions, code d'erreur. Cela évite de détruire le contexte via retour de pile tant que son cycle de vie reste incertain.

## Limites et risques résiduels
Ce confinement ne constitue **pas** une preuve d'arrêt matériel ou de callback quiescent. Le pointeur reste vivable mais un échec OS pourrait conserver des ressources ou callbacks, et le comportement du périphérique ne sera pas connu. L'unique API publique de génération demeure refusée sans condition ; ce code est **compilé comme objet isolé**, jamais lié ni exécuté par le binaire utilisateur. Le comportement CoreAudio actif, les courses sous charge, l'effet d'un `AudioQueueDispose` échoué et le temps d'extinction demandent une revue B09 indépendante et un futur banc non biologique explicitement autorisé.

Le confinement est une politique de sécurité fail-closed, pas une gestion générale de cache ou de pool et pas une solution de production. Aucun test ne simule un appareil, un champ, une mesure ou une expérience. Aucun essai acoustique ou EM n'est déclenché.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
