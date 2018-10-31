import numpy as np
import heapq
import snake


class Population:
    def __init__(self, factory, pop_size, individuals=None):
        self.pop_size = pop_size
        self.pop_factory = factory
        self.mutation_rate = 1  # Represents the percentage that some weight will vary.
        # Represents the percentage of mutants in a population.
        self.mutation_frequency = self.pop_size // 10

        if individuals is None:
            self.population = np.empty(pop_size, dtype=object)
            self.create_population(factory)
        else:
            self.population = np.array(individuals, dtype=object)

    def sort_population(self):
        fit_a = np.array([indv.get_fit() for indv in self.population])
        fit_a = heapq.nlargest(self.pop_size, range(self.pop_size), fit_a.take)
        self.population = np.array([self.population[fit_a[i]] for i in range(len(fit_a))])

    def create_population(self, factory):
        for i in range(self.pop_size):
            self.population[i] = Individual(factory)

    def remove_worst(self):
        # Talvez substituir o 4 por algo com pop_size. Tipo: self.pop_size//5
        for p in range(int(self.pop_size * (1 - 0.50)), self.pop_size):
            self.population[p] = Individual(self.pop_factory)

    """ def make_crossover(self, indv_a, indv_b, indv_c):
        for l in range(len(indv_a.layers)):
            indv_a.layers[l].weight_mtr = np.divide(np.add(indv_b.layers[l].weight_mtr,
                                                           indv_c.layers[l].weight_mtr), 2) """

    def make_crossover_simoes(self):
        for i in range(1, self.pop_size):
            for j in range(len(self.population[0].indv.layers)):
                self.population[i].indv.layers[j].weight_mtr = np.add(
                    np.multiply(self.population[0].indv.layers[j].weight_mtr, 0.35),
                    np.multiply(self.population[i].indv.layers[j].weight_mtr, 0.65))

    def make_crossover(self):
        for i in range(1, self.pop_size):
            for j in range(len(self.population[0].indv.layers)):
                best_mtr = self.population[0].indv.layers[j].weight_mtr
                curr_mtr = self.population[i].indv.layers[j].weight_mtr

                rand_r = np.random.randint(best_mtr.shape[0])
                rand_c = np.random.randint(best_mtr.shape[1])

                curr_mtr[0:rand_r, 0:rand_c] = best_mtr[0:rand_r, 0:rand_c]

    def mutate(self):
        counter = 0
        for indv in self.population:
            if counter == 0:
                counter += 1
                continue
            for l in indv.indv.layers:
                mtr = l.weight_mtr
                for i in range(mtr.shape[0]):
                    for j in range(mtr.shape[1]):
                        if np.random.uniform(0, 1) < 0.2:
                            mtr[i][j] = np.random.uniform(-1, 1)
        # for i in range(self.mutation_frequency):
        #     mutant_ind = random.randint(1, self.pop_size - 1)
        #     mutant_layer = random.randint(0, len(self.population[0].indv.layers) - 1)
        #     self.population[mutant_ind].indv.layers[mutant_layer].weight_mtr =\
        #         self.population[mutant_ind].indv.layers[mutant_layer].weight_mtr * \
        #         (1 + (self.mutation_rate) * (-1)**(mutant_ind))

    def improve_pop(self):
        self.sort_population()
        self.remove_worst()
        self.make_crossover()
        self.mutate()


class Individual:
    def __init__(self, factory, indv=None):
        self.fit = [0] * 3
        self.rank = 0
        if indv is None:
            self.indv = factory.create()
        else:
            self.indv = indv

    def get_mov(self, input_array):
        y = self.indv.predict(input_array)
        y = np.argmax(y)
        if y == 0:
            return None
        elif y == 1:
            return snake.Direction.right
        else:
            return snake.Direction.left

    def get_fit(self):
        return np.divide(np.sum(self.fit), 3)

    def add_fit(self, fit_score):
        del self.fit[0]
        self.fit.append(fit_score)

    def clear_fit(self):
        self.fit = 0
