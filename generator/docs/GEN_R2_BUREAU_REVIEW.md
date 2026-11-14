# FREQMED GEN-R2 — Revue du Bureau, pas certification

**B04 + B07** : le nombre de canaux et la fréquence d'échantillonnage rapportés par CoreAudio reflètent des métadonnées du périphérique par défaut, sans mesure acoustique indépendante et sans garantie de transducteur réel. La bande physique et le SPL ne sont pas déduits des valeurs OS.

**B09** : la compilation de R2 ne relie **aucun symbole de démarrage audio**. Le fichier de backend AudioQueue `acoustic_macos.c` est conservé dans les sources, isolé du binaire et non appelé ; l'API publique de sortie retourne toujours une erreur.

**B05** : aucune génération EM ne peut être implémentée sans un appareil réel choisi et un contrat de communication vérifié. Pas de Wi-Fi/Bluetooth/iPhone utilisés comme émetteurs de fréquence arbitraire.

**B10** : demander des profils matériels, des limites d'exposition, une coupure physique indépendante, un protocole de banc non biologique et un avis de sûreté avant un build de génération effectif. Ce rapport n'autorise rien.

Aucun test logiciel ne peut qualifier une émission, une pression physique ou une application médicale. Les tests du code ne sont pas des simulations scientifiques.
