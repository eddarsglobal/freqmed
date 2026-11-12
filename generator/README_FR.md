# FREQMED — GEN-R4 : route acoustique surveillée et arrêt immédiat

**AUCUNE ÉMISSION PHYSIQUE** dans le binaire R4. Il s'agit du développement du véritable backend du générateur, pas d'un logiciel de simulation ou de relevés.

GEN-R3 : la compilation CoreAudio isolée et les 50 tests ont réussi sur le Mac Intel. La sortie audio par défaut a déclaré deux canaux et une cadence nominale de 44 100 Hz. Ce n'est pas une fréquence acoustique émise.

**GEN-R4 ajoute au code source de sortie acoustique :**

- Empreinte de route interne (jeton éphémère de périphérique OS, fréquence nominale et nombre de canaux), sans publication du jeton.
- Comparaison de la route avant préparation, juste avant le démarrage prévu et pendant le fonctionnement futur.
- Demande d'arrêt immédiat en cas de changement de route ou d'erreur, sans vidange prolongée des tampons.
- Compilation indépendante du code AudioQueue et du module de surveillance, dans deux objets **non liés** au programme lancé.
- Refus toujours actif de toute émission acoustique et EM dans l'exécutable livré.

**Limites importantes :** ce contrôle n'empêche pas une bascule de périphérique entre deux lectures, ne fixe pas explicitement un transducteur physique, ne fournit aucun arrêt matériel indépendant et ne démontre aucun niveau acoustique sûr. Le code générateur ne doit pas être activé avant les revues et essais du Bureau.

**Commande Mac Intel :** `bash RUN_GEN_R4_MAC_INTEL.command selftest`, puis `bash RUN_GEN_R4_MAC_INTEL.command probe` pour afficher les seules métadonnées CoreAudio. Aucune installation ni connexion Internet.

Logiciel libre Apache-2.0 ; frameworks CoreAudio propriétaires de macOS comme dépendance de plateforme. Design Windows 11 × macOS inchangé, 10 langues conservées dans la feuille de route.

`NEVER_SIMULATION=ENFORCED` · `ACOUSTIC_EMISSION=NONE` · `EM_OUTPUT=BLOCKED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
