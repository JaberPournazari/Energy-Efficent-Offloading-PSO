import csv
import logging
import random
import simpy

from leaf.application import Application, SourceTask, ProcessingTask, SinkTask
from leaf.infrastructure import Node, Link, Infrastructure
from leaf.orchestrator import Orchestrator
from leaf.power import PowerModelNode, PowerModelLink, PowerMeter

# Assuming Node, Link, PowerModelNode, PowerModelLink, and Infrastructure are defined in your environment

def read_nodes_from_csv(file_path):
    nodes = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['type'] == 'sensor' or row['type'] == 'fog':
                node = Node(
                    row['name'],
                    cu=int(row['cu']),
                    power_model=PowerModelNode(
                        max_power=float(row['max_power']),
                        static_power=float(row['static_power'])
                    ),
                    initial_power=int(row['initial_power']),
                    remaining_power=int(row['remaining_power']) if row['remaining_power'] else None
                )
            elif row['type'] == 'cloud':
                node = Node(
                    row['name'],
                    power_model=PowerModelNode(
                        power_per_cu=float(row['max_power'])
                    ),
                    initial_power=int(row['initial_power'])
                )
            nodes.append(node)
    return nodes


def read_links_from_csv(file_path, nodes):
    links = []
    node_dict = {node.name: node for node in nodes}
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            source = node_dict[row['source']]
            target = node_dict[row['target']]
            link = Link(
                source,
                target,
                latency=int(row['latency']),
                bandwidth=float(row['bandwidth']),
                power_model=PowerModelLink(float(row['power_per_bit']))
            )
            links.append(link)
    return links


def create_infrastructure(nodes_csv_path, links_csv_path):
    nodes = read_nodes_from_csv(nodes_csv_path)
    links = read_links_from_csv(links_csv_path, nodes)

    infrastructure = Infrastructure()
    for link in links:
        infrastructure.add_link(link)

    return infrastructure


# Provide the paths to your CSV files



# Create the infrastructure
infrastructure = create_infrastructure(nodes_csv_path, links_csv_path)

# To verify the infrastructure, you can print out the nodes and links
for node in infrastructure.nodes:
    # print(node)

for link in infrastructure.links:
    # print(link)