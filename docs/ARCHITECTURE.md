# Architecture de Tariqi Legal AI

## Objectif

Tariqi Legal AI est une application RAG orientée droit routier marocain. Elle doit aider un citoyen à comprendre une règle, une infraction, une amende, le permis à points ou une procédure, en citant les sources utilisées.

Le projet sépare volontairement deux modes :

- `RAG` : recherche de passages officiels et réponse structurée.
- `CSV structuré` : calcul d'amendes et de points quand une donnée tabulaire fiable existe.

## Flux global

```text
Sources officielles
    -> extraction
    -> nettoyage
    -> découpage en chunks
    -> enrichissement par métadonnées
    -> embeddings
    -> index vectoriel
    -> retrieval
    -> réponse avec citations
```

## Couches techniques

```text
app/                    Interface Streamlit
scripts/                Commandes CLI
src/tariqi/             Code métier
data/raw/               Sources téléchargées localement, non versionnées
data/seed/              Corpus démonstratif versionné
data/structured/        CSV d'infractions et procédures
vectorstore/            Index généré, non versionné
outputs/                Résultats d'évaluation, non versionnés
docs/                   Documentation projet
tests/                  Tests unitaires
```

## Modules Python

- `schemas.py` : objets de données du projet.
- `source_registry.py` : chargement du manifeste de sources.
- `loaders.py` : extraction depuis TXT, HTML et PDF.
- `cleaning.py` : nettoyage du texte.
- `chunking.py` : découpage contrôlé.
- `embeddings.py` : backend local ou OpenAI.
- `vector_store.py` : index JSON simple, portable et testable.
- `retriever.py` : recherche des passages pertinents.
- `answerer.py` : réponse structurée avec ou sans LLM.
- `calculator.py` : calculateur d'amendes et points.
- `procedures.py` : guides pratiques paiement, déclaration, réclamation.
- `pipeline.py` : construction complète de l'index.

## Choix important

Le dépôt contient un index JSON simple au lieu d'imposer FAISS ou ChromaDB directement. Cette décision rend le projet exécutable sur Windows, Linux et macOS sans compilation native. Pour une version production, `requirements-faiss.txt` prépare l'installation de FAISS.

## Garde-fous

- Réponse limitée aux passages retrouvés.
- Affichage obligatoire des sources.
- Refus ou prudence si le score est faible.
- Mention claire : information générale, non conseil juridique définitif.
- Priorité aux sources `A+` et `A`.
