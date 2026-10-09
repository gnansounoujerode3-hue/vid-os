# Rapport de production

**Montage plein écran v2, inspiré des références « Our Work » — 9 octobre 2026.**

## Direction retenue

La correction de direction est intégrée : les références servent d’inspiration pour le **montage**, pas pour la mise en page de présentation. La v2 reste un portrait 9:16 plein écran, sans cadre portfolio ni écran avant/après. Elle alterne l’A-roll avec quatre cutaways graphiques courts — calendrier, « TIME → WHAT MATTERS », choix abstrait et pile de priorités — et renforce les titres cinétiques en violet/vert. La voix originale continue sous les inserts; les captions restent en anglais.

## Transcription

- Reconnaissance vocale locale PocketSphinx, modèle anglais; aucun service externe utilisé.
- Texte normalisé pour la ponctuation et quelques corrections contextuelles évidentes.
- Le rendu est un premier jet ASR, pas une transcription certifiée. À écouter et corriger avant diffusion : l’ouverture (**3–6 s**), le passage **18,7–21,3 s** et la formule **« X amount of time »**.
- Les sous-titres restent en anglais; aucun doublage/traduction française.

## Source et image

- Source : `sources/video-brut-1l-original.mp4` — 37,125 s, 720 × 1280, 24 i/s.
- Neuf silences resserrés et dix segments assemblés; recadrages jusqu’à environ 1,12×.
- Correction colorimétrique discrète préservée; les cutaways n’ajoutent pas de nouvelles paroles.

## Livrables et contrôles

- Nouveau montage social plein écran : `renders/video-brut-1l-motion-v2-en.mp4` — 35,750 s, H.264/AAC, 720 × 1280, 24 i/s, 8 544 235 octets.
- Première version conservée : `renders/video-brut-1l-pinterest-en.mp4`.
- Sidecars v2 anglais modifiables : `subtitles/video-brut-1l-motion-v2-en.ass` et `subtitles/video-brut-1l-motion-v2-en.srt`; cues et repères : `subtitles/captions-motion-v2-en.json`.
- Audio d’origine conservé; pas de musique, voix off ou effets sonores ajoutés.
- Décodage audio/vidéo complet validé (858 images vidéo); métadonnées et contrôles : `renders/motion-v2-probe.json`, `renders/motion-v2-verify.json`.
- Aperçu : `snapshots/motion-v2-contact-sheet.png`.

## Reproduction

Voir `README.md`. Le rendu v2 est généré par `compositions/render_social_motion.py` après `render_edit.py`.
