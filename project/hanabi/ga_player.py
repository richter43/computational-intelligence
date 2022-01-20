import time
from threading import Thread
import numpy as np
import numpy.typing as npt
from typing import Tuple
import subprocess
import csv

import player
import utils.localparse as parse
from argparse import Namespace
import ga

POPULATION = 16
GENE_SIZE = 3

crossover_functions = [ga.Crossover.simulated_binary_crossover, ga.Crossover.single_point_crossover]
mutation_functions = [ga.Mutation.random_mutation, ga.Mutation.normally_distributed_mutation,
                      ga.Mutation.alternate_random_mutation]


def genetic_algorithm(args):
    """
    Genetic algorithm iteration

    Args:
        args: Namespace that contains all of the parsed arguments at execution time
    """

    pop = initial_population(POPULATION, GENE_SIZE)
    results = np.zeros(POPULATION, dtype=(np.float32, np.float32))

    for idx in range(args.iterations):

        subprocess.Popen(["python", "server.py", f"{args.num_players}"])

        if idx != 0:

            crossover = np.random.choice(crossover_functions, 1)[0]
            mutation = np.random.choice(mutation_functions, 1)[0]

            if np.random.rand() < 0.5:
                parent_1, parent_2 = tournament(pop, results), tournament(pop, results)
            else:
                parent_1, parent_2 = elites(pop, results)

            offspring = []

            for idx_in in range(POPULATION):

                if crossover is ga.Crossover.simulated_binary_crossover:
                    offspring_1, offspring_2 = crossover(parent_1, parent_2)
                    offspring.append(mutation(offspring_1))
                    offspring.append(mutation(offspring_2))
                    if len(offspring) >= POPULATION:
                        break
                else:
                    offspring_1 = crossover(parent_1, parent_2)
                    offspring.append(mutation(offspring_1))

            pop = np.vstack(offspring)

        results = fitness_function(args, pop)
        with open(f"best_chromosomes.csv", 'a') as f:
            f.write(f"{pop[results == np.max(results)][0]},{np.max(results)}\n")

        if np.max(results) > 18:
            print(f"Best solution: {pop[results == np.max(results)]}")
            break


def elites(parents: npt.NDArray[npt.NDArray[np.float32]], fitness: npt.NDArray[np.int]) -> Tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
    """

    Return two of the best parents

    Args:
        parents:  Matrix of parents
        fitness: Array of fitness values to the given parent

    Returns:
        Tuple of the best two parents
    """
    sorted_order = fitness.argsort()
    par_1, par_2 = parents[sorted_order[::-1][:2]]
    return par_1, par_2



def tournament(parents: npt.NDArray[npt.NDArray[np.float32]], fitness: npt.NDArray[np.int],
               tournament_size: int = 2) -> npt.NDArray[np.float32]:
    """

    Implementation of tournament between tournament_size parents

    Args:
        parents: Matrix of parents
        fitness: Array of scores
        tournament_size: Parents that will fight between each other

    Returns:
        Best individual's genes
    """
    idxs = np.random.choice(len(parents), tournament_size, replace=False)
    tmp_parents = parents[idxs]
    best_parent_idx = np.argmax(fitness[idxs])

    return tmp_parents[best_parent_idx]


def initial_population(population_size: int, chromosome_size: int) -> npt.NDArray[npt.NDArray[np.float32]]:
    """

    Initializes the population by creating random individuals

    Args:
        chromosome_size: Size of each chromosome
        population_size: Amount of individuals to return

    Returns:
        Matrix of individuals' genetic info
    """

    return np.random.random((population_size, chromosome_size))


def fitness_function(args: Namespace, chromosome_array: npt.NDArray[npt.NDArray[np.float32]]) -> npt.NDArray[np.int]:
    """

    Function that computes the fitness, in this case, it plays a Hanabi round with a single GA player and the rest are
    deterministic

    Args:
        args: Namespace object that contains all the values passed.
        chromosome_array: Matrix of chromosomes to be tested

    Returns:
        Array of the scores
    """
    threads = []
    tmp_ret = []

    time.sleep(1)  # Sadly, it's the only way to ensure that the server has started before instantiating the agents

    player.init_global_vars(args)

    for idx in range(args.num_players):
        if idx == 0:
            t = Thread(target=player.player_thread, args=(
            idx, tmp_ret, "ga", chromosome_array.shape[0], [chromosome for chromosome in chromosome_array], args.slowmode))
        else:
            t = Thread(target=player.player_thread,
                       args=(idx, tmp_ret, "deterministic", chromosome_array.shape[0], None, args.slowmode))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return np.array(tmp_ret)


if __name__ == "__main__":
    args = parse.parse_arguments()
    genetic_algorithm(args)
