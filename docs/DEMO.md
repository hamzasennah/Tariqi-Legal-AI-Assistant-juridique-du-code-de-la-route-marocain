# Guide de démonstration

Ce guide donne un scénario simple pour présenter Tariqi Legal AI devant un jury.

## 1. Présenter le problème

Les citoyens ont souvent besoin de comprendre rapidement :

- une infraction routière ;
- le montant probable d'une amende ;
- le retrait de points ;
- une démarche de paiement, déclaration ou réclamation ;
- la source officielle utilisée.

Tariqi Legal AI répond à ce besoin avec un assistant RAG sourcé.

## 2. Construire l'index

```bash
python scripts/build_index.py
```

Message attendu :

```text
Index construit avec succès.
Documents : 16
Chunks : 16
Backend embeddings : hashing
```

## 3. Montrer une question RAG

```bash
python scripts/ask.py "Combien de points sont retirés pour un feu rouge ?"
```

À montrer :

- réponse courte ;
- source Khadamat NARSA ;
- tableau officiel des infractions et délits ;
- prudence juridique.

## 4. Montrer le calculateur

```bash
python scripts/calculate_fine.py --infraction "feu rouge" --delay 24h
```

À montrer :

- montant indicatif ;
- points retirés ;
- classe ;
- source officielle.

## 5. Montrer l'application web

```bash
python scripts/run_web.py
```

Puis ouvrir `http://127.0.0.1:8000`.

Pages à présenter :

- Assistant juridique ;
- Calculateur d'amende ;
- Que faire maintenant ? ;
- Sources.

## 6. Montrer les tests

```bash
pytest
```

Résultat attendu :

```text
9 passed
```

## 7. Phrase de conclusion

Tariqi Legal AI ne remplace pas les autorités ni un juriste. Il fournit une aide claire,
structurée et sourcée à partir de sources institutionnelles marocaines.
