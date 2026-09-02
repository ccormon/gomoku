# gomoku

## Construction et lancement

Le moteur ne dépend que de la bibliothèque standard C++17. Le front utilise Python 3 et Pygame.

```sh
make
./Gomoku
```

`make` construit `build/libgomoku_ai.so` puis le lanceur `Gomoku`. Les dépendances des objets sont déclarées explicitement : une seconde invocation de `make` ne recompile et ne relie rien.

Les cibles demandées par le sujet sont disponibles : `all`, `clean`, `fclean` et `re`. Deux cibles supplémentaires exécutent la validation :

```sh
make test
make bench
```

## Architecture

Le front Python reste propriétaire de la partie et de l'affichage. `src/AI/GomokuAI.py` transforme le plateau 19×19 en tableau contigu, appelle l'ABI C avec `ctypes`, puis retourne `(row, col)`. Les compteurs de captures sont transmis à chaque recherche.

Le moteur C++ sépare quatre responsabilités :

- `Board` contient les deux bitboards, les cellules, les captures, les lignes évaluées et le hash Zobrist ;
- les règles valident les coups, retirent les captures, détectent les trois libres et déterminent si un alignement est réellement gagnant ;
- l'évaluateur recalcule uniquement les lignes touchées et utilise 28 motifs tactiques compilés dans une table de lookup ;
- `Engine` effectue un Min-Max sous forme Negamax avec alpha-bêta, approfondissement, table de transposition, killer moves et historique.

L'ABI publique se trouve dans `include/gomoku/c_api.h`. Un moteur opaque conserve sa table de transposition entre les tours. Chaque résultat expose le coup, le score, la profondeur entièrement terminée, le nombre de nœuds et le temps natif. Aucune exception C++ ne traverse cette frontière.

## Règles implémentées

- Goban fixe de 19×19 et alignement gagnant de cinq pierres ou plus ;
- capture d'une paire adverse encadrée dans chacune des huit directions ;
- captures multiples et victoire à dix pierres capturées ;
- interdiction d'un coup créant deux trois libres, droits ou brisés, pour les deux couleurs ;
- exception autorisant le double-trois lorsque le même coup capture une paire ;
- alignement différé si l'adversaire peut le casser par capture ou atteindre immédiatement dix captures.

La détection d'un trois libre ne repose pas uniquement sur une chaîne littérale. Pour chaque axe, le moteur vérifie qu'une continuation peut réellement produire un quatre ouvert aux deux extrémités. Les bords du plateau et les pierres adverses sont donc traités comme des blocages.

## Recherche et limite de temps

Les coups candidats se trouvent à deux intersections au maximum d'une pierre existante. Avant la réduction sélective, ils sont ordonnés selon les priorités suivantes : victoire, blocage d'une victoire, capture, coup de transposition, killer move, historique et score local. Le potentiel tactique adverse reçoit un poids double : un quatre ouvert ou un trois cassé à bloquer ne peut ainsi pas être masqué par une attaque secondaire.

Avant cette recherche, le moteur traite exhaustivement les tactiques forcées en un coup. Il privilégie d'abord son propre alignement de cinq, même lorsque celui-ci impose encore une réponse de capture, puis traite les menaces adverses. Il bloque aussi un alignement adverse de cinq encore cassable : bien qu'il ne gagne pas immédiatement selon les règles, il imposerait une capture au tour suivant et ne doit pas être ignoré en l'absence d'une continuation offensive équivalente.

La recherche termine rapidement les profondeurs 1 à 4, puis une recherche sélective à 10 plis. Elle continue ensuite à 11 plis et au-delà jusqu'au budget par défaut de 450 ms. Les niveaux profonds comparent 16 coups à la racine, 6 réponses adverses, puis 3 coups sur les niveaux tactiques suivants. Le meilleur résultat d'une profondeur complètement terminée est conservé si l'horloge expire.

Le premier coup utilise directement le centre comme coup d'ouverture. Sa profondeur annoncée vaut donc honnêtement zéro plutôt que de prétendre avoir exploré un arbre inutilement symétrique.

## Validation

Les tests C++ couvrent les captures simples et multiples, apply/undo, hash Zobrist, évaluation incrémentale, double-trois, exception par capture, alignements cassables, victoire par captures, défense immédiate et recherche tactique.

Les tests Python vérifient le chargement de la bibliothèque, l'absence de mutation du plateau fourni, la parité des règles essentielles et le budget sur une position de milieu de partie. Le benchmark exige une profondeur terminée d'au moins 10, un temps natif inférieur à 475 ms et un temps total Python inférieur à 525 ms afin de tolérer une faible variation d'ordonnancement du système.
