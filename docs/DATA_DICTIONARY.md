# Dictionnaire des données

## `data/seed/legal_corpus.jsonl`

Une ligne JSON correspond à un document ou extrait exploitable par le RAG.

Champs :

- `id` : identifiant unique du passage source.
- `source_id` : identifiant dans `data/raw/sources_manifest.json`.
- `authority` : organisme éditeur.
- `title` : titre de la source.
- `document` : type ou nom du document.
- `article_or_section` : article, rubrique ou section.
- `date_source` : date connue ou date de consultation.
- `language` : langue principale.
- `theme` : thème métier.
- `trust_level` : niveau de confiance.
- `url` : lien de consultation.
- `text` : contenu utilisé par le RAG.

## `data/structured/infractions_maroc.csv`

CSV utilisé par le calculateur d'amende et de points.

Champs :

- `id_infraction` : identifiant stable.
- `nom_infraction` : nom compréhensible de l'infraction.
- `type_infraction` : contravention ou délit.
- `classe` : classe de l'infraction si applicable.
- `montant_24h`, `montant_15j`, `montant_30j` : montants en dirhams selon délai quand l'ATF est applicable.
- `points_retires` : points retirés selon le tableau officiel.
- `sanction_possible` : résumé de l'effet possible.
- `source`, `document`, `article_ou_page`, `date_source`, `source_url` : traçabilité.
- `confiance` : niveau de confiance de la ligne.
- `notes` : prudence ou précision.

## `data/structured/procedures.json`

Guides pratiques utilisés par le module "Que faire maintenant ?".

Champs :

- `id` : identifiant.
- `title` : titre de la procédure.
- `trigger_keywords` : mots-clés de détection.
- `summary` : résumé court.
- `steps` : étapes à afficher.
- `source_id` et `url` : source.
- `warning` : prudence juridique.
