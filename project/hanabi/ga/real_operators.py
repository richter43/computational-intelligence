import numpy as np
import numpy.typing as npt

class Crossover(object):

    @staticmethod
    def single_point_crossover(cod_1: npt.NDArray[np.float32], cod_2: npt.NDArray[np.float32]):

        assert cod_1.shape[0] == cod_2.shape[0]

        size = cod_1.shape[0]
        new_cod = np.zeros(size)

        rand_cut = np.random.randint(size)

        new_cod[:rand_cut] = cod_1[:rand_cut]
        new_cod[rand_cut:] = cod_2[rand_cut:]

        return new_cod

    @staticmethod
    def simulated_binary_crossover(cod_1: npt.NDArray[np.float32], cod_2: npt.NDArray[np.float32], distribution_index=5, low=0, high=1.0):

        assert cod_1.shape[0] == cod_2.shape[0]

        u = np.random.rand()

        eta = distribution_index

        if u > 0.5:
            beta = (1 / (2 * (1 - u)))**(1 / (eta + 1))
        else:
            beta = (2 * u)**(1 / (eta + 1))

        cod_1_new = 0.5*((1+beta)*cod_1 + (1-beta)*cod_2)
        cod_2_new = 0.5*((1-beta)*cod_1 + (1+beta)*cod_2)

        cod_1_new = np.clip(cod_1_new, low, high)
        cod_2_new = np.clip(cod_2_new, low, high)

        return cod_1_new, cod_2_new

class Mutation(object):


    @staticmethod
    def random_mutation(cod:npt.NDArray[np.float32], low=0, high=1.0):
        return np.random.uniform(low=low, high=high, size=(len(cod),))

    @staticmethod
    def alternate_random_mutation(cod: npt.NDArray[np.float32], low:float=0, high:float=1.0, window:float=0.2):

        cod_new = np.random.uniform(cod-window, cod+window).clip(low,high)

        return cod_new

    @staticmethod
    def normally_distributed_mutation(cod: npt.NDArray[np.float32], low:float=0, high:float=1.0, sigma:float=0.1):
        cod_new = np.random.normal(cod,sigma)
        cod_new = cod_new.clip(low,high)

        return cod_new