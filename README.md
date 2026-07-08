# Tariqi Legal AI

Assistant juridique RAG pour comprendre le code de la route marocain, les infractions, les amendes, le permis à points et les démarches liées aux contraventions.

Le projet est conçu pour répondre uniquement à partir de sources institutionnelles marocaines : Secrétariat Général du Gouvernement, Bulletin Officiel, Ministère du Transport et de la Logistique, NARSA, Khadamat NARSA et services publics liés au paiement.

> Tariqi Legal AI est une aide informative. Il ne remplace pas une décision administrative, une consultation juridique professionnelle ou les autorités compétentes.

## Modules

- Assistant juridique RAG avec citations.
- Calculateur d'amende et de points à partir d'un CSV structuré.
- Module "Que faire maintenant ?" pour paiement, déclaration et réclamation.
- Module permis à points.
- Espace sources et niveau de confiance.
- Pipeline d'indexation des PDF, HTML, TXT et jeux de données structurés.

## Structure

```text
tariqi-legal-ai/
├── app/
│   ├── main.py
│   ├── static/
│   └── templates/
├── data/
│   ├── raw/
│   ├── seed/
│   └── structured/
├── docs/
├── outputs/
├── scripts/
├── src/
│   └── tariqi/
├── tests/
├── vectorstore/
├── .env.example
├── requirements.txt
└── README.md
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Sur macOS/Linux :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copier `.env.example` vers `.env`, puis compléter les valeurs nécessaires.

```env
OPENAI_API_KEY=
OPENAI_GENERATION_MODEL=gpt-5.5
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TARIQI_EMBEDDING_BACKEND=hashing
```

Par défaut, le projet fonctionne avec un backend local `hashing`, sans clé API, pour les démonstrations et les tests. Pour utiliser les embeddings OpenAI, définir :

```env
TARIQI_EMBEDDING_BACKEND=openai
```

## Construire l'index

```bash
python scripts/build_index.py
```

L'index est écrit dans :

```text
vectorstore/tariqi_index.json
```

## Poser une question en CLI

```bash
python scripts/ask.py "Combien de points sont retirés pour un feu rouge ?"
```

## Lancer l'application web

```bash
python scripts/run_web.py
```

Puis ouvrir :

```text
http://127.0.0.1:8000
```

L'application web est construite avec FastAPI, HTML, CSS et JavaScript. Elle ne montre pas
les détails internes comme le backend d'embeddings ou l'état du LLM dans l'interface
utilisateur.

## Calculateur d'amende

```bash
python scripts/calculate_fine.py --infraction "feu rouge" --delay 24h
```

Le calculateur lit `data/structured/infractions_maroc.csv`. Le fichier contient une base initiale démonstrative et traçable, à enrichir avec les tableaux officiels complets.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Démonstration et rapport

- Guide de démonstration : `docs/DEMO.md`
- Rapport LaTeX : `docs/rapport_tariqi_legal_ai.tex`
- Architecture : `docs/ARCHITECTURE.md`
- Dictionnaire des données : `docs/DATA_DICTIONARY.md`

## Sources principales

Les sources suivies par le projet sont listées dans `data/raw/sources_manifest.json` et expliquées dans `docs/SOURCES.md`.

Niveaux utilisés :

- `A+` : source institutionnelle primaire ou texte juridique officiel.
- `A` : source institutionnelle pratique, par exemple Khadamat NARSA.
- `B` : source complémentaire institutionnelle, par exemple signalisation ou statistiques.
- `C` : source non utilisée pour répondre automatiquement.

## Format de réponse

Chaque réponse doit contenir :

- une réponse courte ;
- des détails ;
- les conséquences possibles ;
- la procédure utile ;
- les sources ;
- une remarque de prudence juridique ;
- un niveau de confiance.

## Licence et prudence

Le code du projet peut être adapté librement selon la licence choisie par le propriétaire du dépôt. Les documents officiels restent la propriété de leurs éditeurs institutionnels. Ne pas redistribuer de PDF officiel sans vérifier les conditions applicables.
