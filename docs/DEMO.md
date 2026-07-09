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
Documents : 22
Chunks : 22
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

## 5. Montrer le refus RAG

Entrer une question volontairement inutile :

```text
cc?
```

Résultat attendu :

- confiance faible ;
- aucune source pertinente ;
- message de refus au lieu d'une réponse inventée.

Montrer ensuite une question mélangée qui contient un vrai mot-clé mais pas une vraie question juridique :

```text
pourquoi une voiture noire est interdite par police feu rouge?
```

Résultat attendu :

- refus ;
- aucune source ;
- explication que le contexte récupéré n'est pas assez solide.

## 6. Montrer une question réaliste mal formulée

Entrer :

```text
quelle sont les cas qui me permet de stopper dans une autoroute sans avoir des problemes avec police?
```

À montrer :

- récupération du décret n° 2-10-420 ;
- réponse sur la nécessité absolue ;
- source affichée ;
- pas de réponse hors sujet sur la déclaration ou le paiement.

## 7. Montrer l'application web

```bash
python scripts/run_web.py
```

Puis ouvrir `http://127.0.0.1:8000`.

Pages à présenter :

- Assistant juridique ;
- Calculateur d'amende ;
- Que faire maintenant ? ;
- Sources.

## 8. Montrer les tests

```bash
pytest
```

Résultat attendu :

```text
28 passed
```

## 9. Phrase de conclusion

Tariqi Legal AI ne remplace pas les autorités ni un juriste. Il fournit une aide claire,
structurée et sourcée à partir de sources institutionnelles marocaines.
