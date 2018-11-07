import numpy as np
import heapq
import snake
import copy


class Population:
    def __init__(self, factory, pop_size, individuals=None):
        self.pop_size = pop_size
        self.generation = 0
        self.pop_factory = factory
        self.mutation_rate = 1  # Represents the percentage that some weight will vary.
        # Represents the percentage of mutants in a population.
        self.mutation_frequency = self.pop_size // 10

        if individuals is None:
            self.population = np.empty(pop_size, dtype=object)
            self.create_population(factory)
        else:
            self.population = np.array(individuals, dtype=object)

        self.best_indv_alltime = copy.deepcopy(self.population[0])
        self.previous_best = self.population[0]
        self.test = self.best_indv_alltime

    def sort_population(self):
        fit_a = np.array([indv.get_fit() for indv in self.population])
        fit_a = heapq.nlargest(self.pop_size, range(self.pop_size), fit_a.take)
        self.population = np.array([self.population[fit_a[i]] for i in range(len(fit_a))])
        print([indv.get_fit() for indv in self.population][0:7])

    def create_population(self, factory):
        for i in range(self.pop_size):
            self.population[i] = Individual(factory)

    def remove_worst(self):
        # Talvez substituir o 4 por algo com pop_size. Tipo: self.pop_size//5
        for p in range(int(self.pop_size * (1 - 0.20)), self.pop_size):
            self.population[p] = Individual(self.pop_factory)

    """ def make_crossover(self, indv_a, indv_b, indv_c):
        for l in range(len(indv_a.layers)):
            indv_a.layers[l].weight_mtr = np.divide(np.add(indv_b.layers[l].weight_mtr,
                                                           indv_c.layers[l].weight_mtr), 2) """

    def make_crossover_simoes(self):
        for i in range(1, self.pop_size):
            for j in range(len(self.population[0].indv.layers)):
                self.population[i].indv.layers[j].weight_mtr = np.add(
                    np.multiply(self.population[0].indv.layers[j].weight_mtr, 0.25),
                    np.multiply(self.population[i].indv.layers[j].weight_mtr, 0.75))

    def make_crossover(self):
        for i in range(1, self.pop_size):
            for j in range(len(self.population[0].indv.layers)):
                best_mtr = self.population[0].indv.layers[j].weight_mtr
                curr_mtr = self.population[i].indv.layers[j].weight_mtr

                rand_r = np.random.randint(best_mtr.shape[0])
                rand_c = np.random.randint(best_mtr.shape[1])

                curr_mtr[0:rand_r, 0:rand_c] = best_mtr[0:rand_r, 0:rand_c]

    def indv_crossover(self, indv_a, indv_b):
        new_indv = copy.deepcopy(indv_b)
        for j in range(len(indv_a.indv.layers)):
            indv_a_mtr = indv_a.indv.layers[j].weight_mtr
            indv_b_mtr = indv_b.indv.layers[j].weight_mtr
            new_mtr = np.empty(indv_a_mtr.shape)

            rand_r = np.random.randint(indv_a_mtr.shape[0])
            rand_c = np.random.randint(indv_a_mtr.shape[1])

            new_mtr[0:rand_r, 0:rand_c] = indv_a_mtr[0:rand_r, 0:rand_c]
            new_mtr[rand_r:, rand_c:] = indv_b_mtr[rand_r:, rand_c:]
            new_indv.indv.layers[j].weight_mtr = new_mtr
        return new_indv

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
                        if np.random.uniform(0, 1) < 0.0075:
                            mtr[i][j] = np.random.uniform(-1, 1)
        # for i in range(self.mutation_frequency):
        #     mutant_ind = np.random.randint(1, self.pop_size - 1)
        #     mutant_layer = np.random.randint(0, len(self.population[0].indv.layers) - 1)
        #     self.population[mutant_ind].indv.layers[mutant_layer].weight_mtr =\
        #         self.population[mutant_ind].indv.layers[mutant_layer].weight_mtr * \
        #         (1 + (self.mutation_rate) * (-1)**(mutant_ind))

    def improve_pop(self):
        self.previous_best = self.population[0]
        self.sort_population()
        if self.best_indv_alltime.get_fit() < self.population[0].get_fit():
            self.best_indv_alltime = copy.deepcopy(self.population[0])

        # if self.previous_best is not self.population[0]:
        #     print('CHANGED')
        # else:
        #     print('SAME')
        self.remove_worst()
        self.make_crossover_simoes()

        # prob_array = []
        # for i in range(self.population.shape[0]):
        #     for j in range(int(self.population[i].get_fit()) + 2):
        #         prob_array.append(self.population[i])
        #
        # prob_array_size = len(prob_array)
        # print(prob_array_size)
        # new_pop = [self.population[0]]
        # for i in range(self.pop_size - 1):
        #     parent_a = prob_array[np.random.randint(prob_array_size)]
        #     parent_b = prob_array[np.random.randint(prob_array_size)]
        #
        #     new_pop.append(self.indv_crossover(parent_a, parent_b))
        #
        # self.population = np.array(new_pop, dtype=object)
        if self.generation % 30 == 0:
            self.test = copy.deepcopy(self.best_indv_alltime)
            self.population[-1] = self.test

        i = 0
        for indv in self.population:
            if indv is self.test:
                print('i =', i)
                break
            i += 1

        self.mutate()
        self.generation += 1


class Individual:
    def __init__(self, factory, indv=None):
        self.fit = [0] * 6
        self.fit_size = len(self.fit)
        self.rank = 0
        self.add_counter = 0
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
        if self.add_counter < self.fit_size:
            return np.divide(np.sum(self.fit), self.add_counter)
        return np.divide(np.sum(self.fit), self.fit_size)

    def add_fit(self, fit_score):
        self.add_counter += 1
        del self.fit[0]
        self.fit.append(fit_score)

    def clear_fit(self):
        self.fit = 0
