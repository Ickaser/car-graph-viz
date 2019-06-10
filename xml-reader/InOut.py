#!/usr/bin/env python
"""
   Description: I/O module for an XML file containing data for an undirected-graph-like map
   Author: Paolo Fazzini
   Email: paolo.fazzini@iia.cnr.it
   Company: CNR-IIA
   Copyright: 2019
   Version: 0.1
"""


import xml.etree.ElementTree as ET
from CreateGraph import Node, Street


def write_XML(nodes, streets):
    root = ET.Element('street_and_node_data')
    #nodes
    node_list = ET.SubElement(root, 'nodes')
    for node in nodes:
        n_ = ET.SubElement(node_list, 'node', id = str(node.id))
        ET.SubElement(n_, 'x').text = str(node.x)
        ET.SubElement(n_, 'y').text = str(node.y)
        node_street_list = ET.SubElement(n_, 'streets')               
        for street in node.streets:
            s_ = ET.SubElement(node_street_list, 'street', id = str(street.id))
            ET.SubElement(s_, 'name').text = str(street.name)
            ET.SubElement(s_, 'node_distance').text = str(street.node_distance)
            ET.SubElement(s_, 'speed_limit').text = str(street.speed_limit)
            ET.SubElement(s_, 'allowed_directions').text = str(street.allowed_directions)
            node_street_node_list = ET.SubElement(s_, 'street_nodes')
            for street_node in street.nodes:
                sn_ = ET.SubElement(node_street_node_list, 'street_node', id = str(street_node.name))
                ET.SubElement(sn_, 'x').text = str(street_node.x)
                ET.SubElement(sn_, 'y').text = str(street_node.y)
    #streets
    street_list = ET.SubElement(root, 'streets')
    for street in streets:
        s_ = ET.SubElement(street_list, 'street', id = str(street.id))
        ET.SubElement(s_, 'name').text = str(street.name)
        ET.SubElement(s_, 'node_distance').text = str(street.node_distance)
        ET.SubElement(s_, 'speed_limit').text = str(street.speed_limit)
        ET.SubElement(s_, 'allowed_directions').text = str(street.allowed_directions)
        street_node_list = ET.SubElement(s_, 'nodes')               
        for street_node in street.nodes:
            n_ = ET.SubElement(street_node_list, 'node', id = str(street_node.id))
            ET.SubElement(n_, 'x').text = str(street_node.x)
            ET.SubElement(n_, 'y').text = str(street_node.y)

    data = ET.ElementTree(root)
    data.write('storage.xml')  
    


def read_XML(nodes, streets):
    #nodes
    root = ET.parse('storage.xml').getroot()  
    for node_list in root.findall('nodes/node'):
        node = Node()
        node.id = int(node_list.attrib['id'])
        node.x = int(node_list.find('x').text)
        node.y = int(node_list.find('y').text)
        for node_street_list in node_list.findall('streets/street'):
            street = Street()
            street.id = int(node_street_list.attrib['id'])
            street.name = node_street_list.find('name').text
            street.node_distance = float(node_street_list.find('node_distance').text)
            street.speed_limit = int(node_street_list.find('speed_limit').text)
            street.allowed_directions = int(node_street_list.find('allowed_directions').text)
            for street_node_list in node_street_list.findall('street_nodes/street_node'):
                street_node = Node()
                street_node.id = int(street_node_list.attrib['id']) 
                street_node.x = int(street_node_list.find('x').text)
                street_node.y = int(street_node_list.find('y').text)
                street.nodes.append(street_node)
            node.streets.append(street)
        nodes.append(node)          
    #streets          
    for street_list in root.findall('streets/street'):
        street = Street()
        street.id = int(street_list.attrib['id'])
        street.name = street_list.find('name').text
        street.node_distance = float(street_list.find('node_distance').text)
        street.speed_limit = int(street_list.find('speed_limit').text)
        street.allowed_directions = int(street_list.find('allowed_directions').text)
        for node_street_list in street_list.findall('nodes/node'):
            node = Node()
            node.id = int(node_street_list.attrib['id'])
            node.x = int(node_street_list.find('x').text)
            node.y = int(node_street_list.find('y').text)
            street.nodes.append(node)
        streets.append(street)          
