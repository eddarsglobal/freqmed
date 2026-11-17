# GEN-R6 — Contrat logiciel EM et frontières de sécurité

Le cœur de produit FREQMED est la **génération physique** (acoustique et EM). Le Bureau assume recherche et certification. La présente étape développe une frontière logicielle pour de futurs équipements EM spécifiques, sans en inventer aucun.

`FMEmDeviceContract` décrit le transport série/USBTMC, l'empreinte d'identité, l'unité commandée, les limites propres à l'équipement et la durée maximale. `FMEmSetpoint` fournit une demande typée. Les fonctions de contrôle vérifient les données mais renvoient explicitement une réussite **structurelle seulement**, jamais une autorisation de sortie. Une identité SHA-256 au bon format ne constitue aucune attestation indépendante.

`fm_em_try_physical_emission()` refuse toujours, y compris lorsque la validation du contrat est favorable. `em_instrument_driver_abi.h` n'installe aucune implémentation : son contrat exige seulement des points d'observation du matériel et une coupure future, et ne comporte aucune commande d'activation.

Le binaire Mac R6 compile les composants de génération CoreAudio et le contrat EM en **objets séparés**, n'en charge aucun et conserve l'exécutable avec uniquement le contrôleur CoreAudio en lecture seule et les stubs de refus. Le script fait un audit `nm` des symboles interdits. Le seul programme additionnel exécutable est un test logiciel C de validation de structures, sans instrument ni données expérimentales.

Limites : aucune source physique EM, pas de pilote d'émission, pas de signaux produits, pas d'inférence de puissance/champ, pas de conformité RF/CEM démontrée, pas de coupure indépendante mise à l'essai. Les futurs plafonds logiciels ne sauraient garantir l'absence de danger biologique. Toutes les sorties restent verrouillées.
