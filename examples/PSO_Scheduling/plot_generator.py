import numpy as np
from matplotlib import pyplot as plt
import util


def generate_plot(list_fitness):
    # Example one-dimensional array of energy values
    energy_values = list_fitness

    # Generate x-axis values (iterations)
    iterations = list(range(len(energy_values)))

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(iterations, energy_values, marker='o', linestyle='-')

    # Add title and labels
    plt.title('Energy over Iterations')
    plt.xlabel('Iterations')
    plt.ylabel('Energy')

    # Show the grid
    plt.grid(True)

    # Display the plot
    plt.show()


# # 1 100
# 1000
# 1 100
def generate_plot(values,title,x,y):
    # Example one-dimensional array of values
    Compute_unit_values = values

    # Generate x-axis values (iterations)
    iterations = list(range(len(Compute_unit_values)))

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(iterations, Compute_unit_values, marker='o', linestyle='-')

    # Add title and labels
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)

    # Show the grid
    plt.grid(True)

    # Display the plot
    plt.show()

def generate_plot_count_tasks_on_nodes(count_tasks_on_nodes):

    # Example array where index represents the node number and value represents the count of tasks
    task_counts = count_tasks_on_nodes

    # Generate the x values (node numbers)
    nodes = range(len(task_counts))

    # Create the bar plot
    plt.bar(nodes, task_counts)

    # Label the axes
    plt.xlabel('Node Number')
    plt.ylabel('Task Count')

    # Add a title to the plot
    plt.title('Task Distribution Across Nodes')

    # Set x-axis ticks to be integers
    plt.xticks(nodes)

    # Show the plot
    plt.show()


def generate_plot_energy(power_nodes_ls, item):
    # Example array of 2D tuples with dynamic and static power values
    power_values = power_nodes_ls

    # Generate x-axis values (nodes)
    nodes = list(range(len(power_values)))

    # Extract dynamic and static power values
    dynamic_power = [p.dynamic for p in power_values]
    static_power = [p.static for p in power_values]

    # Define bar width and positions
    bar_width = 0.35
    r1 = np.arange(len(nodes))
    r2 = [x + bar_width for x in r1]

    # Create the bar plot
    plt.figure(figsize=(10, 5))
    plt.bar(r1, dynamic_power, width=bar_width, edgecolor='grey', label='Dynamic Power')
    plt.bar(r2, static_power, width=bar_width, edgecolor='grey', label='Static Power')

    # Add title and labels
    plt.title('Dynamic and Static Power per ' + item)
    plt.xlabel(item)
    plt.ylabel('Power(W)')
    # plt.xticks([r + bar_width / 2 for r in range(len(nodes))], [f'{item} {i}' for i in nodes])
    plt.xticks([r + bar_width / 2 for r in range(len(nodes))], [f'{i}' for i in nodes])

    # Add legend
    plt.legend()

    # Show the plot
    plt.show()

def generate_plot_links(link_nodes_ls, item):
    # Example array of 2D tuples with dynamic and static power values
    power_values = link_nodes_ls

    # Generate x-axis values (nodes)
    nodes = list(range(len(power_values)))

    # Extract dynamic and static power values
    dynamic_power = [p.dynamic for p in power_values]
    static_power = [p.static for p in power_values]

    # Define bar width and positions
    bar_width = 0.35
    r1 = np.arange(len(nodes))
    r2 = [x + bar_width for x in r1]

    # Create the bar plot
    plt.figure(figsize=(10, 5))
    plt.plot(r1, dynamic_power, marker='o',  linestyle='-', label='Dynamic Power')
    plt.plot(r2, static_power, marker='s',  linestyle='-', label='Static Power')

    # Add title and labels
    plt.title('Dynamic and Static Power per ' + item)
    plt.xlabel(item)
    plt.ylabel('Power(W)')
    # plt.xticks([r + bar_width / 2 for r in range(len(nodes))], [f'{item} {i}' for i in nodes])
    plt.xticks([r + bar_width / 2 for r in range(len(nodes))], [f'{i}' for i in nodes])

    # Add legend
    plt.legend()

    # Show the plot
    plt.show()


def generate_plot_applications(application_power_ls, item):
    # Example array of 2D tuples with dynamic and static power values
    power_values = application_power_ls

    # Generate x-axis values (nodes)
    nodes = list(range(len(power_values)))

    # Extract dynamic and static power values
    dynamic_power = [p.dynamic for p in power_values]
    static_power = [p.static for p in power_values]

    # Define bar width and positions
    bar_width = 0.35
    r1 = np.arange(len(nodes))
    r2 = [x + bar_width for x in r1]

    # Create the bar plot
    plt.figure(figsize=(10, 5))
    plt.plot(r1, dynamic_power, marker='o',  linestyle='-', label='Dynamic Power')
    plt.plot(r2, static_power, marker='s',  linestyle='-', label='Static Power')

    # Add title and labels
    plt.title('Dynamic and Static Power per ' + item)
    plt.xlabel(item)
    plt.ylabel('Power(W)')
    # plt.xticks([r + bar_width / 2 for r in range(len(nodes))], [f'{item} {i}' for i in nodes])
    plt.xticks([r + bar_width / 2 for r in range(len(nodes))], [f'{i}' for i in nodes])

    # Add legend
    plt.legend()

    # Show the plot
    plt.show()

def plot_total(csv_files, legends, xlabel, ylabel, title):
    nodes_list = []
    energy_list = []

    for file in csv_files:
        data = util.read_data(file)
        nodes_list.append(np.asarray(data, float)[:, 0])
        energy_list.append(np.asarray(data, float)[:, 1])

    # Data for the first, second, third, and fourth files
    nodes1 = nodes_list[0]
    energy1 = energy_list[0]

    nodes2 = nodes_list[1]
    energy2 = energy_list[1]

    nodes3 = nodes_list[2]
    energy3 = energy_list[2]

    nodes4 = nodes_list[3]  # Fourth dataset
    energy4 = energy_list[3]  # Fourth energy list

    # Ensure all files have the same nodes
    assert len(nodes1) == len(nodes2) == len(nodes3) == len(nodes4), "The nodes in all files do not match."

    # Define the bar width and positions
    bar_width = 0.2  # Adjusted for four bars
    r1 = np.arange(len(nodes1))
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]
    r4 = [x + bar_width for x in r3]  # Fourth dataset positions

    # Create the bar plot
    plt.figure(figsize=(12, 6))
    plt.bar(r1, energy1, width=bar_width, edgecolor='grey', label=legends[0])
    plt.bar(r2, energy2, width=bar_width, edgecolor='grey', label=legends[1])
    plt.bar(r3, energy3, width=bar_width, edgecolor='grey', label=legends[2])
    plt.bar(r4, energy4, width=bar_width, edgecolor='grey', label=legends[3])  # Fourth dataset

    # Add title and labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks([r + 1.5 * bar_width for r in r1], nodes1)

    # Add legend
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.show()


def plot_task_distribution(array1, array2, array3,array4):
    # Node numbers (x-axis)
    nodes = np.arange(1, len(array1) + 1)

    # Plotting the bar chart
    width = 0.2  # the width of the bars, adjusted for four bars

    fig, ax = plt.subplots(figsize=(15, 6))
    bar1 = ax.bar(nodes - 1.5 * width, array1, width, label='P-PSO')
    bar2 = ax.bar(nodes - 0.5 * width, array2, width, label='P-CSA')
    bar3 = ax.bar(nodes + 0.5 * width, array3, width, label='B-PSO')  # Adjust the label as needed
    bar4 = ax.bar(nodes + 1.5 * width, array4, width, label='B-CSA')

    # Add some text for labels, title, and axes ticks
    ax.set_xlabel('Node number')
    ax.set_ylabel('Number of Tasks')

    step = 5  # Adjust step size as needed
    ax.set_xticks(nodes[::step])
    ax.set_xticklabels([f'{i}' for i in nodes[::step]])

    # Rotate the x-axis labels by 45 degrees
    plt.setp(ax.get_xticklabels(), rotation=0, ha="right")

    # Show only every nth label on the y-axis
    y_step = 10  # Adjust step size as needed
    y_ticks = np.arange(0, max(max(array1), max(array2), max(array3), max(array4)) + y_step, y_step)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{i}' for i in y_ticks])

    ax.legend()
    plt.title('Total tasks distribution ')
    # Display the plot
    plt.show()

def plot_task_min_iterations(task_lists, iteration_lists, labels, colors, width=0.2):
    """
    Plot a bar chart with 'number of tasks' on the X-axis and 'iteration number' on the Y-axis,
    with bars placed side by side, using arrays instead of DataFrames.

    Parameters:
    task_lists (list of lists): A list of arrays/lists, each containing 'number of tasks' values.
    iteration_lists (list of lists): A list of arrays/lists, each containing 'iteration number' values.
    labels (list of str): List of labels for each dataset to be used in the legend.
    colors (list of str): List of colors for each dataset bar plot.
    width (float): Width of each bar (default is 0.2).
    """
    plt.figure(figsize=(10, 6))

    # Extract the 'number of tasks' from the first list (assuming all have the same tasks)
    num_tasks = task_lists[0]

    # Determine the number of datasets and the indices
    num_dataframes = len(task_lists)
    indices = np.arange(len(num_tasks))  # Get the indices for each bar group

    # Loop over the datasets and plot each one with an offset
    for i in range(num_dataframes):
        # Offset each bar group by i * width
        plt.bar(indices + i * width, iteration_lists[i],
                width=width, label=labels[i], color=colors[i], alpha=0.7)

    # Customize the plot
    plt.xlabel('Number of Tasks')
    plt.ylabel('Iteration Number')
    plt.title('Iteration count for optimal solution')
    plt.xticks(indices + width * (num_dataframes - 1) / 2, num_tasks)  # Adjust X-axis tick positions
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.show()


