# FREQMED — GEN-R20 Independent Evidence Reverification

## Témoin logiciel antérieur
Le journal propriétaire Mac Intel du 14 novembre 2026 pour **GEN-R19**, commit `e77b1ff47a0748d4e91118a865e2681680fd9c31`, a confirmé **375/375 tests Python, 33/33 assertions natives C, 13/13 contrôles adversariaux R19 et 103/103 empreintes sources PASS**. R16/R17/R18 PASS ; aucun générateur acoustique/EM n'était lié à l'exécutable. L'archive privée R19 `~/Downloads/FREQMED_GEN_R19_EVIDENCE__63dtqxs` a été créée, avec quatre JSON, le manifeste source et les index SHA-256. Le journal atteste sa création et la vérification de ses empreintes ; le contenu détaillé des quatre JSON ne figure pas directement dans la PR.

## Contre-vérification GEN-R20
`audits/r20_bureau_archive_review.py` ouvre cette **archive historique en lecture seule**. Sa seule source de référence est le manifeste original R19, pas le manifeste courant R20. Il exige le commit R19 exact et le SHA-256 littéral `c80091fd6d22e8e8bef076b4565f5640be70c53268c4238aa8d264b1207dfb28`, avec **103 fichiers historiques**. Cela empêche d'utiliser une nouvelle archive GEN-R20, automatiquement plus grande, pour se prétendre témoin R19.

Le vérificateur examine les sept noms autorisés de l'archive, les six empreintes répertoriées, les octets du manifeste, la cohérence de l'index et les quatre rapports :
- R16 : **25 identifiants exacts**, état PASS, réserves obligatoires, SHA du code acoustique ;
- R17 : SHA du manifeste R19, 103 sources, lien SHA de la représentation canonique R16 ;
- R18 : preuve exacte de **13 retours, 4 libérations heap et 6 libérations de verrou**, SHA des octets des rapports R16/R17, SHA de la source et du manifeste ;
- R19 : **13 contrôles adversariaux**, limites non effacées, empreintes des sources acoustique et EM, 103 sources et refus d'émission.

Il recalcule séparément sur le code C *encore identique et épinglé* les preuves R16 et l'enveloppe source R18, puis les treize contrôles structurels R19. L'archive du propriétaire n'est jamais modifiée, déplacée ni remplacée. Les tests GEN-R20 utilisent uniquement des archives temporaires construites à partir des vraies sources du dépôt, pour confronter des altérations logicielles, et non des données physiques inventées.

## Traçabilité et limites
Le nouveau runner `RUN_GEN_R20_MAC_INTEL.command` exige le chemin réel de l'archive R19 via `FREQMED_GEN_R19_ARCHIVE_DIR`. Le contrôle est **obligatoire avant toute compilation**. Ensuite seulement, les cinq objets natifs isolés non liés, les assertions C et la suite Python complète sont exécutés. À la fin d'un selftest PASS, un **nouveau dossier privé R20** est créé dans Downloads, avec le JSON de revérification, une grille Markdown du Bureau et un manifeste SHA-256 de ces deux rapports. L'archive R19 reste intouchée.

Les contrôles SHA prouvent la **cohérence relative à une empreinte épinglée** ; ils ne garantissent pas l'identité du producteur, l'immutabilité, un horodatage certifié ou une signature cryptographique tierce. Cette revue documentaire ne prouve aucune course mémoire C11, aucune sûreté de callback CoreAudio actif ou d'échec OS réel, aucun interverrouillage indépendant, aucune métrologie, aucune qualification instrumentale ni efficacité médicale.

**Objectif propriétaire GEN-R20** : 395 tests Python (375+20), 33 assertions natives C, R16–R19 PASS et revue indépendante de l'archive R19. GEN-R20 Mac Intel **PENDING** avant témoin réel. Bureau **PENDING**, RoadMap P0.01 **IN_PROGRESS**, PR #1 DRAFT, main inchangée.

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `ACOUSTIC_OUTPUT=LOCKED` · `EM_OUTPUT=LOCKED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
