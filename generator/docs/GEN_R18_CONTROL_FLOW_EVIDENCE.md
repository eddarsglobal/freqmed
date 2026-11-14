# FREQMED — GEN-R18 : renforcement de la chaîne de preuves et couverture des sorties

## Référence vérifiée

Le témoin réel du Mac Intel (14 novembre 2026) pour GEN-R17, commit `ab4bbec86c7b3bec29a2a382adfead7c189604da`, rapporte **335/335 tests Python PASS, 33/33 assertions C PASS, 25/25 contrôles R16 PASS**, 92 fichiers intègres et vérification indépendante R17 PASS. Cinq objets natifs ont été compilés **sans être liés à l'exécutable** ; aucune émission acoustique ni électromagnétique.

## Nouvel auditeur GEN-R18

`audits/r18_control_flow_envelope.py` analyse **le code C réel et ses jetons**, sans jamais appeler les fonctions AudioQueue ni procéder à des essais physiques. Il ne modifie pas `acoustic_macos.c`. Ses constats structuraux admissibles sont strictement bornés :

- **13 sites de `return`** classifiés avec garde lexicalement vérifiée, emplacement source et phase de propriété des ressources. Les phases prévues sont 5 avant la réservation de session, 2 dans la réservation sans allocation, 3 après allocation mais avant publication de userdata CoreAudio, 2 après publication OS potentielle, et 1 retour final sous contrôle d'erreur.
- **4 sites de `free(owner_ctx)`**, chacun associé à une condition explicite : trames invalides, enveloppe invalide, disposition de binding confirmée avec les deux compteurs de callbacks à zéro, ou `context_quiescent` final.
- **6 libérations du verrou `fm_session_claim`**, chacune située dans une garde autorisée ; aux quatre chemins qui possèdent un contexte heap, `free` précède la restitution de la réservation.
- **7 familles d'appels OS** inventoriées sans invocation : une création de queue, deux dispositions, un démarrage, un arrêt d'urgence, un ajout et retrait de listener et une allocation de buffer. GEN-R18 exige les dénombrements et l'ordre attendu de publication, liaison, listener, démarrage, barrière d'arrêt, retrait et disposition finale.
- **Ordres atomiques** : accès en acquire à la quarantaine, publications monotones à la valeur 1 avec release, acquisition unique de la session et restitution avec release ; aucun déverrouillage de quarantaine toléré.
- Toute sortie ajoutée, expression de succès anticipé, `goto` inattendu, site de libération non classifié ou nouvel appel OS non recensé produit un **échec fermé**. Le parseur traite les `if` à bloc et les retours directement gardés à instruction unique.

## Chaîne de preuves reliée

Le runner GEN-R18 exécute dans cet ordre :

1. Vérification SHA-256 du manifeste et des fichiers de la source épinglée.
2. Auditeur R16 : `GEN_R16_OWNERSHIP_EVIDENCE.json` avec 25 contrôles statiques.
3. Vérificateur R17 : `GEN_R17_VERIFIED_EVIDENCE.json`, qui atteste l'intégrité des fichiers et refuse les rapports incomplets.
4. Auditeur R18 : `GEN_R18_CONTROL_FLOW_EVIDENCE.json`, qui classe les sorties et revalide le SHA du code, l'empreinte du manifeste, l'empreinte canonique du rapport R16 et les données de vérification R17. Il vérifie en plus l'allowlist **six fichiers C exactement** du runner R18.
5. Compilation macOS Intel des cinq objets backend **isolés et non liés**, 33 assertions C natives, audit `nm` des symboles du programme hard-denied, puis **355 tests Python attendus** (335 précédents + 20).

Ces rapports n'incluent ni signature cryptographique externe ni certification formelle. Ils portent des SHA-256 des octets contrôlés, pas une identité juridique. Les tests de modifications source sont des vérifications **textuelles en mémoire**, sans jamais compiler le code modifié ni simuler une mesure physique.

## Limites impératives

L'auditeur est un **analyseur lexical borné**, pas un graphe de flot de contrôle C complet, pas un compilateur vérifié, pas un model checker C11 et pas une preuve d'absence de race. Les branches conditionnelles préprocesseur, les alternatives non recensées et les effets interprocéduraux restent des limites. Les compteurs atomiques n'établissent pas la durée de vie réelle des callbacks sous incident OS. Aucune expérience de coupure indépendante, métrologie acoustique/EM, qualification instrumentale, simulation scientifique, exposition biologique ou sortie physique n'a lieu dans GEN-R18.

**Statut préparatoire :** commit source candidat, **355 tests Python + 33 assertions natives C attendus sur le vrai Mac Intel**, sans annoncer leur réussite avant le journal du propriétaire. Bureau PENDING. RoadMap P0.01 IN_PROGRESS. PR #1 reste DRAFT ; `main` non modifiée.

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `ACOUSTIC_OUTPUT=LOCKED` · `EM_OUTPUT=LOCKED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
