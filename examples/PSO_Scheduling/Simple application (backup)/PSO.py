############################################################################################################
import numpy as np
import csv
import random
import leaf.application
import leaf.infrastructure
from leaf.infrastructure import *

class TaskDeviceScheduler:
    #def __init__(self, devices, tasks,infrastructure,applications,num_particles=30, max_iter=100, c1=1.5, c2=1.5, w=0.9,
    #             w_damp=0.99):
    def __init__(self, devices, tasks, infrastructure, application, num_particles=10, max_iter=20, c1=1.5, c2=1.5,
                     w=0.9,
                     w_damp=0.99):
        self.devices = devices
        self.tasks = tasks
        self.infrastructure=infrastructure
        self.application=application
        self.num_tasks = len(tasks)
        self.num_devices = len(devices)


        self.num_particles = num_particles
        self.max_iter = max_iter
        self.c1 = c1  # Cognitive (particle) weight
        self.c2 = c2  # Social (swarm) weight
        self.w = w  # Inertia weightx
        self.w_damp = w_damp  # Inertia damping after each iteration

        # Particles initialization
        self.particles_position = np.random.randint(0, self.num_devices, size=(self.num_particles, self.num_tasks))
        self.particles_velocity = np.zeros_like(self.particles_position, dtype=float)
        self.particles_best_position = np.copy(self.particles_position)
        self.particles_best_score = np.array([self.fitness(pos) for pos in self.particles_best_position])
        self.global_best_position = self.particles_best_position[np.argmin(self.particles_best_score)]
        self.global_best_score = np.min(self.particles_best_score)

    def fitness(self, positions):
        i=0
        sum = 0
        for pos in positions:
            self.tasks[i].allocate(self.devices[pos])
            tmp=self.devices[i].measure_power()
            sum = sum +tmp.dynamic +tmp.static
            i=i+1
            #self.devices[pos]=self.tasks[i].node



        for src_task_id, dst_task_id, data_flow in self.application.graph.edges.data("data"):
            src_task = self.application.graph.nodes[src_task_id]["data"]
            dst_task = self.application.graph.nodes[dst_task_id]["data"]

            if isinstance(src_task,leaf.application.SourceTask):
                shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.bound_node.name,
                                                 dst_task.node.name)
            else:
                shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.node.name,
                                                 dst_task.bound_node.name)

            links = [self.infrastructure.graph.edges[a, b, 0]["data"] for a, b in nx.utils.pairwise(shortest_path)]
            #logger.info(f"- {data_flow} on {links}.")
            data_flow.allocate(links)

            for link in links:
                tmp=link.measure_power()
                sum=sum+tmp.dynamic +tmp.static


        for i in range(self.num_tasks):
            self.tasks[i].deallocate()


        for flow in self.application.data_flows():
            flow.deallocate()

        # print(positions)
        # print(sum)
        # print('==================')

        return sum

        # total_response_time = sum(
        #     self.tasks_instructions[i] / self.device_capacities[int(positions[i])] for i in range(self.num_tasks))
        # return total_response_time



    def optimize(self):
        for _ in range(self.max_iter):
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

                # Calculate fitness
                current_fitness = self.fitness(self.particles_position[i])

                # Update personal best
                if current_fitness < self.particles_best_score[i]:
                    self.particles_best_score[i] = current_fitness
                    self.particles_best_position[i] = self.particles_position[i].copy()

                # Update global best
                if current_fitness < self.global_best_score:
                    self.global_best_score = current_fitness
                    self.global_best_position = self.particles_position[i].copy()

            # Dampen inertia weight
            self.w *= self.w_damp

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


