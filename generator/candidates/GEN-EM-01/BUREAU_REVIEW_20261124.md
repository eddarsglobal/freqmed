# GEN-EM-01 — Qualification autonome du sous-système EM (source-only)
Date: 2026-11-24. RoadMap.md blob 81024a17e9aeafdfb5319455dae30529d85d6a16, clause E. P2.01 reste PENDING, P0.01 IN_PROGRESS_REBASE_REVIEW et P0.02 PENDING.

## Delta concret
Sept sources historiques R6/R7/R11 et ABI, reprises sans modification depuis le commit 87c9b87f4f7c63daab012fbd46dc5c56271c5f00 de la PR #1 (pins dans qualify_em.py). Aucune répétition de GEN-R66 ou modification de son code. Un nouveau lanceur autonome vérifie chaque source, compile les trois modules C11 en bibliothèque temporaire, contrôle le refus natif d'émission et d'admission documentaire, puis interroge uniquement les métadonnées du registre IOKit sur Darwin. Les sorties sont contrôlées pour cohérence, bornes, capacité et troncature. Le rapport ne contient ni chemin série, ni numéro de série, ni adresse de périphérique. La présence d'une interface USBTMC ou série ne certifie pas l'existence d'un générateur EM. Pas de pilote, d'ouverture de port ou de commande instrument. Aucun matériel n'est qualifié ni ajouté.

## Preuves exécutées le 24 novembre 2026 sur Linux x86_64
- 9/9 tests unittest du lanceur PASS (ABI ctypes, pin absent/altéré, digest, refus de qualification automatique, refus de comptes/capacité/troncature/bornes incohérents). Les données adversariales sont des entrées API invalides, jamais des mesures physiques.
- 7/7 blobs Git historiques vérifiés à l'identique dans la copie locale compilée et sur la branche.
- Compilation C11 des trois sources exactes + chargement ctypes : PASS. Refus natif d'émission et de qualification : PASS. Sur Linux, inventaire absent (null), UNSUPPORTED_PLATFORM, retour 77, verdict PASS_PORTABLE_ONLY_MAC_PENDING. Aucun résultat IOKit prétendu.
- SHA256 du lanceur exact : 211ea3e96600fb47f13b0144999fc05053d96ed50fe4ac8f9e40056046b0eedc ; blob Git d2cbc87110fbfeca7cb6c742b8be54d0c0c1db5e.
- Mac Intel réel : PENDING. Aucune preuve de sécurité matérielle indépendante.

## Qualification Mac
Depuis cette branche candidate, dans un dossier isolé : python3 -B qualify_em.py --selftest puis python3 -B qualify_em.py. Un seul rapport BUREAU_REPORT. Aucun Safari, aucune installation, aucun sudo. Requiert Python 3 et compilateur C déjà disponibles ; IOKit/CoreFoundation sont des dépendances Apple propriétaires de plateforme, non redistribuées. L'inventaire Mac sera une observation réelle en lecture seule, pas une mesure du champ ni un test de générateur. Le code ne lance aucun serveur.

## Bureau — périmètres de revue, non signatures
B05 : identité, unité physique propre à l'instrument, protocole constructeur, limites et conformité encore à établir. B06 : inventaire des transports observables, métrologie non effectuée. B09 : pins, contrôle ABI et séparation du candidat. B10 : aucun pilote lié, refus natif. La revue est assistée par IA, sans certification indépendante. Ne pas utiliser d'équipement non qualifié. Un éventuel instrument exige identification fiable, droits documentaires, profil/limites et arrêt indépendant, et autorisations conformes aux gates G0–G4. Aucune émission ou exposition, aucune simulation. REAL_OUTPUT=NOT_AUTHORIZED ; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED ; PRODUCTION=NOT_AUTHORIZED ; EM_OUTPUT=BLOCKED_NO_QUALIFIED_DEVICE. PR DRAFT, aucune fusion dans main.
