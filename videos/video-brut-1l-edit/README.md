# Montage « vidéo brut 1L »

Deux exports sont disponibles : le **montage social plein écran** en anglais, puis une **présentation portfolio “Our Work”** qui compare le cut source au montage fini. La voix originale est conservée; aucun sous-titre français n’est ajouté.

- Montage social plein écran : [`renders/video-brut-1l-pinterest-en.mp4`](renders/video-brut-1l-pinterest-en.mp4)
- Présentation “Our Work” avant/après : [`renders/video-brut-1l-our-work-en.mp4`](renders/video-brut-1l-our-work-en.mp4)
- Fichiers de sous-titres anglais : [`subtitles/video-brut-1l-en.ass`](subtitles/video-brut-1l-en.ass) (style/motion) et [`subtitles/video-brut-1l-en.srt`](subtitles/video-brut-1l-en.srt) (texte/minutage).
- Texte et minutage des captions : [`subtitles/captions-en.json`](subtitles/captions-en.json)
- Base de montage sans captions : `edit/video-brut-1l-cut-base.mp4`.
- Cadre portfolio personnalisable : `assets/our-work-layout.png` et masques des fenêtres vidéo.

## Reconstruction

Installer FFmpeg/FFprobe, puis lancer depuis la racine du dépôt :

```bash
python3 videos/video-brut-1l-edit/compositions/render_edit.py
python3 videos/video-brut-1l-edit/compositions/render_pinterest.py
python3 videos/video-brut-1l-edit/compositions/render_our_work.py
```

Pour régénérer le cadre et ses masques après modification du graphisme, installer Pillow (`python3 -m pip install Pillow`), puis lancer `compositions/build_our_work_assets.py`.

Le cadre portfolio reprend les principes visuels des références “Our Work” (fond éditorial clair, comparaison synchronisée source/final, fenêtres arrondies, labels), avec un habillage générique propre à ce projet; le logo et le handle des références ne sont pas repris. La petite fenêtre montre le cut sans captions; la fenêtre principale montre le montage anglais.

Les sous-titres sont générés à partir d’une reconnaissance vocale PocketSphinx effectuée localement. Aucun audio n’est transmis à un service externe. Le premier jet anglais comporte des formulations à confirmer vers 3–6 s et 18,7–21,3 s, ainsi que « X amount of time »; les vérifier avant diffusion publique/payante.
