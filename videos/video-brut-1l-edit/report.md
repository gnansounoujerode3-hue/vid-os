# Rapport de production

**Version sous-titrée et motion design rendue — 9 octobre 2026.**

## Direction retenue

Après demande de l’utilisateur, la version sans sous-titres a été remplacée par une version sous-titrée **en anglais**, sans traduction française. Le montage conserve les rushes de la prise source, resserre les pauses, alterne les recadrages et ajoute un habillage éditorial social : titre d’ouverture, progression/chapitres, callouts, mots-clés dorés et sous-titres cinétiques. Le décor bleu-violet et la lumière chaude sont préservés.

## Transcription

- Reconnaissance vocale locale PocketSphinx, modèle anglais; aucun service externe utilisé.
- Texte normalisé pour la ponctuation et quelques corrections contextuelles évidentes.
- La formulation de l’ouverture, environ **3–6 s de la source**, a une confiance ASR plus faible. Le rendu est exploitable comme premier jet, mais cette petite portion doit être écoutée et corrigée avant une diffusion publique ou payante.
- Les sous-titres restent en anglais; aucun doublage/traduction française.

## Source et image

- Source : `sources/video-brut-1l-original.mp4` — 37,125 s, 720 × 1280, 24 i/s.
- Neuf silences resserrés et dix segments assemblés; recadrages jusqu’à environ 1,12×.
- Correction colorimétrique discrète : contraste +3,5 %, saturation +4,5 %.

## Livrable et contrôles

- MP4 final : `renders/video-brut-1l-pinterest-en.mp4` — 35,750 s, H.264/AAC, 720 × 1280, 24 i/s, audio stéréo 44,1 kHz; sous-titres brûlés dans l’image.
- Sidecars anglais éditables : `subtitles/video-brut-1l-en.ass` (style) et `subtitles/video-brut-1l-en.srt` (texte/minutage).
- Audio d’origine conservé, sans musique ni voix ajoutée; métriques de la base : −14,6 LUFS intégrés, true peak −0,8 dBFS.
- Décodage vidéo et audio complet vérifié; un flux H.264 et un flux AAC, aucun flux texte séparé.
- Planche de contact finale inspectée : `snapshots/final-contact-sheet.png`.
- Vérifications techniques : `renders/probe.json` et `renders/verify.json`.

## Reproduction

Voir `README.md`; les deux scripts de rendu sont dans `compositions/`.
