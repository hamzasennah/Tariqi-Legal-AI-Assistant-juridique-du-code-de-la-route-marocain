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
app/                    Application web FastAPI, templates HTML et assets statiques
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
- `answerer.py` : réponse structurée avec LLM si disponible, sinon fallback local spécialisé.
- `calculator.py` : calculateur d'amendes et points.
- `procedures.py` : guides pratiques paiement, déclaration, réclamation.
- `pipeline.py` : construction complète de l'index.

## Choix important

Le dépôt contient un index JSON simple au lieu d'imposer FAISS ou ChromaDB directement. Cette décision rend le projet exécutable sur Windows, Linux et macOS sans compilation native. Pour une version production, `requirements-faiss.txt` prépare l'installation de FAISS.

L'interface utilisateur est servie par FastAPI avec des routes API séparées :

- `GET /` : application web ;
- `POST /api/ask` : assistant juridique ;
- `POST /api/calculate` : calculateur d'amende ;
- `GET /api/procedure` : recherche de procédure ;
- `GET /api/sources` : manifeste des sources.

## Garde-fous

- Réponse limitée aux passages retrouvés.
- Affichage obligatoire des sources.
- Refus ou prudence si le score est faible.
- Filtrage des passages sous le seuil de pertinence.
- Refus automatique des questions trop courtes ou sans ancrage lexical suffisant dans les sources.
- Contrôle de couverture : le passage doit expliquer une part suffisante des mots importants de la question.
- Contrôle du bruit : si la question mélange des termes non couverts par la source, l'assistant refuse au lieu de répondre sur un seul mot-clé.
- Retrieval hybride : les candidats viennent de l'index vectoriel et d'un filtre lexical, puis sont fusionnés et rerankés.
- Routage de réponse : les questions explicatives utilisent d'abord les passages juridiques, alors que les questions de montant, points ou sanction peuvent utiliser le CSV structuré.
- Mention claire : information générale, non conseil juridique définitif.
- Priorité aux sources `A+` et `A`.
