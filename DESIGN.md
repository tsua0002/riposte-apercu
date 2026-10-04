# Direction visuelle — carnet de préparation

Direction approuvée : populaire, home-made et chaleureuse, sans simuler un site officiel de La Riposte. L’IA est assumée dans la méthode ; la composition ne doit pas évoquer un dashboard SaaS.

## Monde visuel
- Papier chaud (#f3efe5), encre (#201d19), rouge (#a92c20), jaune ponctuel (#e8b83f).
- Grain PNG local très discret, sans animation. Aucun asset distant au chargement.
- Literata 600 auto-hébergée pour les grands titres (licence OFL dans assets/fonts). Typographie système pour les textes et contrôles ; monospace réservé aux horodatages et empreintes.
- Entrées de presse ouvertes, séparateurs fins, horodatages en marge sur desktop puis au-dessus sur mobile. Pas de cartes répétitives, gradient, stickers ou inclinaisons artificielles.

## Information et interaction
- Mode principal : Read ; démonstration du lecteur : Operate.
- Source, date et statut de recherche visibles. Les incertitudes détaillées restent dans « Notes de recherche ».
- Petite icône SVG pour une explication courte, sans lien interactif dans l’infobulle. Accès souris, clavier et clic/touch ; fermeture par Échap et clic extérieur.
- Longues notes et liens : dépliables HTML natifs. Sans JS, la petite note reste affichée et les dépliables fonctionnent.
- Statut non officiel visible, consentement YouTube conservé, aucune transcription intégrale publique.
- Cibles principales d’au moins 44 px, focus visible, lien d’évitement et version imprimable.

## Construction
Modifier scripts/build_preview.py, assets/style.css et les modules, puis régénérer index.html. Ne jamais copier l’archive privée dans ce dépôt. La police et le grain sont des ressources publiques locales, sans dépendance runtime supplémentaire.
