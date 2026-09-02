# Heuristique d'évaluation

## Rôle de l'heuristique

Une recherche exhaustive jusqu'à la fin d'une partie de Gomoku est impossible dans le temps accordé à l'IA. Lorsque la recherche atteint sa profondeur limite, le moteur doit donc estimer laquelle des positions obtenues est la plus favorable.

Cette estimation est réalisée par `Board::evaluation` dans `src/cpp/engine.cpp`. Un score positif favorise le joueur 1 et un score négatif favorise le joueur 2. Lorsque la recherche demande le point de vue du joueur 2, le signe est inversé. Cette convention permet au Negamax d'utiliser la même fonction pour les deux joueurs.

Les victoires ne sont pas de simples valeurs heuristiques. Elles utilisent le score spécial `WinScore = 10 000 000`, supérieur à tous les motifs ordinaires, afin qu'une victoire forcée soit toujours préférée à un avantage positionnel.

## Représentation d'une ligne

Le moteur évalue toutes les lignes horizontales, verticales et diagonales du plateau. Pour évaluer une ligne du point de vue d'un joueur, chaque intersection est encodée ainsi :

| Code | Signification |
|---:|---|
| `0` | case vide |
| `1` | pierre du joueur évalué |
| `3` | pierre adverse ou bord du plateau |

Le même motif peut donc servir aux deux joueurs. Par exemple, `011110` représente quatre pierres consécutives avec deux extrémités libres. Le code `3` permet de traiter de la même manière une pierre adverse et un bord, puisqu'ils ferment tous les deux l'alignement.

Cette conversion est effectuée dans `Board::scoreLine`. La fonction parcourt chaque sous-chaîne de longueur maximale 7 et consulte sa valeur dans une table préconstruite.

## Motifs reconnus

Les 28 motifs et leurs poids sont déclarés dans `HeuristicPatterns`. Les catégories principales sont les suivantes :

| Exemple | Situation | Score indicatif |
|---|---|---:|
| `11111` | cinq aligné | 2 000 000 |
| `011110` | quatre ouvert | 100 000 |
| `101110`, `011101` | quatre cassé | 50 000 |
| `0110110` | autre quatre cassé ouvert | 40 000 |
| `311110`, `011113` | quatre fermé d'un côté | 10 000 |
| `01110` | trois ouvert | 5 000 |
| `010110`, `011010` | trois cassé ouvert | 3 000 |
| `0110`, `01010` | deux ouvert ou cassé | 300 |
| `010` | pierre avec espace disponible | 20 |

Les variantes préfixées ou suffixées par `3` représentent des formes bloquées. Elles reçoivent une valeur plus faible que leurs équivalents ouverts, car elles offrent moins de continuations gagnantes.

Les poids ne représentent pas une probabilité. Ils imposent une hiérarchie tactique : un quatre vaut beaucoup plus qu'un trois, un trois vaut plus qu'un deux, et un cinq domine les motifs non terminaux. Les tests de `testPatternHeuristic` vérifient notamment qu'un quatre ouvert est mieux noté qu'un quatre fermé et qu'un trois cassé dépasse un deux ouvert.

## Table de consultation

Comparer des chaînes de caractères à chaque nœud serait coûteux. `heuristicScoreTable` transforme une fois chaque motif en un entier en base 4 :

```text
code = code * 4 + valeur_de_la_case
```

La longueur et ce code donnent directement accès au score dans un tableau. Pendant la recherche, `scoreLine` construit le même code progressivement et effectue une consultation en temps constant. La table est créée une seule fois grâce à une variable `static` locale.

## Score des captures

L'évaluation positionnelle ajoute également la différence entre les compteurs de captures :

```text
(captures_joueur_1 - captures_joueur_2) × 15 000
```

Les compteurs sont exprimés en nombre de pierres. Une paire capturée vaut donc 30 000 points heuristiques. Cette valeur rend une capture importante sans lui permettre de dépasser une victoire réelle. Atteindre dix pierres capturées reste traité comme une condition terminale par les règles, et non comme une simple estimation.

## Calcul du score global

`Board::rebuildDerivedState` calcule initialement le score de toutes les lignes. Ensuite, lorsqu'un coup est joué ou annulé, seules les lignes traversant les intersections modifiées sont recalculées par `Board::refreshLines`. Le résultat est conservé dans `totalScore_`.

`Board::evaluation` combine alors :

```text
score des motifs + score des captures
```

La fonction `Board::fullEvaluation` recalcule volontairement tout le plateau. Elle sert de référence dans les tests afin de vérifier que le score incrémental reste exact après une suite de coups et d'annulations. Les détails de cette optimisation sont présentés dans `02_optimisations.md`.

## Utilisation pendant la recherche

L'heuristique intervient à deux endroits :

1. À profondeur zéro, `Engine::negamax` retourne `board.evaluation(player)`.
2. Dans `Engine::movePriority`, la variation d'évaluation produite par un coup aide à explorer d'abord les continuations prometteuses.

Elle ne décide donc pas seule du résultat. Les victoires, les menaces directes et les règles de capture sont vérifiées avant ou pendant la recherche. L'heuristique départage surtout les positions lorsque la conclusion de la partie se trouve au-delà de la profondeur atteinte.

