import argparse
import os
from copy import deepcopy
from xml.etree.ElementTree import parse, ElementTree, Element
import xml.dom.minidom

from tqdm import tqdm


def upgrade_xml_file(element_tree: ElementTree) -> ElementTree:
    nodes = Element("Nodes", attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                     "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"})

    class_mapping = {"notehead-full": "noteheadFull",
                     "grace-notehead-full": "grace-noteheadFull",

                     }

    for crop_object in element_tree.findall("*/CropObject"):
        # Copy all values from an existing crop-object
        node = deepcopy(crop_object)  # type: Element

        # Rename CropObject -> Node
        node.tag = "Node"

        for child in node:
            # Remove the leading ML prefix from MLClassName, in case it still exists
            if child.tag == "MLClassName":
                child.tag = "ClassName"

            # Map classes to new names
            if child.tag == "ClassName":
                if child.text in class_mapping:
                    child.text = class_mapping[child.text]


        nodes.append(node)

    return ElementTree(nodes)


def prettify_xml_file(path):
    dom = xml.dom.minidom.parse(path)
    pretty_xml_as_string = dom.toprettyxml(indent="    ", newl="\n")
    pretty_xml_as_string = '\n'.join(list(filter(lambda x: len(x.strip()), pretty_xml_as_string.split('\n'))))
    pretty_xml_as_string = pretty_xml_as_string.replace('version="1.0" ?>', 'version="1.0" encoding="utf-8"?>')
    with open(path, "w") as file:
        file.write(pretty_xml_as_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts MUSCIMA++ v1.0 to MUSCIMA++ v2.0')
    parser.add_argument('--source_directory', type=str, default="v1.0",
                        help='Directory of the MUSCIMA++ dataset v1.0')
    parser.add_argument("--destination_directory", type=str, default="v2.0",
                        help="Directory, where the upgraded MUSCIMA++ v2.0 dataset should be written to.")

    flags = parser.parse_args()

    source_directory = flags.source_directory
    destination_directory = flags.destination_directory

    directory_mapping = {"data/cropobjects_manual": "data/nodes_without_staff_annotations",
                         "data/cropobjects_withstaff": "data/nodes_with_staff_annotations"}

    for source_subdirectory, destination_subdirectory in directory_mapping.items():
        source = os.path.join(source_directory, source_subdirectory)
        destination = os.path.join(destination_directory, destination_subdirectory)

        for annotation_file in tqdm(os.listdir(source), "Converting annotations"):
            tree = parse(os.path.join(source, annotation_file))
            upgraded_tree = upgrade_xml_file(tree)

            upgraded_tree.write(os.path.join(destination, annotation_file), encoding="utf-8", xml_declaration=True)
            prettify_xml_file(os.path.join(destination, annotation_file))
