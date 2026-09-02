# Implémentation des règles du jeu

## Deux implémentations cohérentes

Les règles existent à deux endroits pour des responsabilités différentes :

- `src/Game/Game.py` applique les coups de la partie réelle, met à jour l'affichage, l'historique et le gagnant ;
- la classe C++ `Board` de `src/cpp/engine.cpp` reproduit les mêmes règles dans les positions simulées par l'IA.

Le moteur reçoit la grille et les compteurs de captures au début de chaque recherche. Il travaille ensuite sur une copie : les simulations de l'IA ne modifient jamais la partie affichée.

## Plateau et joueurs

Le plateau mesure 19 × 19 intersections. Une cellule contient :

| Valeur | Contenu |
|---:|---|
| `0` | vide |
| `1` | joueur 1 |
| `2` | joueur 2 |

Dans le moteur, ces constantes correspondent à `BoardSize`, `CellCount` et à l'énumération `Player`. `Board::inside` centralise le contrôle des limites.

Dans le front, `Game.activePlayer` indique le joueur au trait. `_handleMove` valide et pose la pierre, traite les captures, enregistre le coup, vérifie la fin de partie, puis alterne le joueur.

## Validité d'un coup

Un coup ordinaire est légal si :

1. ses coordonnées appartiennent au plateau ;
2. la case est vide ;
3. il ne crée pas un double trois interdit.

Le front applique ces conditions avec `Game._checkValidMove`. Le moteur utilise `Board::isLegalMove`. L'IA ne génère donc que des coups que l'interface acceptera ensuite.

## Capture d'une paire

Une paire adverse est capturée lorsqu'un joueur l'encadre en posant une pierre selon la forme suivante :

```text
nouvelle pierre - adversaire - adversaire - pierre alliée
```

La règle est vérifiée dans les huit directions : horizontales, verticales et diagonales, dans les deux sens.

Dans le front :

- `_captureCells` détermine quelles pierres seraient capturées sans modifier la grille ;
- `_handleCapture` retire réellement les pierres après la pose et ajoute deux au score du joueur par paire.

Dans le moteur :

- `Board::isCapturingMove` indique si un coup produirait au moins une capture ;
- `Board::play` recherche toutes les paires encadrées, les retire et met à jour le compteur ;
- plusieurs paires peuvent être capturées par un seul coup dans des directions différentes ;
- `Board::undo` restaure toutes les pierres capturées pendant le retour arrière de la recherche.

Les compteurs représentent des pierres capturées, et non des paires. Une capture ajoute donc 2 et la victoire par capture est atteinte à 10.

## Interdiction du double trois

Un coup est interdit s'il crée simultanément au moins deux trois libres sur des axes différents. Les quatre axes examinés sont l'horizontale, la verticale et les deux diagonales.

La détection ne recherche pas seulement la chaîne littérale `01110`. Pour chaque axe, le programme :

1. construit une fenêtre de onze cases autour du coup ;
2. simule la pierre jouée ;
3. essaie chaque case vide comme continuation ;
4. vérifie si cette continuation peut produire quatre pierres avec les deux extrémités libres ;
5. compte les axes qui possèdent réellement une telle possibilité.

Cette méthode reconnaît aussi les trois cassés. Une pierre adverse ou un bord reçoit la valeur bloquante `3`, ce qui empêche de considérer comme libre une forme fermée.

Le front implémente cette logique dans `_checkDoubleThreeForPlayer`. Le moteur la sépare entre `directionHasOpenThree` et `isDoubleThree`.

Une exception est prévue : si le même coup capture une paire, le double trois reste autorisé. Les deux implémentations vérifient donc la capture avant d'interdire le coup.

## Alignement de cinq

Un alignement contient au moins cinq pierres consécutives sur l'un des quatre axes. Les alignements de plus de cinq sont également acceptés.

Dans le front :

- `_checkFiveInARow` compte les pierres depuis le dernier coup dans les deux sens ;
- `_hasAnyFive` recherche un cinq déjà présent n'importe où sur le plateau.

Dans le moteur :

- `Board::hasFive` examine toutes les lignes ;
- `hasFiveThrough` limite la vérification aux lignes du dernier coup lorsqu'il est possible de le faire ;
- `isWinningMove` et `isWinningState` combinent l'alignement avec la règle des captures défensives.

## Alignement cassable par capture

Dans cette variante, former cinq pierres ne gagne pas immédiatement si l'adversaire peut casser tous les alignements de cinq avec une capture au coup suivant, ou atteindre dix captures avec cette réponse.

`Game._canBreakAlignmentOrWinByCapture` parcourt toutes les cases vides. Pour chaque capture possible du défenseur, la fonction simule la pose et le retrait de la paire, puis vérifie si l'alignement a disparu ou si le défenseur gagne par captures. La grille est ensuite restaurée.

Le moteur applique la même règle dans `Board::hasBreakingCapture` en copiant le plateau, en jouant chaque réponse capturante légale et en appelant de nouveau `hasFive`.

Cette distinction explique les deux notions utilisées par l'IA :

- `hasFive` signifie qu'un alignement physique existe ;
- `isWinningMove` signifie que cet alignement constitue déjà une victoire selon toutes les règles.

Un cinq encore cassable impose néanmoins une réponse : si le défenseur joue ailleurs sans supprimer l'alignement, la victoire adverse est validée. Le prétraitement tactique de l'IA tient compte de cette obligation ; son fonctionnement stratégique est décrit dans `02_optimisations.md`.

## Victoire par captures

Un joueur gagne dès que son compteur atteint dix pierres capturées. Le front teste cette condition au début de `_checkWinCondition`. Le moteur la teste dans `isWinningState` et `isWinningMove`.

Lors de l'analyse d'un cinq cassable, une capture qui fait atteindre dix au défenseur est également une réponse gagnante, même si un autre alignement subsiste sur le plateau.

## Ordre de résolution d'un tour

Pour la partie affichée, `_handleMove` suit cet ordre :

1. vérifier la légalité du coup ;
2. poser la pierre ;
3. retirer les paires capturées ;
4. mettre à jour l'historique et le temps ;
5. vérifier la victoire par captures ou alignement ;
6. vérifier si le plateau est plein ;
7. changer le joueur actif.

L'ordre « capture avant victoire » est important : une pierre retirée ne doit pas être comptée dans un alignement gagnant.

## Égalité

`Game._checkTieCondition` déclare une égalité uniquement lorsque toutes les cases sont occupées et qu'aucune victoire n'a été détectée auparavant. Le moteur n'a pas besoin d'un état spécial d'égalité : si aucun coup légal n'existe, il renvoie le statut `GOMOKU_NO_LEGAL_MOVE` par l'API C.

## Parité entre le front et le moteur

Les tests Python vérifient les règles exposées par le front, notamment le double trois, son exception par capture et le cinq cassable. Les tests C++ couvrent les mêmes cas dans le moteur, ainsi que les captures multiples, la victoire à dix pierres et la restauration par `undo`.

Cette double validation est nécessaire : une différence entre Python et C++ pourrait conduire l'IA à proposer un coup refusé par l'interface ou à évaluer comme gagnante une position que le jeu laisse continuer.

