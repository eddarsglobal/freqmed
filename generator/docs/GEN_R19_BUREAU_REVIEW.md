# FREQMED GEN-R19 — Bureau indépendant : revue adversariale et archivage (PENDING)

**B09 : intégrité du code, mémoire et concurrence.** Reproduire les 13 contrôles adversariaux à partir du code C épinglé, distinguer les détections sémantiques de la barrière SHA-256 globale et démontrer, à l'aide des tests textuels seulement, quelles mutations restent hors périmètre. Revoir les 13 sorties, 4 `free`, 6 releases et transitions en cas d'erreur OS. L'audit lexical n'est pas une preuve complète du contrôle-flow C ni de l'absence de races mémoire C11.

**B09 : authenticité des preuves.** Inspecter les quatre JSON R16–R19 après recalcul indépendant des sources et du manifeste ; vérifier `EVIDENCE_SHA256SUMS.txt`, `EVIDENCE_INDEX.json`, le lien au commit du bootstrap et les permissions 0700/0600. Confirmer la limite explicite : **pas de signature externe, pas de magasin WORM, pas d'horodatage tiers** ; toute personne pouvant réécrire les preuves et leurs propres hashes peut fabriquer une nouvelle archive cohérente.

**B04/B07 : acoustique.** Le backend CoreAudio reste un objet **compilé isolément et non lié**. Aucun haut-parleur alimenté, aucune fréquence émise, aucune mesure de pression et aucun interverrouillage matériel indépendant qualifié.

**B05/B06 : EM.** Aucun générateur EM qualifié, aucun port de sortie ouvert, aucune fréquence/champ physique généré ou mesuré. Un descripteur USB ou un registre OS en lecture seule n'est pas une preuve d'instrument admissible.

**B10 : éthique et gouvernance.** Aucune simulation scientifique, aucun essai humain/animal/biologique, aucune production. Vérification des licences FOSS des dépendances (GEN-R19 : standard library Python seulement). Aucun déclassement du refus `Guardian`.

**Baseline réelle :** GEN-R18 Mac Intel, 355/355 Python, 33/33 C, 97 fichiers PASS, sans émission. **GEN-R19 :** 375 Python attendus, 33 C, quatre JSON et une archive locale vérifiable, encore **NON ATTESTÉ**. RoadMap P0.01 IN_PROGRESS. PR #1 DRAFT, base main inchangée. `BUREAU_CERTIFICATION=PENDING` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
