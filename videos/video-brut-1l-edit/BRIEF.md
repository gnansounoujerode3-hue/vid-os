# Brief de montage — « vidéo brut 1L »

- **Objectif :** rendre la prise de parole plus rythmée tout en gardant le propos et l’identité naturelle de la prise source.
- **Entrée faisant foi :** `sources/video-brut-1l-original.mp4`, récupérée sur le dépôt principal de l’utilisateur (`vid-os`, branche `main`).
- **Livrable :** MP4 vertical prêt à partager, dans `renders/`.
- **Format :** 720 × 1280 (9:16), 24 i/s, durée cible ≈ 36 s; la résolution et la cadence sources sont conservées.
- **Direction visuelle :** montage face caméra sobre et dynamique; coupes resserrées sur les silences, alternance de plans larges et de punch-ins mesurés, légère correction de contraste/saturation. Préserver le décor bleu-violet et la lumière chaude.
- **Son :** conserver uniquement l’audio d’origine, sans musique ajoutée ni voix off. Aucun sous-titre, aucune transcription et aucune analyse sémantique des paroles. Les coupes reposent uniquement sur les niveaux de silence mesurés.
- **Provenance / confidentialité :** traitement local avec FFmpeg; aucun envoi audio/vidéo à un service externe.
- **Critères d’acceptation :** image et son synchronisés; pas de flux de sous-titres; vidéo décodable; MP4 H.264/AAC, lecture verticale fluide; vérification visuelle et audio après export.
- **Outil :** script reproductible `compositions/render_edit.py`, FFmpeg/FFprobe.
