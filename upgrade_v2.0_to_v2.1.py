import argparse
import os
from typing import List

import xml.dom.minidom
from mung.io import read_nodes_from_file, write_nodes_to_file
from mung.node import Node
from tqdm import tqdm

CLASS_NAME_MAPPING = {"cClef": "clefC",
                      "fClef": "clefF",
                      "gClef": "clefG",
                      "multiMeasureRest": "restHBar",
                      }


def upgrade_xml_file(nodes: List[Node]) -> List[Node]:
    new_nodes = []
    for node in nodes:
        new_class_name = node.class_name
        if node.class_name in CLASS_NAME_MAPPING:
            new_class_name = CLASS_NAME_MAPPING[node.class_name]
        new_node = Node(node.id, new_class_name, node.top, node.left, node.width, node.height, node.outlinks,
                        node.inlinks, node.mask, node.dataset, node.document, node.data)
        new_nodes.append(new_node)
    return new_nodes


def prettify_xml_file(path):
    dom = xml.dom.minidom.parse(path)
    pretty_xml_as_string = dom.toprettyxml(indent="    ", newl="\n")
    pretty_xml_as_string = '\n'.join(list(filter(lambda x: len(x.strip()), pretty_xml_as_string.split('\n'))))
    pretty_xml_as_string = pretty_xml_as_string.replace('version="1.0" ?>',
                                                        'version="1.0" encoding="utf-8"?>')
    with open(path, "w") as file:
        file.write(pretty_xml_as_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts MUSCIMA++ v2.0 to MUSCIMA++ v2.1')
    parser.add_argument('--source_directory', type=str, default="v2.0",
                        help='Directory of the MUSCIMA++ dataset v2.0')
    parser.add_argument("--destination_directory", type=str, default="v2.1",
                        help="Directory, where the upgraded MUSCIMA++ v2.1 dataset should be written to.")

    flags = parser.parse_args()
    source_directory = flags.source_directory
    destination_directory = flags.destination_directory

    source = os.path.join(source_directory, "data/annotations")
    destination = os.path.join(destination_directory, "data/annotations")

    for annotation_file in tqdm(os.listdir(source), "Converting annotations"):
        try:
            annotation_file_path = os.path.join(source, annotation_file)
            output_file_path = os.path.join(destination, annotation_file)
            document = os.path.splitext(annotation_file)[0]
            nodes = read_nodes_from_file(annotation_file_path)
            upgraded_nodes = upgrade_xml_file(nodes)
            write_nodes_to_file(upgraded_nodes, output_file_path, document=document, dataset="MUSCIMA-pp_2.1")
            prettify_xml_file(output_file_path)
        except:
            print("Error while reading {0}. Skipping file".format(annotation_file))
