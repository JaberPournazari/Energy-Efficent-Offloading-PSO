import logging
import random
import simpy
import numpy as np

from examples.PSO_Scheduling.Csa.csa_proposed_orchestrator import CsaProposedOrchestrator
from examples.PSO_Scheduling.Csa.csa_orchestrator import CsaOrchestrator
from examples.PSO_Scheduling.Pso.EETOPSO_orchestrator import EETOPSOOrchestrator
from examples.PSO_Scheduling.Pso.pso_orchestrator import PSOOrchestrator
from examples.PSO_Scheduling.setting import *
from leaf.application import Application, SourceTask, ProcessingTask, SinkTask
from leaf.infrastructure import Node, Link, Infrastructure
from leaf.power import PowerModelNode, PowerModelLink, PowerMeter
import util,plot_generator

logging.getLogger('matplotlib.font_manager').disabled = True

#########################
RANDOM_SEED = 1

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')

infrastructure = Infrastructure()

sensor_nodes = []
fog_nodes = []
cloud_nodes = []

processing_task_id = 0

devices = []
tasks = []

devices_available_cu = []
tasks_require_cu=[]


########################## NEW @@@@@@@@@@@@@@@
def create_sensors():
    for current_sensor_index in range(NO_SENSORS):
        max_power = random.gauss(SENSOR_MAX_POWER_MEAN, SENSOR_MAX_POWER_STD_DEVIATION)
        static_power = random.gauss(SENSOR_STATIC_POWER_MEAN, SENSOR_STATIC_POWER_STD_DEVIATION)
        cu = random.gauss(SENSOR_CU_POWER_MEAN, SENSOR_CU_STD_DEVIATION)
        sensor_node = Node(type="sensor", name=f"Sensor_{current_sensor_index}", cu=cu,
                           power_model=PowerModelNode(static_power=static_power, max_power=max_power),
                           initial_power=SENSOR_INITIAL_POWER_MEAN,
                           remaining_power=SENSOR_REMAINING_POWER_MEAN)

        sensor_nodes.append(sensor_node)
        infrastructure.add_node(sensor_node)
    return sensor_nodes


def create_fogs(counts):
    power_per_cu = 0.00035
    for index in range(counts):
        #max_power = random.gauss(MICROPROCESSORS_MAX_POWER_MEAN, MICROPROCESSORS_MAX_POWER_STD_DEVIATION)
        max_power = random.uniform(MICROPROCESSORS_MAX_POWER_MEAN-MICROPROCESSORS_MAX_POWER_STD_DEVIATION,
                                   MICROPROCESSORS_MAX_POWER_MEAN+MICROPROCESSORS_MAX_POWER_STD_DEVIATION)

        static_power = random.uniform(MICROPROCESSORS_STATIC_POWER_MEAN-MICROPROCESSORS_STATIC_POWER_STD_DEVIATION,
                                      MICROPROCESSORS_STATIC_POWER_MEAN+MICROPROCESSORS_STATIC_POWER_STD_DEVIATION)

        cu = random.uniform(MICROPROCESSORS_CU_POWER_MEAN - MICROPROCESSORS_CU_STD_DEVIATION,
                          MICROPROCESSORS_CU_POWER_MEAN + MICROPROCESSORS_CU_STD_DEVIATION)

        fog_node = Node(type="fog", name=f"fog_{index}", cu=cu,
                        power_model=PowerModelNode(power_per_cu=power_per_cu, static_power=static_power),
                        initial_power=MICROPROCESSORS_INITIAL_POWER_MEAN,
                        remaining_power=MICROPROCESSORS_REMAINING_POWER_MEAN)
        fog_nodes.append(fog_node)
        infrastructure.add_node(fog_node)

    return fog_nodes

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
        # cu=0.9 * sensor.power_model.max_power
        app1_source_task = SourceTask(cu=0.9 * sensor.power_model.max_power, bound_node=sensor)

        task_size=random.randint(TASK_MEAN-TASK_STD_DEVIATION,TASK_MEAN+TASK_STD_DEVIATION)

        app1_processing_task = ProcessingTask(cu=task_size)
        app1_processing_task.scheduling_id = processing_task_id
        processing_task_id = processing_task_id + 1

        # TODO: we consider one cloud, so we set index [0]
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
    ########################## NEW @@@@@@@@@@@@@@@
    sensor_nodes = create_sensors()
    # fog_nodes = create_fogs(sensor_nodes[1:len(sensor_nodes) // 2])
    fog_nodes = create_fogs(NUMBER_OF_FOGS)

    cloud_node = Node(type='cloud', name=f"cloud", power_model=PowerModelNode(power_per_cu=SERVER_POWER_PER_CU,
                                                                              static_power=SERVER_STATIC_POWER))  # sink
    cloud_nodes.append(cloud_node)
    infrastructure.add_node(cloud_node)
    ##################################################

    create_links_to_cloud()
    create_links_from_sensors()

    create_applications(sensor_nodes, cloud_nodes)
    show_application_info()

    generate_devices_from_infrastructure()

    generate_tasks_from_applications()

    # print(f"Available CU: {devices_available_cu}")
    # print(f"Tasks Available CU: {tasks_require_cu}")

    orchestrator_list=[]
    #
    orchestrator_list.append(EETOPSOOrchestrator(infrastructure, applications, devices, tasks, alpha=.34, beta=.33, gamma=.33,
                                                 delta=0))

    orchestrator_list.append(CsaProposedOrchestrator(infrastructure, applications, devices, tasks, alpha=.34, beta=.33, gamma=.33,
                        delta=0))

    orchestrator_list.append(
        PSOOrchestrator(infrastructure, applications, devices, tasks, alpha=.34, beta=.33, gamma=.33,
                        delta=0))

    orchestrator_list.append(CsaOrchestrator(infrastructure, applications, devices, tasks, alpha=.34, beta=.33, gamma=.33,
                                   delta=0))


    # TODO: We ignore one application argument. Just pass it to the method and working with global variable applications.
    # TODO: It should be corrected.
    # for application in applications:
    #    orchestrator.place(application)

    # Create name for files
    orchestrator_class_name_ls=[]
    for orchestrator in orchestrator_list:
        orchestrator.place(applications[0])
        #orchestrator_class_name_ls.append(orchestrator.__class__.__name__)
        orchestrator_class_name_ls.append(orchestrator.legend)

    #################### per node ####################
    #
    #read file names automatically based on the name of the class (Energy)
    total_node_energy_file_names=[]
    for orchestrator_name in orchestrator_class_name_ls:
        total_node_energy_file_names.append(f'ResultsCsv/{orchestrator_name}-node-energy-total')
    #
    # we all algorithms are running plot can be done # ,'Total Energy Comparison'
    plot_generator.plot_total(
        total_node_energy_file_names,orchestrator_class_name_ls,'Number of Nodes','Total Energy(W)','Total Energy Consumption')


    # read file names automatically based on the name of the class (Time)
    total_node_time_file_names = []
    for orchestrator_name in orchestrator_class_name_ls:
        total_node_time_file_names.append(f'ResultsCsv/{orchestrator_name}-node-time-total')


    plot_generator.plot_total(
         total_node_time_file_names, orchestrator_class_name_ls, 'Number of Nodes', 'Time(S)',
         'Makespan')


    # # read file names automatically based on the name of the class (Ram)
    # total_ram_energy_node_file_names = []
    # for orchestrator_name in orchestrator_class_name_ls:
    #     total_ram_energy_node_file_names.append(f'ResultsCsv/{orchestrator_name}-ram-energy-node-total')
    #
    # plot_generator.plot_total(
    #     total_ram_energy_node_file_names, orchestrator_class_name_ls, 'Number of Nodes', 'Total Ram',
    #     'Total Ram Comparison')
    #
    # # read file names automatically based on the name of the class (Link)
    # total_link_energy_node_file_names = []
    # for orchestrator_name in orchestrator_class_name_ls:
    #     total_link_energy_node_file_names.append(f'ResultsCsv/{orchestrator_name}-link-energy-node-total')
    #
    # plot_generator.plot_total(
    #     total_link_energy_node_file_names, orchestrator_class_name_ls, 'Number of Nodes', 'Total link',
    #     'Total link Comparison')

    #################### per application ####################

    # read file names automatically based on the name of the class (Energy of Applications)
    total_application_energy_file_names = []
    for orchestrator_name in orchestrator_class_name_ls:
        total_application_energy_file_names.append(f'ResultsCsv/{orchestrator_name}-application-energy-total')

    plot_generator.plot_total(
         total_application_energy_file_names, orchestrator_class_name_ls, 'Number of Tasks', 'Energy(w)',
         'Total energy consumption')

    # read file names automatically based on the name of the class (Link energy of Applications)
    total_link_energy_application_file_names = []
    for orchestrator_name in orchestrator_class_name_ls:
        total_link_energy_application_file_names.append(f'ResultsCsv/{orchestrator_name}-link-energy-application-total')

    # plot_generator.plot_total(
    #     total_link_energy_application_file_names, orchestrator_class_name_ls, 'Number of Applications', 'Energy(w)',
    #     'Link energy consumptions based on number of applications')

    # read file names automatically based on the name of the class (Ram energy of Applications)
    total_ram_energy_application_file_names = []
    for orchestrator_name in orchestrator_class_name_ls:
        total_ram_energy_application_file_names.append(f'ResultsCsv/{orchestrator_name}-ram-energy-application-total')

    # plot_generator.plot_total(
    #     total_ram_energy_application_file_names, orchestrator_class_name_ls, 'Number of Applications', 'Energy(w)',
    #     'Ram energy consumptions based on number of applications')

    # read file names automatically based on the name of the class (Ram energy of Applications)
    total_time_application_file_names = []
    for orchestrator_name in orchestrator_class_name_ls:
        total_time_application_file_names.append(f'ResultsCsv/{orchestrator_name}-execution-time-total')

    plot_generator.plot_total(
        total_time_application_file_names, orchestrator_class_name_ls, 'Number of Tasks', 'Time(s)',
        ' Makespan')

    count_tasks_on_nodes_file_names=[]
    for orchestrator_name in orchestrator_class_name_ls:
        count_tasks_on_nodes_file_names.append(f'ResultsCsv/{orchestrator_name}-count-tasks-on-nodes')


    arrays=[]
    for file in count_tasks_on_nodes_file_names:
        temp_arr=util.read_data(file)
        arrays.append([int(i) for i in temp_arr[0]])

    plot_generator.plot_task_distribution(arrays[0],arrays[1],arrays[2],arrays[3])

    min_iter_file_names = []
    for orchestrator_name in orchestrator_class_name_ls:
        min_iter_file_names.append(f'ResultsCsv/{orchestrator_name}-best-iteration')

    task_lists = []
    iteration_lists=[]
    for file in min_iter_file_names:
        temp_arr = util.read_data(file)
        task_lists.append([int(i) for i in np.array(temp_arr)[:, 0]])
        iteration_lists.append([int(i) for i in np.array(temp_arr)[:, 1]])


    labels=[i.legend for i in orchestrator_list]
    colors=['tab:blue','tab:orange','tab:green','tab:red']
    plot_generator.plot_task_min_iterations(task_lists,iteration_lists,labels,colors)




    # x= infrastructure.nodes(PowerModelNode._)
    # y=[infrastructure.node("fog1")]

    application_pm = PowerMeter(applications, name="application_meter")
    # cloud_and_fog_pm = PowerMeter([infrastructure.node("cloud"), infrastructure.node("fog")], name="cloud_and_fog_meter")

    # cloud_and_fog_pm = PowerMeter([infrastructure.nodes("cloud"), infrastructure.nodes("fog")],
    #                             name="cloud_and_fog_meter")

    # TODO: fog_ names shoud be dynamically read from infrastructore nodes with the type of fog.
    # TODO: Rememeber filter node types with fog, it returns sensor and fogs together
    nodes_names_arr = []
    for i in range(len(fog_nodes)):
        nodes_names_arr.append("fog_" + str(i))

    powermeter_arr = [infrastructure.node("cloud")]
    for node_name in nodes_names_arr:
        powermeter_arr.append(infrastructure.node(node_name))
    cloud_and_fog_pm = PowerMeter(powermeter_arr)

    # [n.measure_power() for n in infrastructure.nodes() if n.type=='fog' ]
    # cloud_and_fog_pm = PowerMeter(
    #     [infrastructure.node("cloud"), infrastructure.node("fog_0"), infrastructure.node("fog_1")
    #         , infrastructure.node("fog_2"), infrastructure.node("fog_3"), infrastructure.node("fog_4"),
    #      infrastructure.node("fog_5"), infrastructure.node("fog_6"), infrastructure.node("fog_7"),
    #      infrastructure.node("fog_8"), infrastructure.node("fog_9")],
    #     name="cloud_and_fog_meter")

    infrastructure_pm = PowerMeter(infrastructure, name="infrastructure_meter", measurement_interval=2)

    # SimPy library is process-based discrete-event simulation framework
    env = simpy.Environment()
    env.process(application_pm.run(env, delay=0.5))
    env.process(cloud_and_fog_pm.run(env))
    env.run(until=5)

    # application_energy=application_pm.get_final_measurement()

    print("Final Power Measurements:")
    print("Application Power:", application_pm.get_final_measurement())
    print("Cloud and Fog Power:", cloud_and_fog_pm.get_final_measurement())
    print("Infrastructure Power:", infrastructure_pm.get_final_measurement())

    # power_nodes_ls = [n.measure_power() for n in infrastructure.nodes() if n.type == 'fog']
    # generate_plot_energy(power_nodes_ls, 'Node')

    # TODO: should be caculated in placement after node_energies
    # links_ls = [n.measure_power() for n in infrastructure.links()]
    # generate_plot_energy(links_ls, 'Link')
    # links_ls = [n.measure_power() for n in infrastructure.links()]
    # generate_plot_energy(links_ls, 'Link')

def generate_tasks_from_applications():
    for app in applications:
        for task in app.tasks():
            if type(task) == ProcessingTask:
                tasks_require_cu.append(task.cu)
                tasks.append(task)

def generate_devices_from_infrastructure():
    for node in infrastructure.nodes():
        print(node.type)
        if node.type == 'fog':
            devices_available_cu.append(node.cu)
            devices.append(node)


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


if __name__ == '__main__':
    random.seed(RANDOM_SEED)
    main()
