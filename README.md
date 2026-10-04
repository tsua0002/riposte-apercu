# La Riposte — aperçu limité d’une proposition d’auditeur

Projet personnel et non officiel de Thomas, contact : thomas@codethelaw.eu. Aucun partenariat ni validation de Radio Nova ou de l’équipe de La Riposte n’est présumé.

Ce site présente une proposition d’accompagnement de l’émission du 28 septembre 2026 : un court extrait de la présentation (environ dix secondes), la revue de presse complète (129 sujets et références) et l’empreinte SHA-256 de la transcription complète conservée en privé. L’empreinte engage sur une version : elle ne prouve seule ni la complétude ni l’exactitude du fichier.

**Ce dépôt ne contient ni vidéo, ni audio, ni transcription intégrale, ni sous-titres complets.** La transcription complète et les sous-titres sont conservés séparément comme outils de travail proposés à l’équipe, sans publication indépendante prévue ici.

- Page : https://tsua0002.github.io/riposte-apercu/
- Code : https://github.com/tsua0002/riposte-apercu

## Transparence

Le site est statique, avec un petit module JavaScript de synchronisation. **YouTube ne se charge qu’après un clic explicite sur « Activer YouTube »**. Le lecteur utilise le domaine `youtube-nocookie.com`, mais son activation charge aussi l’API officielle depuis `youtube.com` : YouTube reçoit notamment votre adresse IP ; ce n’est pas une lecture anonyme ni une garantie d’absence de suivi par YouTube.

Aucun MP4 n’est servi par ce site ou par R2. Aucun formulaire d’envoi, téléchargement automatique ou outil d’analyse d’audience n’est ajouté par le projet. L’hébergeur peut conserver des journaux techniques. Les services externes ont leurs propres politiques de confidentialité.

## Démonstration

Activer le lecteur, puis lire l’introduction entre environ 00:42 et 00:52. Les cinq répliques affichées suivent la lecture ; cliquer sur leur horodatage déplace le lecteur lorsqu’il est prêt. Faire défiler manuellement le texte suspend le suivi. « Réaligner » le reprend ; « Relancer l’extrait » revient au début. Hors de ces cinq répliques, aucune autre transcription n’est fournie.

Sur iPhone, la lecture reste dans la page grâce à `playsinline` ; un appui supplémentaire sur ▶ peut être nécessaire. Si l’intégration est interdite, indisponible ou bloquée, le lien YouTube officiel reste utilisable. Sans JavaScript, le texte, les sources et les liens restent lisibles.

## Vérifications locales

```bash
python3 scripts/build_preview.py  # nécessite les données privées du dépôt voisin
python3 scripts/test_preview.py
node --test scripts/test_demo.mjs
python3 -m http.server 8000 --bind 127.0.0.1
```

Aucune dépendance à installer. Le générateur ne copie jamais les fichiers intégraux dans ce dépôt.

Cinq explications générales sont regroupées derrière de petites icônes d’avertissement. Les métadonnées des articles restent lisibles, les notes détaillées sont dans des volets « Notes de recherche » et le hash reste visible. Pour les icônes : survol à la souris, focus au clavier ou toucher/clic pour les ouvrir. Un second clic, Échap ou un clic extérieur ferme l’infobulle. Les textes et liens sont conservés ; sans JavaScript, ils restent affichés normalement.

Les sources sont proposées pour documenter les sujets ; ce ne sont pas les sources officiellement déclarées par l’équipe. Le travail intégral reste en cours de relecture. Aucun article intégral n’est reproduit.

## Collaboration

L’objectif est un complément facultatif permettant aux auditeurs moins au fait de l’actualité de retrouver les références. La proposition principale est une revue de presse semi-automatisée à améliorer avec l’équipe. La transcription complète et les sous-titres sont des outils de travail destinés à l’aider à retrouver des passages et à préparer de meilleurs sous-titres. La démo utilise uniquement la vidéo YouTube officielle, sans rediffusion du MP4. Les demandes de correction ou de retrait sont bienvenues.

Les droits sur les propos et articles restent ceux de leurs ayants droit. `LICENSE-CODE.md` concerne uniquement le code et la mise en forme originale.
