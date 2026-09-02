# Optimisations du moteur de recherche

## Architecture native

L'interface et l'état principal de la partie sont écrits en Python, mais la recherche est exécutée en C++17. `src/AI/GomokuAI.py` aplatit la grille 19 × 19 dans un tableau de 361 octets et appelle `gomoku_find_best_move` avec `ctypes`.

La frontière publique est définie dans `include/gomoku/c_api.h`. `src/cpp/c_api.cpp` valide les paramètres, construit un `Board`, appelle le moteur et renvoie le coup, le score, la profondeur terminée, le nombre de nœuds et le temps écoulé. Aucune exception C++ ne traverse cette frontière.

L'objet `Engine` reste vivant entre les tours. Sa table de transposition et son historique peuvent ainsi être réutilisés sans reconstruire tout le moteur à chaque appel.

## Negamax et élagage alpha-bêta

`Engine::negamax` est une forme compacte de Min-Max. Le principe est que le meilleur score d'un joueur est l'opposé du meilleur score de son adversaire :

```text
score(coup) = -negamax(position suivante, adversaire)
```

Il n'est donc pas nécessaire d'écrire séparément une fonction qui maximise pour un joueur et une fonction qui minimise pour l'autre.

Les bornes `alpha` et `beta` représentent respectivement le meilleur résultat déjà garanti au joueur actif et la limite au-delà de laquelle la branche n'apporte plus d'information. Dès que `alpha >= beta`, les coups restants de la branche sont ignorés. Cet élagage ne change pas le résultat d'une recherche complète à profondeur égale ; son efficacité dépend surtout de l'ordre dans lequel les coups sont essayés.

## Approfondissement itératif et limite de temps

`Engine::findBestMove` recherche successivement aux profondeurs 1, 2, 3, 4, puis 10 et enfin 11 à 32 tant que le budget le permet. Après chaque profondeur entièrement terminée, le meilleur coup est enregistré dans `SearchResult`.

`checkDeadline` compare régulièrement l'horloge monotone à la date limite. Lorsque le budget est épuisé, une exception interne `Timeout` interrompt uniquement l'itération en cours. Le résultat de la dernière profondeur complète est conservé. L'interface peut afficher cette valeur grâce au champ `completed_depth`.

Ce fonctionnement évite de renvoyer le résultat incomplet d'une branche interrompue. Il donne aussi rapidement un coup valide avant de consacrer le temps restant aux variantes plus profondes.

## Prétraitement des tactiques forcées

Avant le Min-Max, `findBestMove` traite exhaustivement les situations en un coup :

1. victoire immédiate du joueur actif ;
2. création de son propre cinq, même si ce cinq impose encore une réponse par capture ;
3. cinq adverse déjà présent et encore cassable ;
4. coup gagnant immédiat de l'adversaire ;
5. création possible d'un cinq adverse encore cassable.

Pour chaque menace adverse, le moteur vérifie qu'une défense supprime réellement toutes les réponses gagnantes, car poser directement sur une extrémité n'est pas toujours la seule solution : une capture jouée ailleurs peut casser la ligne.

L'ordre des deux premiers points corrige le cas « quatre contre quatre » : si le joueur actif peut compléter son propre alignement, l'IA ne remplace plus automatiquement cette attaque par le blocage du quatre adverse.

Ce prétraitement rend les tactiques urgentes indépendantes de l'ordre heuristique, de la réduction de branches et d'un budget très court.

## Génération sélective des coups

`Board::legalMoves` ne retourne pas les centaines de cases vides du plateau. Une case est candidate seulement si elle se trouve à une distance maximale de deux lignes et deux colonnes d'une pierre existante. Les coups illégaux sont ensuite retirés.

Sur un plateau vide, le moteur joue directement au centre `(9, 9)`. Ce choix supprime une recherche inutile entre des ouvertures symétriques.

La restriction locale réduit fortement le facteur de branchement. Elle suppose qu'un coup pertinent se trouve près du jeu existant, ce qui est généralement vrai au Gomoku.

## Ordonnancement des coups

`Engine::orderedMoves` attribue une priorité à chaque coup avec `movePriority`, puis les trie du plus prometteur au moins prometteur. Un bon ordre provoque plus tôt des coupures alpha-bêta.

La priorité combine :

- le meilleur coup trouvé dans la table de transposition ;
- les killer moves ayant déjà produit une coupure à la même profondeur ;
- l'historique des coups ayant souvent provoqué des coupures ;
- une victoire créée par le coup ;
- les pierres capturées ;
- la variation du score heuristique ;
- la valeur tactique qu'aurait cette même case pour l'adversaire.

Le coup est joué temporairement avec `Board::play`, évalué, puis annulé avec `Board::undo`. Une capture reçoit 400 000 points de priorité par pierre retirée. Une victoire reçoit un bonus encore supérieur. Le potentiel adverse reçoit un facteur deux afin de faire remonter rapidement les cases défensives importantes.

L'ordonnancement influence la vitesse et les branches conservées par la recherche sélective, mais les tactiques forcées décrites précédemment sont vérifiées avant lui.

## Réduction du facteur de branchement

`Engine::branchLimit` limite le nombre de coups approfondis après leur tri. Pour les recherches profondes, le moteur conserve jusqu'à 16 coups à la racine, 6 au niveau suivant, 3 jusqu'au quatrième niveau, puis 1 dans les niveaux les plus éloignés. Pour les petites profondeurs, les limites sont plus larges après la racine.

Cette sélection permet d'annoncer une profondeur importante dans le budget de 450 ms. En contrepartie, contrairement à l'alpha-bêta seul, elle peut écarter un coup mal classé par l'ordonnancement. Le prétraitement tactique protège les gains et défenses immédiats contre ce risque.

## Table de transposition et hash Zobrist

Deux suites de coups différentes peuvent conduire à la même position. La table de transposition évite alors de refaire une recherche déjà connue.

`Board::hash` combine des clés pseudo-aléatoires déterministes pour :

- chaque pierre et sa case ;
- le compteur de captures de chaque joueur ;
- le joueur au trait.

Lorsqu'une pierre ou un compteur change, un XOR retire l'ancienne clé et ajoute la nouvelle. Le hash est donc mis à jour sans reparcourir le plateau.

La table contient `2^18` entrées et utilise les bits bas du hash comme index. Une entrée mémorise sa clé complète, sa profondeur, son score, son meilleur coup et le type de borne : exacte, inférieure ou supérieure. La clé complète protège contre l'utilisation directe d'une collision d'index.

Un numéro de génération distingue les recherches successives. `store` remplace une entrée appartenant à une ancienne génération ou moins profonde. `probe` peut fournir un score déjà calculé ou au minimum un bon premier coup pour l'ordonnancement.

## Killer moves et historique

Lorsqu'un coup produit une coupure alpha-bêta, le moteur mémorise :

- jusqu'à deux killer moves pour le niveau courant ;
- un score d'historique propre au joueur et à la case, augmenté de `profondeur²`.

Les killer moves représentent des coups efficaces dans des positions voisines au même niveau de l'arbre. L'historique favorise les cases qui ont souvent réfuté une variante, indépendamment d'une position précise. Ces deux mécanismes améliorent l'ordre des coups sans modifier les règles.

## État incrémental et annulation

Le plateau conserve simultanément :

- un tableau de 361 cellules pour les accès simples ;
- des bitboards indiquant rapidement les pierres de chaque joueur ;
- les scores des lignes ;
- le score total ;
- le hash Zobrist ;
- les compteurs de captures.

`initializeLines` construit une fois toutes les lignes du plateau et les quatre identifiants de ligne associés à chaque case. Après un coup, `refreshLines` recalcule uniquement les lignes touchées par la pierre posée ou les pierres capturées.

`MoveUndo` conserve le coup, les pierres retirées, les anciens compteurs et l'ancien hash. `Board::undo` restaure ensuite exactement la position sans la reconstruire. Cette opération est essentielle puisque la recherche joue et annule un très grand nombre de coups.

## Compilation optimisée et validation

Le `Makefile` compile le moteur avec `-O3` et `-DNDEBUG`, produit une bibliothèque partagée, puis la charge depuis Python. `make test` exécute les tests C++ et Python. `make bench` vérifie notamment le budget de temps et la profondeur atteinte sur une position représentative.

Les métriques natives permettent de contrôler les effets des optimisations : `nodes`, `elapsed_us` et `completed_depth` sont transmis jusqu'à l'interface.

