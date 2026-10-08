# Rapport de production — Moteur d’Acquisition 360°

## Livrable

- `renders/moteur-acquisition-360-vertical.mp4`
- 34 s · vertical 9:16 · 1080×1920 · 30 fps
- H.264 High / `yuv420p` · AAC-LC stéréo, 48 kHz
- Vidéo sans voix off, comme demandé; ambiance électronique instrumentale créée localement.

## Contrôles effectués

- FFprobe lit le fichier et confirme les dimensions, cadence, durée ainsi que les pistes vidéo et audio.
- Le contrôle `verify_render.py` a réussi toutes ses vérifications bloquantes.
- Décodage complet par FFmpeg effectué sans erreur.
- Contrôle de niveau audio EBU R128 : intégrée `-16.1 LUFS`, crête vraie `-4.0 dBFS`; pas d’écrêtage détecté.
- Planche de contact inspectée : texte principal lisible, contraste élevé, composition verticale cohérente, CTA visible.
- Copie recoupée avec les affirmations présentes sur la page publique : les trois agents, le lien public, les demandes qualifiées, les sorties de contenu et les canaux de prospection.
- Aucun chiffre de performance ou résultat client n’a été inventé. L’offre est formulée comme gratuite **pendant la phase de test**, et non comme gratuite à vie.

## Identité visuelle et limites

La page et le manifeste web ont été consultés. Le manifeste confirme `theme_color: #0A0B0E`, repris comme fond du film. Les captures, CSS, logo séparé, typographie et couleurs d’accent n’étaient pas disponibles; l’utilisateur a choisi une reconstitution indicative. Les écrans sont donc des schémas illustratifs basés sur le texte public et ne doivent pas être présentés comme des captures réelles. Le vert clair/lilas et la police Instrument Sans sont des choix de production, pas des couleurs ou polices certifiées de la marque. Le wordmark est uniquement typographique.

Pour une version strictement conforme au pixel près, remplacer les compositions illustratives par des captures de la vraie interface et fournir les autres éléments du guide de marque.

## Outils et provenance

Production locale selon le workflow `video-director`; composition Pillow + FFmpeg, faute de runtime HyperFrames installé dans ce workspace. Les formes et le son sont créés localement, sans service externe ni média stock. Les polices extraites du pack de skills sont publiées sous SIL Open Font License; références de licence incluses dans `assets/`.

Le son a été contrôlé par mesure; une écoute de monitoring sur haut-parleurs/casque reste recommandée avant publication. Aucun téléchargement de média utilisateur ou envoi vers un fournisseur externe n’a eu lieu.
