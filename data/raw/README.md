# Dossier `data/raw`

Ce dossier est prévu pour recevoir les PDF, HTML et TXT téléchargés depuis les sources institutionnelles.

Les fichiers bruts ne sont pas versionnés par défaut pour éviter de publier des copies de documents officiels sans vérifier les conditions de réutilisation.

Utilisation recommandée :

```bash
python scripts/download_sources.py
python scripts/build_index.py --include-raw
```

Le manifeste des sources se trouve dans `data/raw/sources_manifest.json`.
