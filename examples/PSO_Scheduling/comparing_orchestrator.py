import networkx as nx

from examples.PSO_Scheduling.setting import MICROPROCESSORS_POWER_RAM
from examples.PSO_Scheduling.util import *
from examples.PSO_Scheduling.plot_generator import *
from leaf.application import ProcessingTask, Application, SourceTask
from leaf.orchestrator import Orchestrator
from leaf.power import PowerMeasurement


class comparing_orchestrator(Orchestrator):
    def __init__(self, infrastructure, applications, scheduler):
        self.infrastructure = infrastructure
        self.applications = applications
        self.scheduler = scheduler

    def place(self, application: Application):
        devices_len = len(self.devices)
        orchestrator_legend = self.legend
        self.scheduler.optimize()

        print(f'starting placement {orchestrator_legend}')
        print('result', self.scheduler.get_best_assignment())
        # [0] index array for min position
        positions = self.scheduler.get_best_assignment()[0]

        positions_ls = []
        application_powers = []
        links_ls = []
        node_times = [0 for pos in set(self.devices)]
        i = 0
        for pos in positions:
            # try:
            self.tasks[i].allocate(self.devices[pos])
            # except Exception as ex:
            # print(ex)

            # calculating node consumed time
            node_times[pos] = node_times[pos] + self.tasks[i].cu / self.devices[pos].cu

            energy = self.infrastructure.node(self.devices[pos].name).measure_power()
            positions_ls.append((pos, energy))

            # placing applications
            app = self.applications[i]

            for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
                src_task = app.graph.nodes[src_task_id]["data"]
                dst_task = app.graph.nodes[dst_task_id]["data"]

                if isinstance(src_task, SourceTask):
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.bound_node.name,
                                                     dst_task.node.name)
                else:
                    shortest_path = nx.shortest_path(self.infrastructure.graph, src_task.node.name,
                                                     dst_task.bound_node.name)

                links = [self.infrastructure.graph.edges[a, b, 0]["data"] for a, b in
                         nx.utils.pairwise(shortest_path)]
                data_flow.allocate(links)
            # ==================end of placing applications

            # calculating application links power (we consider each application has one link)
            # application_powers.append([n.measure_power() for n in links][0])

            application_powers.append(app.measure_power())

            links_ls = [n.measure_power() for n in self.infrastructure.links()]

            for src_task_id, dst_task_id, data_flow in app.graph.edges.data("data"):
                data_flow.deallocate()

            self.tasks[i].deallocate()
            i = i + 1

        # sum ram
        sum_time = sum(node_times)
        sum_ram = sum_time * MICROPROCESSORS_POWER_RAM

        write_total(sum_time, f'{orchestrator_legend}-node-time', devices_len)
        write_total(sum_ram, f'{orchestrator_legend}-ram-energy-node', devices_len)

        node_energies = []
        # power_nodes_ls = [n.measure_power() for n in infrastructure.nodes() if n.type == 'fog']
        positions_set = set(positions)
        # delete iteration node numbers (set)
        for j in positions_set:
            # it means that tasks that are running in each node, make a sum of their dynamic energy for each node
            # example for node 0 = how many times used so dynamic power sum
            selected = [k for k in positions_ls if k[0] == j]
            sum_dynamic = 0
            for sel in selected:
                sum_dynamic = sum_dynamic + sel[1].dynamic
            # if node iretated 3 times , just  static power sum 1 times
            node_energies.append(PowerMeasurement(sum_dynamic, selected[0][1].static))

        # write results in separate files with static and dynamic values
        write_to_csv(node_energies, f'{orchestrator_legend}-node-energy')




        # This list is for generating plot of how many tasks will be executing on each node
        count_tasks_on_nodes = np.zeros(devices_len, dtype=np.uint, order='C')

        for i in range(len(positions)):
            count_tasks_on_nodes[positions[i]] = count_tasks_on_nodes[positions[i]] + 1

        # generate_plot_count_tasks_on_nodes(count_tasks_on_nodes)
        write_data(f'ResultsCsv/{orchestrator_legend}-count-tasks-on-nodes', count_tasks_on_nodes)

        # power_nodes_ls = [n.measure_power() for n in infrastructure.nodes() if n.type == 'fog']
        # generate_plot_energy(node_energies, 'Node')

        # we can comment if running is lasting
        # generate_plot_energy(links_ls, 'Link')
        write_to_csv(node_energies, f'{orchestrator_legend}-link-energy')

        # total link
        dynamic_power = [p.dynamic for p in links_ls]
        static_power = [p.static for p in links_ls]
        sum_link = sum(dynamic_power) + sum(static_power)
        write_total_power(links_ls, f'{orchestrator_legend}-link-energy-node', devices_len)

        # write results total energy
        #old one just write node energies without sum_ram and sum_link
        #write_total_power(node_energies, f'{orchestrator_legend}-node-energy', devices_len)

        dynamic_power = [p.dynamic for p in node_energies]
        static_power = [p.static for p in node_energies]
        total_power = sum(dynamic_power) + sum(static_power)
        write_total(total_power+sum_ram + sum_link ,f'{orchestrator_legend}-node-energy', devices_len)

        # based on number of applications
        # old one just write node energies without sum_ram and sum_link
        #write_total_power(node_energies, f'{orchestrator_legend}-application-energy', len(self.applications))

        write_total(total_power+sum_ram + sum_link, f'{orchestrator_legend}-application-energy', len(self.applications))


        # self._calculate_sum_static_dynamic(node_energies)
        # dynamic_power = [p.dynamic for p in node_energies]
        # static_power = [p.static for p in node_energies]
        # total_power = sum(dynamic_power) + sum(static_power)
        # write_total(sum_ram+ self._calculate_sum_static_dynamic(sum_link)+
        #             self._calculate_sum_static_dynamic(node_energies)
        #             , f'{orchestrator_legend}-application', len(self.applications))

        # write_total_power(sum_link, f'{orchestrator_legend}-link-energy', len(self.applications))

        #write_data(f'ResultsCsv/{orchestrator_legend}-link-energy-total', [len(self.applications), sum_link])

        write_total_power(links_ls, f'{orchestrator_legend}-link-energy-application', len(self.applications))

        #write_total_power(sum_ram, f'{orchestrator_legend}-ram-energy', len(self.applications))
        write_data(f'ResultsCsv/{orchestrator_legend}-ram-energy-application-total', [len(self.applications), sum_ram])

        #write_total_power(sum_time, f'{orchestrator_legend}-execution-time', len(self.applications))
        write_data(f'ResultsCsv/{orchestrator_legend}-execution-time-total', [len(self.applications), sum_time])

        #write best iteration
        write_data(f'ResultsCsv/{orchestrator_legend}-best-iteration', [len(self.applications), self.scheduler.best_min_iteration_number])

        # generate_plot(node_times,'Node spent times','Node','Time(s)')
        # write_to_csv(node_times, 'Pso-node-times')

        # generate_plot_energy(application_powers,'Application')

        # print('list_fitness', self.scheduler.list_fitness)

        # generate_plot(scheduler.list_fitness)
        # generate_plot_cu(devices_available_cu)
        # print("done")

    def _calculate_sum_static_dynamic(self, energy):
        if type(energy) == list:
            dynamic_power = [p.dynamic for p in energy]
            static_power = [p.static for p in energy]
            total_power = sum(dynamic_power) + sum(static_power)
            return total_power
        else:
            return energy.dynamic + energy.static

    # [5,3,2,4]kk
    def _processing_task_placement(self, task, application):
        source_node = application.tasks(type_filter=SourceTask)[0].node
        dest_node = self.infrastructure.node("cloud")
