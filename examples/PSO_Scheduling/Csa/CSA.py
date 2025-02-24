############################################################################

# Created by: Prof. Valdecy Pereira, D.Sc.
# UFF - Universidade Federal Fluminense (Brazil)
# email:  valdecy.pereira@gmail.com
# Metaheuristic: Crow Search Algorithm

# PEREIRA, V. (2022). GitHub repository: https://github.com/Valdecy/pyMetaheuristic

# Edited for scheduling by Reza Akraminejad

############################################################################

# Required Libraries
import numpy as np
import random
import os
import leaf.application
import leaf.infrastructure
from examples.PSO_Scheduling.setting import MICROPROCESSORS_POWER_RAM
from leaf.infrastructure import *

############################################################################


############################################################################


# res=[]
res = 10 ** (-8)
iterNum = 0
selected = []


# Function: Crow Search Algorithm
class TaskDeviceScheduler:
    def __init__(self, devices, tasks, infrastructure, applications,
                 population_size=5, ap=0.02, fL=0.02, min_values=[-5, -5], max_values=[5, 5], iterations=100,
                 verbose=False,alpha=.25,beta=.25,gamma=.25,delta=.25):
        self.devices = devices
        self.tasks = tasks
        self.tasks_len=len(tasks)
        self.infrastructure = infrastructure
        self.applications = applications
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.population_size=population_size
        self.ap=ap
        self.fL=fL
        self.min_values=min_values
        self.max_values=max_values
        self.iterations=iterations
        self.verbose=verbose
        self.list_fitness=[]
        self.best_min_iteration_number = iterations

        global res
        global iterNum
        global selected

        self.optimize()

    def optimize(self):
        global res, iterNum
        best_min_iteration_number = self.iterations
        print('Starting B-CSA')
        count = 0
        population = self.initial_population(self.population_size, self.min_values, self.max_values)
        best_ind = np.copy(population[population[:, -1].argsort()][0, :])
        # res.append(best_ind[-1])
        res = best_ind[-1]
        while count <= self.iterations:
            print(count)
            if self.verbose:
                print('Iteration = ', count, ' f(x) = ', best_ind[-1])
            population = self.update_position(population, self.ap, self.fL, self.min_values, self.max_values)
            value = np.copy(population[0, :])
            # res.append(value[-1])

            if best_ind[-1] > value[-1]:
                best_min_iteration_number = count
                value = [int(i) for i in value]
                best_ind = np.copy(value)
                # res.append(best_ind)
                res = best_ind[-1]
                selected.append(iterNum)
            count = count + 1
            iterNum = count



            self.global_best_position = best_ind[:self.tasks_len]
            # TODO: in pso we append list_fitness as every best local fitness of papulation, but here we set
            #  global_best_score in every iteration
            self.global_best_score = best_ind[-1]
            self.list_fitness.append(self.global_best_score)

        self.best_min_iteration_number = best_min_iteration_number
        print("best_number_iteration_print = ", best_min_iteration_number)


    ############################################################################

    # Function: Initialize Variables
    def initial_population(self, population_size=5, min_values=[-5, -5], max_values=[5, 5]):
        population = np.zeros((population_size, len(min_values) + 1))
        for i in range(0, population_size):
            for j in range(0, len(min_values)):
                # population[i, j] = random.uniform(min_values[j], max_values[j])
                population[i, j] = random.randint(min_values[j], max_values[j])
            population[i, -1] = self.target_function(population[i, 0:population.shape[1] - 1])
        return population

    ############################################################################

    # Function: Update Position
    def update_position(self, population, ap, fL, min_values=[-5, -5], max_values=[5, 5]):
        for i in range(0, population.shape[0]):
            idx = [i for i in range(0, population.shape[0])]
            idx.remove(i)
            idx = random.choice(idx)
            rand = int.from_bytes(os.urandom(8), byteorder='big') / ((1 << 64) - 1)
            for j in range(0, len(min_values)):
                if rand >= ap:
                    rand_i = int.from_bytes(os.urandom(8), byteorder='big') / ((1 << 64) - 1)
                    population[i, j] = np.clip(population[i, j] + rand_i * fL * (population[idx, j] - population[i, j]),
                                               min_values[j], max_values[j])
                else:
                    # population[i, j] = random.uniform(min_values[j], max_values[j])
                    population[i, j] = random.randint(min_values[j], max_values[j])
            population[i, -1] = self.target_function(population[i, 0:population.shape[1] - 1])
        return population

    ############################################################################
    # Function
    def target_function(self, positions):
        positions = [int(i) for i in positions]
        positions_set = set(positions)
        i = 0
        sum_total = 0
        sum_node = 0
        sum_link = 0
        sum_time = 0
        static = 0
        node_times = [0 for pos in set(self.devices)]

        for pos in positions:
            self.tasks[i].allocate(self.devices[pos])
            # self.tasks[i].node.power_model().power_per_cu=self.tasks[i].cu

            # calculating node consumed time
            node_times[pos] = node_times[pos] + self.tasks[i].cu / self.devices[pos].cu

            tmp = self.devices[pos].measure_power()
            sum_node = sum_node + tmp.dynamic

            if pos in positions_set:
                sum_node = sum_node + tmp.static
                positions_set.remove(pos)

            # calculating energy of links. here we do not consider energy linkes.
            # we will do it later
            app = self.applications[i]

            # for app in self.applications:
            for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
                src_task = app.graph.nodes[src_task_id]["data"]
                dst_task = app.graph.nodes[dst_task_id]["data"]

                if isinstance(src_task, leaf.application.SourceTask):
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.bound_node.name,
                                                     dst_task.node.name)
                else:
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.node.name,
                                                     dst_task.bound_node.name)

                links = [self.infrastructure.graph.edges[a, b, 0]["data"] for a, b in nx.utils.pairwise(shortest_path)]
                data_flow.allocate(links)

                for link in links:
                    tmp = link.measure_power()
                    sum_link = sum_link + tmp.dynamic
                # TODO: Do not sum duplicated linkes static power

                data_flow.deallocate()

            self.tasks[i].deallocate()
            i = i + 1

        sum_time = sum(node_times)
        # sum_total = sum_link + sum_node
        sum_ram = sum_time * MICROPROCESSORS_POWER_RAM

        sum_total =sum_node + sum_ram + sum_link
        # print(positions)
        # print(sum_total)
        # print('==================')

        # TODO: Do not final sum for fitness
        return sum_total



    def get_best_assignment(self):
        return [int(i) for i in self.global_best_position], self.global_best_score
