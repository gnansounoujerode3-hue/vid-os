# Rapport de production

**Montage social sous-titré et variante portfolio “Our Work” — 9 octobre 2026.**

## Direction retenue

Le montage social conserve la prise et la voix d’origine, resserre les pauses, alterne les recadrages et ajoute un habillage éditorial. À la demande de l’utilisateur, une seconde variante s’inspire des deux références « Our Work » présentes sur `main` : grand panneau du rendu final, petite fenêtre synchronisée du cut source, fond papier clair, cadres arrondis et labels de montage. Le langage graphique est créé pour ce projet; le logo et le handle des références ne sont pas repris.

## Transcription

- Reconnaissance vocale locale PocketSphinx, modèle anglais; aucun service externe utilisé.
- Texte normalisé pour la ponctuation et quelques corrections contextuelles évidentes.
- Le rendu est un premier jet ASR, pas une transcription certifiée. À écouter et corriger avant diffusion : l’ouverture (**3–6 s**), le passage **18,7–21,3 s** et la formule **« X amount of time »**.
- Les sous-titres restent en anglais; aucun doublage/traduction française.

## Source et image

- Source : `sources/video-brut-1l-original.mp4` — 37,125 s, 720 × 1280, 24 i/s.
- Neuf silences resserrés et dix segments assemblés; recadrages jusqu’à environ 1,12×.
- Correction colorimétrique discrète : contraste +3,5 %, saturation +4,5 %.
- La variante portfolio compare en synchronisation la base sans captions et le montage social complet; l’audio est pris une seule fois depuis le montage final.

## Livrables et contrôles

- Montage social plein écran : `renders/video-brut-1l-pinterest-en.mp4` — 35,750 s, H.264/AAC, 720 × 1280, 24 i/s; sous-titres brûlés dans l’image.
- Présentation portfolio : `renders/video-brut-1l-our-work-en.mp4` — 35,750 s, H.264/AAC, 720 × 1280, 24 i/s; voix originale conservée.
- Sidecars anglais éditables : `subtitles/video-brut-1l-en.ass` (style) et `subtitles/video-brut-1l-en.srt` (texte/minutage).
- Audio d’origine conservé, sans musique ni voix ajoutée; métriques de la base : −14,6 LUFS intégrés, true peak −0,8 dBFS.
- Décodage vidéo et audio complet vérifié pour les deux versions; pas de flux texte séparé, captions brûlées.
- Planche de contact de la variante portfolio : `snapshots/our-work-contact-sheet.png`.
- Métadonnées/contrôles : `renders/probe.json`, `renders/verify.json`, `renders/our-work-probe.json` et `renders/our-work-verify.json`.

## Reproduction

Voir `README.md`; les scripts de rendu et de cadre sont dans `compositions/`.
