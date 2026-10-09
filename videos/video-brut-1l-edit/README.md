# Montage « vidéo brut 1L »

Deux versions plein écran en anglais sont conservées : le premier montage social et une **version motion v2**, enrichie de cutaways graphiques inspirés du rythme et des inserts des références « Our Work ». La v2 reste une vidéo sociale verticale classique — pas de cadre portfolio ni de comparaison avant/après. La voix originale est conservée et aucun sous-titre français n’est ajouté.

- **Version améliorée, plein écran :** [`renders/video-brut-1l-motion-v2-en.mp4`](renders/video-brut-1l-motion-v2-en.mp4)
- Première version plein écran : [`renders/video-brut-1l-pinterest-en.mp4`](renders/video-brut-1l-pinterest-en.mp4)
- Sous-titres anglais v2 : [`subtitles/video-brut-1l-motion-v2-en.ass`](subtitles/video-brut-1l-motion-v2-en.ass) (style et animations) et [`subtitles/video-brut-1l-motion-v2-en.srt`](subtitles/video-brut-1l-motion-v2-en.srt) (texte/minutage).
- Texte, minutage et repères des inserts : [`subtitles/captions-motion-v2-en.json`](subtitles/captions-motion-v2-en.json)
- Sous-titres de la première version : `subtitles/video-brut-1l-en.ass` et `.srt`.
- Base sans sous-titres : `edit/video-brut-1l-cut-base.mp4`.

## Reconstruction

Installer FFmpeg/FFprobe, puis lancer depuis la racine du dépôt :

```bash
python3 videos/video-brut-1l-edit/compositions/render_edit.py
python3 videos/video-brut-1l-edit/compositions/render_social_motion.py
```

`render_pinterest.py` reconstruit le premier montage plein écran. La v2 alterne le plan du locuteur avec quatre inserts plein écran synchronisés à la voix : grille de calendrier, passage « TIME → WHAT MATTERS », cartes de choix abstraites, puis pile de priorités. Les titres cinétiques, les mots-clés violets/verts et les sous-titres anglais sont intégrés au même cadre vertical. Aucun texte français, nouvelle voix, musique ou logo de référence n’est ajouté.

Les sous-titres sont générés à partir d’une reconnaissance vocale PocketSphinx effectuée localement; aucun audio n’est transmis à un service externe. Le premier jet anglais comporte des formulations à confirmer vers 3–6 s et 18,7–21,3 s, ainsi que « X amount of time »; les vérifier avant diffusion publique/payante.
