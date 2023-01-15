# Quarto

## Task
Create an agent trained to play **Quarto! Game**.

## General Idea
We decided to implement an agent that exploits **minMax strategy**. Given the high number of possible reachable states, a certain number of optimizations were required.

In particular, looking through academic papers, we found out that in the board there are a certain number of exploitable **symmetries**, which allow us to greatly reduce the amount of explorable states.

## Development

In order to implement minMax algorithm and to reduce the already not low computational weight, we introduce a dictionary to store already visited states.
To achieve this, we used the actual state of the board as _key_ and the possible moves with a goodness metric as _values_.

To maximize **collisions** in the dictionary, we check all the symmetries of the state.
In this way even if the state seems unseen, we already know the best next move.

Even checking the symmetries, the number of possible states is some order of magnitude too high to be fully explored in reasonable time. So we introduce **alpha-beta pruning** in order to cut irrelevant branches.

We decided to implement a **stopping condition** in the exploration, based on the number of keys in the dictionary. After reaching this limit (tweaked by hand), the agent will stop the exploration and will perform some moves without further exploring from the reached state. In the beginning those moves were randomly generated. This strategy led to poor performances during some test games. So we chose to implement a more heuristic strategy, in which we rapidly test all the possible moves we can perform in that state and we ignore those that could lead to an immediate opponent's victory.

To further reduce the exploration space, we decide to randomly make the first move (piece selection), in this way at the beginning of the exploration we can cut 15/16th of the original search tree.

## Bibliography
- https://www.slideshare.net/MatthewKerner2/quarto-55043713

- https://web.archive.org/web/20041012023358/http://ssel.vub.ac.be/Members/LucGoossens/quarto/quartotext.htm

- https://www.mathpages.com/home/kmath352.htm

- http://web.archive.org/web/20120306212129/http://www.cs.rhul.ac.uk/~wouter/Talks/quarto.pdf

## Contributors

- [Fabrizio Sulpizio](https://github.com/Xiusss)
- [Simone Mascali](https://github.com/vmask25)