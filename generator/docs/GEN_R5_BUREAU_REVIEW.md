# GEN-R5 — Candidat de fixation du périphérique acoustique, pour le Bureau

**Aucun avis du Bureau n'est présumé.**

- B04 / B07 : le code propose désormais de fixer un périphérique CoreAudio à l'aide de son UID, de relire le périphérique effectivement associé à AudioQueue et de refuser si fréquence nominale ou canaux ne correspondent pas. Ce n'est ni un étalonnage, ni une mesure de fréquence physique ou de niveau acoustique.
- B09 : les trois unités de compilation (générateur AudioQueue, garde de route, fixation UID) sont compilées séparément en objets **non liés** au binaire exécutable. Vérification `nm` sur symboles d'émission et sur symboles internes.
- B10 : aucune commande d'émission, aucun arrêt matériel indépendant ; la sécurité d'un banc physique ne peut pas être déduite de ce code. Les erreurs sont fail-closed, y compris en cas de changement de route.
- B05 : aucun appareil EM identifié, backend de génération EM bloqué.

Limitations : l'identité UID provient du périphérique OS, pas d'une preuve de transducteur réel ; les garanties de coupure physique, de latence, de niveau sonore et de conformité restent ouvertes. La sélection peut évoluer pendant une opération ; la vérification périodique ne remplace pas une protection indépendante.

`GEN_R5=PREPARED_FOR_BUREAU_REVIEW` · `REAL_OUTPUT=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
