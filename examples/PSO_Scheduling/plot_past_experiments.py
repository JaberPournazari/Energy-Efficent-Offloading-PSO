from examples.PSO_Scheduling import plot_generator
from examples.PSO_Scheduling.util import *
from examples.PSO_Scheduling.plot_generator import *


#
orchestrator_class_name_ls=['pso_orchestrator','csa_orchestrator']
# total_energy_file_names=['ResultsCsv/results 100 task with 10 20 50 70 nodes/psoorchestrator-node-energy-total',
#                          'ResultsCsv/results 100 task with 10 20 50 70 nodes/csaorchestrator-node-energy-total']
#
# # we all algorithms are running plot can be done
# plot_total(
#     total_energy_file_names,orchestrator_class_name_ls,'Number of Nodes','Total Energy','Total Energy Comparison')
#
# # read file names automatically based on the name of the class (Time)
# total_time_file_names = ['ResultsCsv/results 100 task with 10 20 50 70 nodes/psoorchestrator-node-time-total',
#                          'ResultsCsv/results 100 task with 10 20 50 70 nodes/csaorchestrator-node-time-total']
#
# plot_total(
#     total_time_file_names, orchestrator_class_name_ls, 'Number of Nodes', 'Total Time',
#     'Total Time Comparison')
#
# # read file names automatically based on the name of the class (Ram)
# total_ram_file_names = ['ResultsCsv/results 100 task with 10 20 50 70 nodes/psoorchestrator-ram-total',
#                          'ResultsCsv/results 100 task with 10 20 50 70 nodes/csaorchestrator-ram-total']
#
# plot_total(
#     total_ram_file_names, orchestrator_class_name_ls, 'Number of Nodes', 'Total Ram',
#     'Total Ram Comparison')
#
# # read file names automatically based on the name of the class (Link)
# total_link_file_names = ['ResultsCsv/results 100 task with 10 20 50 70 nodes/psoorchestrator-link-energy-total',
#                          'ResultsCsv/results 100 task with 10 20 50 70 nodes/csaorchestrator-link-energy-total']
#
# plot_total(
#     total_link_file_names, orchestrator_class_name_ls, 'Number of Nodes', 'Total link',
#     'Total link Comparison')
#
# count_tasks_on_nodes=read_data('ResultsCsv/results 100 task with 10 20 50 70 nodes/psoorchestrator-count-tasks-on-nodes')
# #convert string values to int
# count_tasks_on_nodes=[int(i) for i in count_tasks_on_nodes[0]]
# generate_plot_count_tasks_on_nodes(count_tasks_on_nodes)

# count_tasks_on_nodes=read_data('ResultsCsv/results 100 task with 10 20 50 70 nodes/csaorchestrator-count-tasks-on-nodes')
# #convert string values to int
# count_tasks_on_nodes=[int(i) for i in count_tasks_on_nodes[0]]
# generate_plot_count_tasks_on_nodes(count_tasks_on_nodes)



# read file names automatically based on the name of the class (Energy of Applications)
total_application_energy_file_names = ['ResultsCsv/psoorchestrator-application-energy-total',
                                       'ResultsCsv/csaorchestrator-application-energy-total']
# plot_generator.plot_total(
#     total_application_energy_file_names, orchestrator_class_name_ls, 'Number of Applications', 'Energy(w)',
#     'Computing energy consumptions based on number of applications')

# read file names automatically based on the name of the class (Link energy of Applications)
# total_link_energy_application_file_names = ['ResultsCsv/psoorchestrator-link-energy-application-total',
#                                             'ResultsCsv/csaorchestrator-link-energy-application-total']
# plot_generator.plot_total(
#     total_link_energy_application_file_names, orchestrator_class_name_ls, 'Number of Applications', 'Energy(w)',
#     'Link energy consumptions based on number of applications')

# read file names automatically based on the name of the class (Ram energy of Applications)
# total_ram_energy_application_file_names = ['ResultsCsv/psoorchestrator-ram-energy-application-total',
#                                            'ResultsCsv/csaorchestrator-ram-energy-application-total']
# plot_generator.plot_total(
#     total_ram_energy_application_file_names, orchestrator_class_name_ls, 'Number of Applications', 'Energy(w)',
#     'Ram energy consumptions based on number of applications')


# read file names automatically based on the name of the class (Ram energy of Applications)
total_time_application_file_names = ['ResultsCsv/psoorchestrator-execution-time-total',
                                     'ResultsCsv/csaorchestrator-execution-time-total']
plot_generator.plot_total(
    total_time_application_file_names, orchestrator_class_name_ls, 'Number of Applications', 'Time(s)',
    'Execution time based on number of applications')

count_tasks_on_nodes_file_names=['ResultsCsv/psoorchestrator-count-tasks-on-nodes',
                                 'ResultsCsv/csaorchestrator-count-tasks-on-nodes']
arrays=[]
for file in count_tasks_on_nodes_file_names:
    temp_arr=util.read_data(file)
    arrays.append([int(i) for i in temp_arr[0]])

plot_generator.plot_task_distribution(arrays[0],arrays[1])