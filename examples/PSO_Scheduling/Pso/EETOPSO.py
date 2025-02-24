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
                 w=0.9, w_damp=0.99,alpha=.25,beta=.25,gamma=.25,delta=.25):
        self.devices = devices
        self.tasks = tasks
        self.infrastructure=infrastructure
        self.applications=applications
        self.num_tasks = len(tasks)
        self.num_devices = len(devices)

        # wight vectors initialization of multi-objective parameters
        self.__check_multi_params__(alpha,beta,gamma, delta)
        self.alpha=alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.list_fitness = []

        self.EnergyPerC = []
        self.EnergyPerT = []
        self.EnergyPerR = []
        self.TimePerC = []

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
        self.best_min_iteration_number=self.max_iter

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
            #try:
            #if (self.devices[pos].cu - self.devices[pos].used_cu) >= self.tasks[i].cu:
                # if pos>=self.num_devices:
                #     pos= self.num_devices-1

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
        sum_total = sum_link+sum_node


        # print(positions)
        # print(sum_total)
        # print('==================')

        ############################ Gradient descent #######################################
        self.EnergyPerC.append(sum_node)
        self.EnergyPerT.append(sum_link)
        self.EnergyPerR.append(sum_time)
        self.TimePerC.append(sum_ram)


        #everytime we reset alpha, beta, gamma and delta
        self.alpha = 45.0
        self.beta = 15.0
        self.gamma = 25.0
        self.delta = 15.0

        # Learning rate
        eta = 0.01

        # Number of iterations
        iterations = 10

        # Gradient Descent with Projection
        for _ in range(iterations):
            # Compute the gradients
            grad_alpha = np.mean(self.EnergyPerC)
            grad_beta = np.mean(self.EnergyPerT)
            grad_gamma = np.mean(self.EnergyPerR)
            grad_delta = np.mean(self.TimePerC)

            # print("grad_delta", f"{grad_delta}")

            # Update the coefficients
            self.alpha += eta * grad_alpha
            self.beta += eta * grad_beta
            self.gamma += eta * grad_gamma
            self.delta += eta * grad_delta

            # print("delta", f"{self.delta}")

            # Project the coefficients to the range [0, 100]
            self.alpha = max(0, min(100, self.alpha))
            self.beta = max(0, min(100, self.beta))
            self.gamma = max(0, min(100, self.gamma))
            self.delta = max(0, min(100, self.delta))

            # Output the optimized coefficients

            # print(f'Optimized alpha: {self.alpha}')
            # print(f'Optimized beta: {self.beta}')
            # print(f'Optimized gamma: {self.gamma}')
            # print(f'Optimized delta: {self.delta}')
            # print('===============================')

        ############################ Gradient descent #######################################

        # TODO: Do not final sum for fitness
        return self.alpha*sum_node + self.beta*sum_link + self.gamma*sum_time + self.delta*sum_ram

        # total_response_time = sum(
        #     self.tasks_instructions[i] / self.device_capacities[int(positions[i])] for i in range(self.num_tasks))
        # return total_response_time



    def optimize(self):
        print('Starting P-PSO')
        best_min_iteration_number=self.max_iter
        for _ in range(self.max_iter):
            number_iteration = _
            print(number_iteration)
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
                    best_min_iteration_number = number_iteration
                    self.global_best_score = current_fitness
                    self.global_best_position = self.particles_position[i].copy()

            # Dampen inertia weight
            self.w *= self.w_damp

        self.best_min_iteration_number=best_min_iteration_number
        print("best_number_iteration_print = ",best_min_iteration_number)
    def get_best_assignment(self):
        return self.global_best_position, self.global_best_score


# def read_data_from_csv(file_path):
#     device_capacities = []
#     tasks_instructions = []
#     with open(file_path, newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if 'Type' in row and row['Type'].lower() == 'device':
#                 device_capacities.append(float(row['Capacity']))
#             elif 'Type' in row and row['Type'].lower() == 'task':
#                 tasks_instructions.append(float(row['Instructions']))
#     return device_capacities, tasks_instructions
#
# class Main:
#     def __init__(self, file_path):
#         self.device_capacities, self.tasks_instructions = read_data_from_csv(file_path)
#
#     def run(self):
#         scheduler = TaskDeviceScheduler(self.device_capacities, self.tasks_instructions)
#         scheduler.optimize()
#         best_assignment, best_score = scheduler.get_best_assignment()
#
#         print("Best device assignments per task:", best_assignment)
#         print("Total system response time:", best_score)

if __name__ == "__main__":

    main_program = Main()
    main_program.run()


