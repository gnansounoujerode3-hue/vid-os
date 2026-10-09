# Montage « vidéo brut 1L »

Montage vertical à partir de la prise située dans `sources/`. La version livrable intègre des sous-titres **en anglais**, non traduits, ainsi qu’un motion design éditorial aux accents violet et or.

- Brief : [`BRIEF.md`](BRIEF.md)
- Storyboard : [`STORYBOARD.md`](STORYBOARD.md)
- Rapport : [`report.md`](report.md)
- Rendu sous-titré : [`renders/video-brut-1l-pinterest-en.mp4`](renders/video-brut-1l-pinterest-en.mp4)
- Fichiers de sous-titres anglais : [`subtitles/video-brut-1l-en.ass`](subtitles/video-brut-1l-en.ass) (style/motion) et [`subtitles/video-brut-1l-en.srt`](subtitles/video-brut-1l-en.srt) (texte/minutage).
- Texte et minutage des captions : [`subtitles/captions-en.json`](subtitles/captions-en.json)
- Base de montage avant titrage : `edit/video-brut-1l-cut-base.mp4`.

## Reconstruction

Installer FFmpeg/FFprobe, puis lancer depuis la racine du dépôt :

```bash
python3 videos/video-brut-1l-edit/compositions/render_edit.py
python3 videos/video-brut-1l-edit/compositions/render_pinterest.py
```

Les sous-titres sont générés à partir d’une reconnaissance vocale PocketSphinx effectuée localement. Aucun audio n’est transmis à un service externe. Le premier jet anglais comporte un passage de confiance plus faible vers 3–6 s; écouter et confirmer ce court passage avant une diffusion publique/payante.
