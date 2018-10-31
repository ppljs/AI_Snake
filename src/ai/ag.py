import numpy as np
import heapq
import snake
import random


class Population:
    def __init__(self, factory, pop_size, individuals=None):
        self.pop_size = pop_size
        self.pop_factory = factory
        self.mutation_rate = 1 #Represents the percentage that some weight will vary.
        self.mutation_frequency = self.pop_size//10 #Represents the percentage of mutants in a population.

        if individuals is None:
            self.population = np.empty(pop_size, dtype=object)
            self.create_population(factory)
        else:
            self.population = np.array(individuals, ndarray=object)

    def sort_population(self):
        fit_a = np.array([indv.fit for indv in self.population])
        print(fit_a)
        fit_a = heapq.nlargest(self.pop_size, range(self.pop_size), fit_a.take)
        self.population = np.array([self.population[fit_a[i]] for i in range(len(fit_a))])

    def create_population(self, factory):
        for i in range(self.pop_size):
            self.population[i] = Individual(factory)

    def remove_worst(self):
        # Talvez substituir o 4 por algo com pop_size. Tipo: self.pop_size//5
        for p in range(self.pop_size - 2, self.pop_size):
            self.population[p] = Individual(self.pop_factory)

    """ def make_crossover(self, indv_a, indv_b, indv_c):
        for l in range(len(indv_a.layers)):
            indv_a.layers[l].weight_mtr = np.divide(np.add(indv_b.layers[l].weight_mtr,
                                                           indv_c.layers[l].weight_mtr), 2) """

    def make_crossover(self):
        for i in range(random.randint(1, self.pop_size-1)):
            for j in range(len(self.population[0].indv.layers)):   
                self.population[i].indv.layers[j].weight_mtr = np.add(self.population[0].indv.layers[j].weight_mtr*0.65, self.population[i].indv.layers[j].weight_mtr*0.35)
            

    """ def mutate(self, indv):
        for l in indv.layers:
            mtr = l.weight_mtr
            for i in range(mtr.shape[0]):
                for j in range(mtr.shape[1]):
                    if np.random.uniform(0, 1) < 0.2:
                        abs_val = np.abs(mtr[i][j])
                        mtr[i][j] = np.random.uniform(-abs_val, abs_val) * \
                            np.random.uniform(1.1, 2) """
    
    def mutate(self):
        for i in range(self.mutation_frequency):
            mutant_ind = random.randint(1, self.pop_size-1)
            mutant_layer = random.randint(0, len(self.population[0].indv.layers)-1)
            self.population[mutant_ind].indv.layers[mutant_layer].weight_mtr = self.population[mutant_ind].indv.layers[mutant_layer].weight_mtr*(1+(self.mutation_rate)*(-1)**(mutant_ind))
            

    def improve_pop(self):
        self.sort_population()
        self.remove_worst()
        self.make_crossover()
        self.mutate()


class Individual:
    def __init__(self, factory):
        self.fit = 0
        self.rank = 0
        self.indv = factory.create()

    def get_mov(self, input_array):
        y = self.indv.predict(input_array)
        print('Y =', y)
        y = np.argmax(y)
        if y == 0:
            return None
        elif y == 1:
            return snake.Direction.right
        else:
            return snake.Direction.left

    def clear_fit(self):
        self.fit = 0
