# Vidéo marketing — Moteur d’Acquisition 360°

Livrable principal : `renders/moteur-acquisition-360-vertical.mp4`.

- Brief : `BRIEF.md`
- Storyboard / texte écran : `STORYBOARD.md`
- Rapport de vérification : `report.md`
- Source reproductible : `compositions/render_video.py`
- Ambiance audio originale : `audio/score.wav`
- Contrôle visuel : `snapshots/contact-sheet.png` et images clés

Les écrans sont une reconstitution illustrative fondée sur le texte public du site; ils ne sont pas des captures de l’application. La couleur de fond `#0A0B0E` provient du `theme_color` de son manifeste web. Les accents et la typographie n’ont pas pu être vérifiés sans captures ou guide de marque.

Pour regénérer dans un environnement avec Python 3.10+, FFmpeg, Pillow et imageio-ffmpeg installés :

```bash
python3 compositions/render_video.py
```
