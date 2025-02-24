import csv
import logging
import random
import simpy
import networkx as nx

from examples.PSO_Scheduling.setting import *
from leaf.application import Application, SourceTask, ProcessingTask, SinkTask
from leaf.infrastructure import Node, Link, Infrastructure
from leaf.orchestrator import Orchestrator
from leaf.power import PowerModelNode, PowerModelLink, PowerMeter
from PSO import TaskDeviceScheduler

#########################
RANDOM_SEED = 1

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')

infrastructure = Infrastructure()

sensor_nodes = []
fog_nodes = []
cloud_nodes = []

processing_task_id=0


def read_node_from_csv(file_path_node):
    fog_node_id = 0
    global processing_task_id
    processing_task_id = 0
    # type,name,cu,max_power,static_power,initial_power,remaining_power
    with open(file_path_node, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            node_type = row["type"].lower() if row['type'] is not None else None
            name = row['name'].lower() if row['name'] is not None else None
            cu = float(row['cu']) if row['cu'] is not None else 0  # CU is only relevant for tasks, not data flows
            max_power = float(row['max_power']) if row['max_power'] is not None else 0
            static_power = float(row['static_power']) if row['static_power'] is not None else 0
            initial_power = float(row['initial_power']) if row['initial_power'] is not None else 0
            remaining_power = row['remaining_power'] if row['remaining_power'] is not None else 0
            if node_type == "sensor":
                sensor_node = Node(type=node_type, name=name, cu=cu,
                                   power_model=PowerModelNode(max_power=max_power, static_power=static_power),
                                   initial_power=initial_power,
                                   remaining_power=float(remaining_power))
                sensor_nodes.append(sensor_node)
                infrastructure.add_node(sensor_node)
            if node_type == "fog":
                fog_node = Node(type=node_type, name=name, cu=cu,
                                power_model=PowerModelNode(max_power=max_power, static_power=static_power),
                                initial_power=initial_power,
                                remaining_power=float(remaining_power), id=fog_node_id)
                fog_node_id = fog_node_id + 1
                fog_nodes.append(fog_node)
                infrastructure.add_node(fog_node)
            if node_type == "cloud":
                cloud_node = Node(type=node_type, name=name,
                                  power_model=PowerModelNode(power_per_cu=max_power),
                                  initial_power=initial_power,
                                  )
                cloud_nodes.append(cloud_node)
                infrastructure.add_node(cloud_node)

    # list of sensors,
    # list of fog nodes
    # list of clouds
    # iterate through the file
    # read the attributes for each line
    # create each object


links = []


def create_links_from_sensors():
    for sensor in sensor_nodes:
        for fog_node in fog_nodes:
            link = Link(name=f"{sensor.name}_to_{fog_node.name}", src=sensor, dst=fog_node,
                        latency=0, bandwidth=SENSOR_TO_FOG_LINK_BANDWIDTH,
                        power_model=PowerModelLink(SENSOR_TO_FOG_LINK_ENERGY_PER_BIT))
            infrastructure.add_link(link)
            links.append(link)

    return links


def create_links_to_cloud():
    for fog_node in fog_nodes:
        for cloud_node in cloud_nodes:
            link = Link(name=f"{fog_node.name}_to_{cloud_node.name}", src=fog_node, dst=cloud_node,
                        latency=0, bandwidth=FOG_TO_CLOUD_LINK_BANDWIDTH,
                        power_model=PowerModelLink(FOG_TO_CLOUD_LINK_ENERGY_PER_BIT))
            links.append(link)
            infrastructure.add_link(link)
    return links


applications = []


def create_applications(sensor_nodes, cloud_nodes):
    global processing_task_id
    for sensor in sensor_nodes:
        app1_source_task = SourceTask(cu=0.9 * sensor.power_model.max_power, bound_node=sensor)
        app1_processing_task = ProcessingTask(cu=50.)
        app1_processing_task.scheduling_id = processing_task_id
        processing_task_id = processing_task_id + 1

        #TODO: we consider one cloud, so we set index [0]
        app1_sink_task = SinkTask(cu=150, bound_node=cloud_nodes[0])

        application = Application()  # name=f"Application{sensor.name}"
        application.name = f"Application_{len(applications)}"
        application.add_task(app1_source_task)
        application.add_task(app1_processing_task, incoming_data_flows=[(app1_source_task, 1000)])
        application.add_task(app1_sink_task, incoming_data_flows=[(app1_processing_task, 300)])

        applications.append(application)
        # print(app1_source_task)


def show_application_info():
    number_applications = len(applications)
    number_processing_tasks = 0
    for application in applications:
        print(f"=============")
        print(f"{application.name} {application.graph}")
        print(f"=========Nodes=============")
        for task in application.tasks():
            print(f"Node:{task.id}.")
            print(f"Cu:{task.cu}.")
            if type(task) == ProcessingTask:
                number_processing_tasks = number_processing_tasks + 1

        print(f"========Data Flows (edge)=============")
        for data_flow in application.data_flows():
            print(f"Bit_rate:{data_flow.bit_rate}.")
            if data_flow.links:
                for link in data_flow.links:
                    print(link)


def main():
    """Simple example that places an application in the beginning an performs power measurements on different entities.

    Read the explanations of :func:`create_infrastructure`, :func:`create_application` and :class:`SimpleOrchestrator`
    for details on the scenario setup.

    The power meters can be configured to periodically measure the power consumption of one or more PowerAware entities
    such as applications, tasks, data flows, compute nodes, network links or the entire infrastructure.

    The scenario is running for 5 time steps.

    Log Output:
        INFO	Placing Application(tasks=3):
        INFO	- SourceTask(id=0, cu=0.1) on Node('sensor', cu=0/1).
        INFO	- ProcessingTask(id=1, cu=5) on Node('fog', cu=0/400).
        INFO	- SinkTask(id=2, cu=0.5) on Node('cloud', cu=0/inf).
        INFO	- DataFlow(bit_rate=1000) on [Link('sensor' -> 'fog', bandwidth=0/30000000.0, latency=10)].
        INFO	- DataFlow(bit_rate=200) on [Link('fog' -> 'cloud', bandwidth=0/1000000000.0, latency=5)].
        DEBUG	0: cloud_and_fog_meter: PowerMeasurement(dynamic=2.38W, static=30.00W)
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=2.54W, static=30.20W)
        DEBUG	0.5: application_meter: PowerMeasurement(dynamic=2.54W, static=30.20W)
        DEBUG	1: cloud_and_fog_meter: PowerMeasurement(dynamic=2.38W, static=30.00W)
        DEBUG	1.5: application_meter: PowerMeasurement(dynamic=2.54W, static=30.20W)
        DEBUG	2: infrastructure_meter: PowerMeasurement(dynamic=2.54W, static=30.20W)
        DEBUG	2: cloud_and_fog_meter: PowerMeasurement(dynamic=2.38W, static=30.00W)
        DEBUG	2.5: application_meter: PowerMeasurement(dynamic=2.54W, static=30.20W)
        DEBUG	3: cloud_and_fog_meter: PowerMeasurement(dynamic=2.38W, static=30.00W)
        DEBUG	3.5: application_meter: PowerMeasurement(dynamic=2.54W, static=30.20W)
        DEBUG	4: infrastructure_meter: PowerMeasurement(dynamic=2.54W, static=30.20W)
        DEBUG	4: cloud_and_fog_meter: PowerMeasurement(dynamic=2.38W, static=30.00W)
        DEBUG	4.5: application_meter: PowerMeasurement(dynamic=2.54W, static=30.20W)
    """
    # infrastructure, fog_node, fog_node2, fog_node3 = create_infrastructure()

    # application = read_application_from_csv(csv_file_path, source_node=infrastructure.node("sensor"), sink_node=infrastructure.node("cloud"))
    # orchestrator = SimpleOrchestrator(infrastructure)
    # orchestrator.place(application)

    read_node_from_csv(file_path_node)
    create_links_to_cloud()
    create_links_from_sensors()

    create_applications(sensor_nodes, cloud_nodes)
    show_application_info()

    orchestrator = SimpleOrchestrator(infrastructure)
    for application in applications:
        orchestrator.place(application)


    # x= infrastructure.nodes(PowerModelNode._)
    # y=[infrastructure.node("fog1")]

    application_pm = PowerMeter(applications, name="application_meter")
    # cloud_and_fog_pm = PowerMeter([infrastructure.node("cloud"), infrastructure.node("fog")], name="cloud_and_fog_meter")

    # cloud_and_fog_pm = PowerMeter([infrastructure.nodes("cloud"), infrastructure.nodes("fog")],
    #                             name="cloud_and_fog_meter")

    cloud_and_fog_pm = PowerMeter(
        [infrastructure.node("cloud"), infrastructure.node("fog1"), infrastructure.node("fog2")
            , infrastructure.node("fog3"), infrastructure.node("fog4")],
        name="cloud_and_fog_meter")

    # cloud_and_fog_pm1 = PowerMeter([infrastructure.node("cloud"), infrastructure.node("fog1")],
    #                             name="cloud_and_fog_meter")
    # cloud_and_fog_pm2 = PowerMeter([infrastructure.node("cloud"), infrastructure.node("fog2")],
    #                             name="cloud_and_fog_meter")
    # cloud_and_fog_pm3 = PowerMeter([infrastructure.node("cloud"), infrastructure.node("fog3")],
    #                             name="cloud_and_fog_meter")
    # cloud_and_fog_pm4 = PowerMeter([infrastructure.node("cloud"), infrastructure.node("fog4")],
    #                             name="cloud_and_fog_meter")

    infrastructure_pm = PowerMeter(infrastructure, name="infrastructure_meter", measurement_interval=2)

    # SimPy library is process-based discrete-event simulation framework
    env = simpy.Environment()
    env.process(application_pm.run(env, delay=0.5))
    env.process(cloud_and_fog_pm.run(env))
    # env.process(cloud_and_fog_pm1.run(env))
    # env.process(cloud_and_fog_pm2.run(env))
    # env.process(cloud_and_fog_pm3.run(env))
    # env.process(cloud_and_fog_pm4.run(env))
    # env.process(infrastructure_pm.run(env))
    env.run(until=5)

    print("Final Power Measurements:")
    print("Application Power:", application_pm.get_final_measurement())
    print("Cloud and Fog Power:", cloud_and_fog_pm.get_final_measurement())
    print("Infrastructure Power:", infrastructure_pm.get_final_measurement())


def create_infrastructure():
    """Create the scenario's infrastructure graph.

    It consists of three nodes:
    - A sensor with a computational capacity of one compute unit (CU).
        It has a maximum power usage of 1.8 Watt and a power usage of 0.2 Watt when being idle.
    - A fog node which can compute up to 400 CU; 200 Watt max and 30 Watt static power usage
    - A node representing a cloud data center with unlimited processing power that consumes 0.5 W/CU

    And two network links that connect the nodes:
    - A WiFi connection between the sensor and fog node that consumes 300 J/bit
    - A wide are network (WAN) connection between the fog node and cloud that consumes 6000 J/bit
    """


class SimpleOrchestrator(Orchestrator):
    """Very simple orchestrator that places the processing task on the fog node.

    You can try out other placements here and see how the placement may consume more energy ("cloud")
    or fail because there are not enough resources available ("sensor").
    """

    devices_available_cu = []

    def place(self, application: Application):
        devices_available_cu = []
        tasks_require_cu = []

        devices = []
        tasks = []

        for node in infrastructure.nodes():
            print(node.type)
            if node.type == 'fog':
                devices_available_cu.append(node.cu)
                devices.append(node)


        for task in application.tasks():
            if type(task) == ProcessingTask:
                tasks_require_cu.append(task.cu)
                tasks.append(task)

        print(f"Available CU: {devices_available_cu}")
        print(f"Tasks Available CU: {tasks_require_cu}")
        print("Hel")

        # scheduler = TaskDeviceScheduler(devices_available_cu, tasks_require_cu)
        scheduler = TaskDeviceScheduler(devices, tasks,infrastructure,application)

        scheduler.optimize()

        print('result', scheduler.get_best_assignment())



    # def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
    #     source_node = application.tasks(type_filter=SourceTask)[0].node
    #     dest_node = self.infrastructure.node("cloud")
    #     paths = list(nx.all_simple_paths(self.infrastructure.graph, source=source_node.name, target=dest_node.name))
    #
    #     return self.infrastructure.node(paths[0][1])

    # [5,3,2,4]kk
    def _processing_task_placement(self, task, application):
        source_node = application.tasks(type_filter=SourceTask)[0].node
        dest_node = self.infrastructure.node("cloud")


if __name__ == '__main__':
    random.seed(RANDOM_SEED)
    main()
