# Brief de montage — « vidéo brut 1L »

- **Objectif :** transformer la prise brute en vidéo sociale verticale, dynamique et visuellement soignée, puis préparer une présentation portfolio inspirée des références « Our Work » ajoutées sur `main`.
- **Entrée :** `sources/video-brut-1l-original.mp4`.
- **Livrables :** `renders/video-brut-1l-pinterest-en.mp4` (montage social plein écran) et `renders/video-brut-1l-our-work-en.mp4` (comparatif portfolio).
- **Format :** 720 × 1280 (9:16), 24 i/s; 35,75 s.
- **Direction du montage social :** décor bleu-violet et lumière chaude préservés; coupes et punch-ins mesurés; titre, chapitres, progression, callouts, mots-clés or et sous-titres cinétiques.
- **Direction portfolio :** fond papier clair, fenêtre principale arrondie pour le montage final, petite fenêtre synchronisée pour le cut source, labels avant/après et signature graphique générique; ne pas reprendre le logo ou le handle des références.
- **Sous-titres :** anglais uniquement, sans traduction française; intégrés à l’image. Le premier jet provient d’une reconnaissance vocale locale PocketSphinx. Les formulations vers 3–6 s et 18,7–21,3 s, ainsi que « X amount of time », restent à vérifier avant diffusion publique ou payante.
- **Son :** audio source conservé; pas de musique ajoutée, pas de voix off.
- **Provenance / confidentialité :** traitement local; aucun envoi audio/vidéo à un service externe.
- **Critères :** H.264/AAC, vertical 9:16, synchronisation cohérente entre les deux fenêtres, sous-titres anglais, décodage complet validé.
- **Outils :** `compositions/render_edit.py`, `compositions/render_pinterest.py`, `compositions/render_our_work.py`; FFmpeg/FFprobe. `build_our_work_assets.py` requiert Pillow pour modifier/régénérer le cadre.
