############################################################################################################
import numpy as np
import csv
import random
import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *
import sys
from examples.PSO_Scheduling.setting import *

class TaskDeviceScheduler:
    # def __init__(self, devices, tasks,infrastructure,applications,num_particles=30, max_iter=100, c1=1.5, c2=1.5, w=0.9,
    #              w_damp=0.99):
    def __init__(self, devices, tasks, infrastructure, applications, num_particles=30, max_iter=100, c1=1.5, c2=1.5,
                 w=0.9, w_damp=0.99):
        self.devices = devices
        self.tasks = tasks
        self.infrastructure=infrastructure
        self.applications=applications
        self.num_tasks = len(tasks)
        self.num_devices = len(devices)

        self.list_fitness = []

        self.num_particles = num_particles
        self.max_iter = max_iter
        self.c1 = c1  # Cognitive (particle) weight
        self.c2 = c2  # Social (swarm) weight
        self.w = w  # Inertia weightx
        self.w_damp = w_damp  # Inertia damping after each iteration
        self.particles_position = np.random.randint(0, self.num_devices, size=(self.num_particles, self.num_tasks))
        self.particles_velocity = np.zeros_like(self.particles_position, dtype=float)
        self.particles_best_position = np.copy(self.particles_position)
        self.particles_best_score = np.array([self.fitness(pos) for pos in self.particles_best_position])
        self.global_best_position = self.particles_best_position[np.argmin(self.particles_best_score)]
        self.global_best_score = np.min(self.particles_best_score)
        self.best_min_iteration_number = self.max_iter

    def __check_multi_params__(self,alpha,beta,gamma,delta):
        if alpha+beta+gamma+delta != 1:
            raise ValueError("Sum of multi-objective parameters should be equal to 1.")

    def fitness(self, positions):
        # print(positions)
        positions_set=set(positions)
        i=0
        sum_total = 0
        sum_node=0
        sum_link=0
        sum_time=0
        static=0
        node_times = [0 for pos in set(self.devices)]

        for pos in positions:
            self.tasks[i].allocate(self.devices[pos])
            # self.tasks[i].node.power_model().power_per_cu=self.tasks[i].cu

            # calculating node consumed time
            node_times[pos] = node_times[pos] + self.tasks[i].cu / self.devices[pos].cu


            tmp = self.devices[pos].measure_power()
            sum_node = sum_node + tmp.dynamic

            if pos in positions_set:
                sum_node=sum_node+tmp.static
                positions_set.remove(pos)

            # calculating energy of links. here we do not consider energy linkes.
            # we will do it later
            app=self.applications[i]

            #for app in self.applications:
            for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
                src_task = app.graph.nodes[src_task_id]["data"]
                dst_task = app.graph.nodes[dst_task_id]["data"]

                if isinstance(src_task,leaf.application.SourceTask):
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.bound_node.name,
                                                     dst_task.node.name)
                else:
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.node.name,
                                                     dst_task.bound_node.name)

                links = [self.infrastructure.graph.edges[a, b, 0]["data"] for a, b in nx.utils.pairwise(shortest_path)]
                data_flow.allocate(links)

                for link in links:
                    tmp=link.measure_power()
                    sum_link=sum_link+tmp.dynamic
                #TODO: Do not sum duplicated linkes static power
                #sum_link=sum_link+tmp.static

                data_flow.deallocate()

            self.tasks[i].deallocate()
            i = i + 1

        sum_time = sum(node_times)
        sum_ram = sum_time * MICROPROCESSORS_POWER_RAM
        sum_total =sum_node + sum_ram + sum_link


        # print(positions)
        # print(sum_total)
        # print('==================')



        # TODO: Do not final sum for fitness
        return sum_total

    def optimize(self):
        print('Starting B-PSO')
        best_min_iteration_number = self.max_iter
        for k in range(self.max_iter):
            print(k)
            for i in range(self.num_particles):
                # Update velocity and position (using modified PSO rules for permutations)
                for j in range(self.num_tasks):
                    # Calculate velocity update
                    r1, r2 = random.random(), random.random()
                    cognitive_component = self.c1 * r1 * (
                                self.particles_best_position[i][j] - self.particles_position[i][j])
                    social_component = self.c2 * r2 * (self.global_best_position[j] - self.particles_position[i][j])
                    self.particles_velocity[i][j] += self.w * self.particles_velocity[i][
                        j] + cognitive_component + social_component

                # Apply a permutation based velocity handling method
                temp_position = np.argsort(np.argsort(self.particles_velocity[i]))
                self.particles_position[i] = np.random.permutation(temp_position)

                #====== Added by Reza ===================
                # TODO: PSO body should be changed or studied more (Apply a permutation based velocity handling method)
                arr = self.particles_position[i].copy()
                for k in range(len(self.particles_position[i])):
                    if arr[k] >= self.num_devices:
                        arr[k] = np.random.randint(0, self.num_devices)

                self.particles_position[i] = arr.copy()
                #========================================

                # Calculate fitness
                current_fitness = self.fitness(self.particles_position[i])



                # Update personal best
                if current_fitness < self.particles_best_score[i]:
                    self.particles_best_score[i] = current_fitness
                    self.particles_best_position[i] = self.particles_position[i].copy()
                    self.list_fitness.append(current_fitness)

                # Update global best
                if current_fitness < self.global_best_score:
                    best_min_iteration_number = k
                    self.global_best_score = current_fitness
                    self.global_best_position = self.particles_position[i].copy()

            # Dampen inertia weight
            self.w *= self.w_damp

        self.best_min_iteration_number = best_min_iteration_number
        print("best_number_iteration_print = ", best_min_iteration_number)

    def get_best_assignment(self):
        return self.global_best_position, self.global_best_score


