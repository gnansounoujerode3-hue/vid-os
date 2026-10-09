# Brief de montage — « vidéo brut 1L »

- **Objectif :** transformer la prise brute en vidéo sociale verticale, rythmée et visuellement soignée.
- **Entrée :** `sources/video-brut-1l-original.mp4`, récupérée sur le dépôt principal de l’utilisateur (`vid-os`, branche `main`).
- **Livrable principal :** `renders/video-brut-1l-pinterest-en.mp4`.
- **Format :** 720 × 1280 (9:16), 24 i/s, 35,75 s.
- **Direction visuelle :** finition éditoriale inspirée des vidéos Pinterest/social premium; conserver le décor bleu-violet et la lumière chaude; jump-cuts et punch-ins mesurés; titre animé, repères de chapitre, barre de progression, accents violet/or et sous-titres cinétiques.
- **Sous-titres :** en anglais, dans la langue parlée, non traduits en français; intégrés à l’image. Le premier jet provient d’une reconnaissance vocale locale PocketSphinx. Les formulations vers 3–6 s et 18,7–21,3 s, ainsi que « X amount of time », restent à vérifier avant diffusion publique ou payante.
- **Son :** audio source conservé; pas de musique ajoutée, pas de voix off.
- **Provenance / confidentialité :** traitement local; aucun envoi audio/vidéo à un service externe.
- **Critères :** H.264/AAC, vertical fluide, paroles sous-titrées en anglais, synchronisation conforme à la timeline, décodage complet validé.
- **Outils :** `compositions/render_edit.py` puis `compositions/render_pinterest.py`; FFmpeg/FFprobe.
