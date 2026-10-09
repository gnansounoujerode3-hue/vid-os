# Brief de montage — « vidéo brut 1L »

- **Objectif :** améliorer le montage social plein écran en s’inspirant des choix de montage des vidéos « Our Work » : rythme plus varié, mots-clés expressifs et inserts graphiques liés au discours — sans reprendre leur cadre de présentation.
- **Entrée :** `sources/video-brut-1l-original.mp4`.
- **Livrables :** `renders/video-brut-1l-motion-v2-en.mp4` (nouvelle version plein écran) et `renders/video-brut-1l-pinterest-en.mp4` (première version conservée).
- **Format :** 720 × 1280 (9:16), 24 i/s, 35,75 s.
- **Montage :** l’A-roll du locuteur reste plein écran; quatre cutaways graphiques courts alternent avec lui (calendrier, temps → ce qui compte, choix, pile de priorités), avec réapparition sur la voix. Punch-ins, titres cinétiques et accents violet/vert renforcés.
- **Sous-titres :** en anglais uniquement, intégrés à l’image. Premier jet PocketSphinx local; formulations vers 3–6 s et 18,7–21,3 s, et « X amount of time », à vérifier avant diffusion.
- **Son :** voix originale conservée; ni voix off, ni musique, ni effets sonores ajoutés.
- **Provenance / confidentialité :** traitement local; aucun envoi audio/vidéo à un service externe.
- **Critères :** H.264/AAC, vertical fluide, narration synchronisée aux inserts, sous-titres anglais, décodage complet validé.
- **Outils :** `compositions/render_edit.py` puis `compositions/render_social_motion.py`; FFmpeg/FFprobe. `render_pinterest.py` reconstruit la première version.
