import logging
from abc import ABC
from functools import partial
from typing import Callable, List

import networkx as nx

from examples.PSO_Scheduling.Pso.EETOPSO import TaskDeviceScheduler
from leaf.application import ProcessingTask, Application, SourceTask, SinkTask
from leaf.infrastructure import Infrastructure, Node
from leaf.power import PowerModelNode

ProcessingTaskPlacement = Callable[[ProcessingTask, Application, Infrastructure], Node]
DataFlowPath = Callable[[nx.Graph, str, str], List[str]]

logger = logging.getLogger(__name__)


class Orchestrator(ABC):
    def __init__(self, infrastructure: Infrastructure, shortest_path: DataFlowPath = None):
        """Orchestrator which is responsible for allocating/placing application tasks on the infrastructure.

        Args:
            infrastructure: The infrastructure graph which the orchestrator operates on.
            shortest_path: A function for determining shortest/optimal paths between nodes.
                This function is called for every data flow between nodes that have been placed on the infrastructure.
                It takes the infrastructure graph, the source node, and target node and maps it to the list of nodes
                on the path. Defaults to `networkx.shortest_path`. More algorithms can be found
                `here <https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html>`_.
        """
        self.infrastructure = infrastructure
        if shortest_path is None:
            self.shortest_path = partial(nx.shortest_path, weight="latency")

    power_model_node_requirement = PowerModelNode(max_power=200, static_power=30)
    def place(self, application: Application):
        """Place an application on the infrastructure."""
        logger.info(f"Placing {application}:")
        for task in application.tasks():
            if isinstance(task, (SourceTask, SinkTask)):
                node = task.bound_node
            elif isinstance(task, ProcessingTask):
                node,device_ca, task_ins = self._processing_task_placement(task, application)
                print('result:', device_ca,task_ins)
                scheduler = TaskDeviceScheduler(device_ca, task_ins)
                scheduler.optimize()
                best_assignment, best_score = scheduler.get_best_assignment()
                print('Final:', best_assignment, best_score)

                print("Fuck device assignments per task:", best_assignment)
                print("Total system response time:", best_score)
            else:
                raise TypeError(f"Unknown task type {task}")
            task.allocate(node)

        for src_task_id, dst_task_id, data_flow in application.graph.edges.data("data"):
            src_task = application.graph.nodes[src_task_id]["data"]
            dst_task = application.graph.nodes[dst_task_id]["data"]


            shortest_path = self.shortest_path(self.infrastructure.graph, src_task.node.name, dst_task.node.name)
            links = [self.infrastructure.graph.edges[a, b, 0]["data"] for a, b in nx.utils.pairwise(shortest_path)]
            logger.info(f"- {data_flow} on {links}.")
            data_flow.allocate(links)

    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        fog_node_ids = ['fog', 'fog2', 'fog3']
        device_capacities = []
        tasks_instructions = []
        for node_id in fog_node_ids:
            node = self.infrastructure.node(node_id)
            available_cu: float = node.cu - node.used_cu
            utilization_power = node.utilization_requirement(processing_task.cu)
            power_model_node = (self.power_model_node_requirement.measure_power_requirement())
            requirement_energy_consumption = power_model_node * utilization_power

            # print ('Node ID:', node_id)
            # print('Node remaining energy:',node.remaining_power)
            # print('Node available_cu:',node.cu)
            # print('Task required estimated energy consumption:', requirement_energy_consumption)
            # print('Task required estimated CU consumption:', processing_task.cu)
            # print('-----------------------------------------')
            if available_cu >= processing_task.cu and node.remaining_power > requirement_energy_consumption:
                print('Selected node:', node_id)
                node.update_remain_energy_consumption(requirement_energy_consumption)
                print('-----------------------------------------')
                return self.infrastructure.node(node_id), tasks_instructions, device_capacities

            device_capacities.append(available_cu)
            tasks_instructions.append(processing_task.cu)

        print(f'device_capacities: {device_capacities}')
        print(f'tasks_instructions: {tasks_instructions}')
        print('Hello')

            # device_capacities, tasks_instructions = self.read_data_from_csv(file_path2)
            #
            # scheduler = TaskDeviceScheduler(device_capacities, tasks_instructions)
            # scheduler.optimize()
            # best_assignment, best_score = scheduler.get_best_assignment()
            #
            # print("Fuck device assignments per task:", best_assignment)
            # print("Total system response time:", best_score)

        logging.error("All fog nodes are full or cannot accommodate the task based on dynamic power criteria.")
        return None

    # @abstractmethod
    # def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
    #     pass
    #
