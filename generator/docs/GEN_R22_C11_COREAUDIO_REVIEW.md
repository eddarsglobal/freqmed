# FREQMED — GEN-R22 Independent C11 & CoreAudio Lifetime Review

## Référence réellement validée

Le journal propriétaire Mac Intel du 14 novembre 2026 a confirmé GEN-R21, commit `01db479705fc39b5b8d72c60845c3a6d29c5c0d8` : **417/417 tests Python PASS**, **33/33 assertions natives C PASS**, **113/113 fichiers du générateur intègres**, ancienne archive R19 recontrôlée (103 fichiers, quatre rapports), registre R21 établi avec **11/11 portes OPEN, 0 résolue**, et nouveau dossier privé de quatre documents SHA-256 vérifiés. Aucune sortie CoreAudio ni EM liée au binaire, aucune simulation scientifique ou émission.

## Revue GEN-R22 — trois premières lacunes du Bureau

L'auditeur `audits/r22_coreaudio_lifetime_review.py` relit le **vrai code C11 épinglé** `src/acoustic_macos.c`, l'allowlist de l'exécutable et le JSON R21 réellement recalculé depuis les sources/rapports R16–R20 et l'archive historique R19.

Il consigne **17 contrats statiques bornés**, chaque contrôle associé à une chaîne présente à une ligne réelle du code et à l'empreinte SHA-256 :
- Compteurs atomiques `active_output_callbacks`, `active_property_listeners`, entrée/sortie des deux callbacks, drapeau `pcm_writer_gate`, défaut de chevauchement des callbacks et champs PCM non atomiques identifiés.
- Contexte alloué sur le tas transmis aux callbacks, tests du verrou de fermeture, suppression des écouteurs et tentative de fermeture synchrone de la file.
- Échec de liaisons de sortie, erreurs de `AudioQueueDispose`, conservation du contexte en cas d'incertitude, compteurs à zéro et `dispose_confirmed` avant certaines libérations.
- Entrée publique acoustique refusant la sortie, exécutable lié uniquement aux sources no-output.

**Ces 17 observations ne sont pas un résultat de vérification formelle du modèle mémoire C11.** L'auditeur utilise un extracteur borné d'accolades et des ancrages textuels, non un parseur C complet, un analyseur d'interleavings concurrentiels, un thread sanitizer ou un outil de qualification OS.

### Trois questions formellement non résolues

1. **`C11_PCM_SINGLE_WRITER_NOT_PROVEN`** — Le PCM possède des champs non atomiques (`phase`, `frames_written`). `atomic_flag` sérialise certaines écritures du callback ; le contrôleur appelle aussi `fill_audio` avant le démarrage prévu. L'absence de chevauchement entre les deux chemins et l'ordre happens-before avec l'OS ne sont pas établis par les éléments statiques.
2. **`CALLBACK_ENTRY_ACCOUNTING_WINDOW_UNPROVEN`** — Les compteurs atomiques sont incrémentés après la réception du pointeur de contexte par un callback. Un relevé à zéro n'empêche pas logiquement un callback tardif de commencer : la preuve de terminaison dépend du contrat et du comportement réel de CoreAudio.
3. **`FAILED_OS_DISPOSE_REAL_BEHAVIOR_UNTESTED`** — Le code est conçu pour conserver le contexte en cas d'échec de `AudioQueueDispose` ou d'incertitude liée aux listeners, mais n'a pas reçu de témoin sur le vrai comportement d'une telle erreur de l'OS.

La revue exige ensuite un audit expert C11/threads, une preuve du cycle de vie API documentée, des tests système spécifiques séparément autorisés et des témoins indépendants. **GEN-R22 ne fait pas ces essais.** Les trois portes originales restent `NOT_PROVEN / NOT_TESTED / NOT_TESTED`, et les 8 autres restent également ouvertes.

## Validation logicielle et conservation des preuves

Le nouveau runner `RUN_GEN_R22_MAC_INTEL.command` relance les audits R16→R21, puis R22, **sans compilation d'objets de sortie dans l'exécutable**. Les cinq objets candidats CoreAudio/EM sont compilés isolément non liés. Les **33 assertions C** et la vérification native `nm` sont conservées. Les **20 nouveaux tests Python** inspectent les contrôles C11, les statuts non certifiés, les mutations textuelles défavorables, et le lien avec les véritables rapports R16–R21.

Après la réussite réelle du selftest Mac Intel uniquement, le runner produit un nouveau dossier local GEN-R22 avec les six JSON/MD R20, R21, R22 et leurs empreintes SHA-256 ; l'archive R19 originale n'est jamais modifiée.

**Cible propriétaire GEN-R22 : 437 Python (417+20), 33 C natives, 118 sources épinglées, 17 observations statiques, 3 questions non résolues, 11 portes ouvertes. GEN-R22 est PENDING jusqu'au journal réel.**

`NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
