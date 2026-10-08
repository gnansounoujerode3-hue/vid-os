# Rapport de production

**Statut : montage terminé — 9 octobre 2026.**

## Décision de montage

Version dynamique sans sous-titres. L’utilisateur a demandé de conserver le son d’origine et de dynamiser l’image, sans analyser ni retranscrire les paroles. Aucun service externe d’ASR n’a été utilisé.

## Source et montage

- Source : `sources/video-brut-1l-original.mp4` — 37,125 s, 720 × 1280, 24 i/s.
- Source vidéo H.264 High; audio AAC HE-AACv2 stéréo, 44,1 kHz.
- Neuf silences repérés par `silencedetect` (seuil −34 dB, durée minimale 0,24 s) ont été resserrés, avec une brève respiration préservée autour des coupes.
- Dix segments assemblés; recadrages alternés jusqu’à environ 1,12× pour créer un rythme de jump-cuts tout en gardant le visage, le micro et les gestes dans le cadre.
- Correction discrète : contraste +3,5 %, saturation +4,5 %; aucun titrage ni sous-titres.
- Audio d’origine conservé, sans musique ni voix ajoutée. Aucun mot n’a été identifié ou retranscrit.
- Travail local avec FFmpeg; aucune donnée envoyée à un service externe.

## Livrable et contrôles

- Rendu : `renders/video-brut-1l-dynamique.mp4` — **35,750 s**, H.264/AAC, 720 × 1280, 24 i/s, stéréo 44,1 kHz, 8,29 Mo.
- FFprobe confirme un seul flux vidéo et un flux audio, aucun flux de sous-titres.
- Contrôles automatisés : fichier lisible, format/dimensions/fréquence/durée/audio conformes; décodage complet FFmpeg réussi.
- Audio final : −14,6 LUFS intégrés; true peak −0,8 dBFS (audio source : −14,6 LUFS, −0,7 dBFS).
- La planche finale `snapshots/final-contact-sheet.png` a été inspectée visuellement.
- Vérification : `renders/verify.json`; métadonnées : `renders/probe.json`; timeline exacte : `edit/timeline.json`.

## Reproduction

Lancer `python3 videos/video-brut-1l-edit/compositions/render_edit.py` depuis la racine du dépôt, avec FFmpeg et FFprobe installés et accessibles dans le `PATH`.
