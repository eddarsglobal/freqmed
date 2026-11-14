# GEN-R8 — Rapport d’ingénierie à soumettre au Bureau (non certifié)

**B04 — Métrologie acoustique.** Le cycle de vie CoreAudio gère à présent séparément les tampons en file et la notification d’arrêt. Cela améliore la cohérence du futur signal de sortie acoustique, mais ne prouve aucune pression ni fréquence acoustique réelle. Aucun appareil de mesure n’a été qualifié.

**B07 — DSP / Audio.** Le code numérique émet des consignes d’échantillons vers AudioQueue, sans prétention de résultat expérimental. À vérifier sur équipement physique : cadence réelle, surcharge, interruption, latence, arrêt sur panne, amplitude et qualité de conversion.

**B09 — Logiciel/sécurité.** La fin normale déclenche une vidange asynchrone des tampons (`AudioQueueStop(false)`) seulement après démarrage. Le statut d’arrêt est observé par `kAudioQueueProperty_IsRunning`. Les arrêts sur défaut utilisent `AudioQueueStop(true)`. Les états partagés sont atomiques. Le backend AudioQueue reste compilé seulement comme objet isolé, aucun appel d’activation dans l’exécutable livrable.

**B05 — Générateur EM.** Les résultats IOKit du Mac Intel sont : 10 périphériques USB, 23 interfaces USB, 4 ports série, 0 USBTMC. Aucun appareil EM qualifié n’en découle. Il est interdit d’inventer une interface d’émission à partir de ports série non identifiés.

**B10 — Sûreté.** Aucune émission n’est autorisée. Les mécanismes de vidange, listener et watchdog ne constituent pas des arrêts matériels indépendants. La certification et l'autorisation d’un banc de test non biologique restent à obtenir.

**Verdict préparatoire : GEN-R8 PREPARED_FOR_BUREAU_REVIEW, aucun vote ni certificat délivré.**
