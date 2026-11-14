# GEN-R7 — Rapport de revue à soumettre au Bureau (NON CERTIFIÉ)

**B05 — Génération et métrologie EM.** IOKit identifie des **classes de périphériques** et des descripteurs de bus USB, sans accès aux instruments. Un périphérique USBTMC peut être un appareil de mesure, pas un générateur. La présence d'une interface ne démontre aucune capacité de sortie, aucune puissance, aucune étendue en Hz et aucune conformité. L'absence d'interface USBTMC ne prouve pas qu'aucun instrument ne soit disponible via une autre interface.

**B06 — Instrumentation.** Le recensement fournit la présence de services USB hôte et de nœuds série d'appel du système, sans ouverture de port. Une identification approfondie exige un manuel d'équipement et une vérification physique.

**B09 — Sécurité du logiciel.** API IOKit consultées exclusivement en lecture seule, classes de service fixes, comptages bornés, libération des objets, pas de numéro de série ou UID imprimé. `nm` doit détecter toute tentative de lier les fonctions de sortie acoustique, d'ouverture de périphérique ou de modification du registre. Ce contrôle ne garantit pas l'ensemble de la sûreté OS.

**B10 — Sûreté.** Aucune commande d'émission acoustique ou EM. La détection d'une interface USBTMC ne satisfait ni le profil matériel certifié, ni l'arrêt indépendant, ni la qualification d'un banc non biologique. L'activation reste interdite.

**Verdict technique préparatoire : `GEN_R7_CODE_CANDIDATE_REVIEW_REQUIRED`.** Aucune approbation ni certification du Bureau ne peut être déduite des tests ou de ce document.
