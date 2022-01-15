import time
from threading import Thread
import numpy as np
import numpy.typing as npt
from typing import Tuple

import player
import server
import utils.localparse as parse
import ga

POPULATION = 16

crossover_functions = [ga.Crossover.simulated_binary_crossover, ga.Crossover.single_point_crossover]
mutation_functions = [ga.Mutation.random_mutation, ga.Mutation.normally_distributed_mutation, ga.Mutation.alternate_random_mutation]

def genetic_algorithm(args):
    """
    Genetic algorithm iteration

    Args:
        args: Namespace that contains all of the parsed arguments at execution time
    """

    pop = initial_population(1, POPULATION)

    results = np.zeros(POPULATION, dtype=(np.float32, np.float32))

    for idx in range(args.iterations):

        if idx != 0:
            # sorted_order = results.argsort()

            crossover = np.random.choice(crossover_functions, 1)[0]
            mutation = np.random.choice(mutation_functions, 1)[0]

            parent_select = np.random.rand()

            if parent_select < 0.5:
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

        for idx_in, individual in enumerate(pop):
            results[idx] = fitness_function(args, individual)

def elites(parents: npt.NDArray[npt.NDArray[np.float32]], fitness: npt.NDArray[np.float32]) -> Tuple[float,float]:
    sorted_order = fitness.argsort()
    par_1, par_2 = parents[sorted_order[::-1][:2]]
    return par_1, par_2

def tournament(parents: npt.NDArray[npt.NDArray[np.float32]], fitness: npt.NDArray[np.float32], tournament_size:int=2) -> float:

    idxs = np.random.choice(len(parents), tournament_size, replace=False)

    print(idxs)

    tmp_parents = parents[idxs]

    print(tmp_parents)
    print(fitness[idxs])

    best_parent_idx = np.argmax(fitness[idxs])

    return tmp_parents[best_parent_idx]


def initial_population(chromosome_size: int, population_size: int) -> npt.NDArray[npt.NDArray[np.float32]]:
    """

    Initializes the population by creating random individuals

    Args:
        chromosome_size: self-explanatory
        population_size:

    Returns:

    """
    return np.random.random((population_size, chromosome_size))

def fitness_function(args, chromosome: npt.NDArray[np.float32]) -> float:

    breakpoint()

    args.ga_max_playability = chromosome[0]
    args.player_type = "ga"

    threads = []
    tmp_ret = [0]

    t = Thread(target=server.start_server, args=(args.num_players,))
    threads.append(t)
    t.start()

    time.sleep(2)

    t = Thread(target=player.main, args=(args, tmp_ret))
    threads.append(t)
    t.start()

    for t in threads:
        t.join()

    return tmp_ret[0]

if __name__ == "__main__":

    args = parse.parse_arguments()
    genetic_algorithm(args)