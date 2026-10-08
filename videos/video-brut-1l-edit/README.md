# Montage « vidéo brut 1L »

Projet de montage vertical local de la prise source située dans `sources/`.

- Brief : [`BRIEF.md`](BRIEF.md)
- Plan de montage : [`STORYBOARD.md`](STORYBOARD.md)
- Rapport : [`report.md`](report.md)
- Script : [`compositions/render_edit.py`](compositions/render_edit.py)
- Rendu final : [`renders/video-brut-1l-dynamique.mp4`](renders/video-brut-1l-dynamique.mp4)

Pour reconstruire le rendu, installer FFmpeg/FFprobe et lancer depuis la racine du dépôt :

```bash
python3 videos/video-brut-1l-edit/compositions/render_edit.py
```

Le script utilise uniquement la détection de silences déjà mesurée, des recadrages et l’audio présent dans le MP4. Il ne génère pas de transcription ou de sous-titres et n’ajoute pas de musique.
