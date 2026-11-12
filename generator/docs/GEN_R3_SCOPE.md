# GEN-R3 — Compilabilité du backend acoustique, sans émission
Le Mac Intel a validé R2 FIX1 : 30/30 tests et CoreAudio en lecture seule, 2 canaux, fréquence d'échantillonnage nominale 44 100 Hz. Aucun son ni champ n'a été émis.
R3 adapte le source AudioQueue au taux nominal réellement observé plutôt que 48 kHz, ajuste la rampe numérique et fait compiler ce code uniquement comme objet isolé.
L'exécutable est assemblé indépendamment avec output_hard_denied.c et ne peut appeler le backend AudioQueue. Le contrôle nm refuse tout symbole d'activation audio dans cet exécutable.
Compilabilité native R3 sur Mac Intel et qualification du matériel restent à vérifier. Aucune preuve d'émission acoustique ni de sécurité.
NEVER_SIMULATION=ENFORCED; EM_OUTPUT=BLOCKED; PRODUCTION=NOT_AUTHORIZED.
