import argparse
import os
from copy import deepcopy
from xml.etree.ElementTree import parse, ElementTree, Element
import xml.dom.minidom

from muscima.cropobject import CropObject
from muscima.io import parse_cropobject_list
from tqdm import tqdm
from typing import List, Dict


def upgrade_xml_file(element_tree: ElementTree, crop_objects: List[CropObject]) -> ElementTree:
    nodes = Element("Nodes", attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                     "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"})

    class_mapping = {"notehead-full": "noteheadFull",
                     "grace-notehead-full": "noteheadFullSmall",
                     "grace-notehead-empty": "noteheadHalfSmall",
                     "duration-dot": "augmentationDot",
                     "sharp": "accidentalSharp",
                     "flat": "accidentalFlat",
                     "natural": "accidentalNatural",
                     "double_sharp": "accidentalDoubleSharp",
                     "double_flat": "accidentalDoubleFlat",
                     "whole_rest": "restWhole",
                     "half_rest": "restHalf",
                     "quarter_rest": "restQuarter",
                     "8th_rest": "rest8th",
                     "16th_rest": "rest16th",
                     "32th_rest": "rest32nd",
                     "multiMeasureRest": "multiMeasureRest",
                     "ledger_line": "legerLine",
                     }

    id_to_cropobject_mapping = {o.objid: o for o in crop_objects}  # type: Dict[int, CropObject]

    for crop_object_node in element_tree.findall("*/CropObject"):
        # Copy all values from an existing crop-object
        node = deepcopy(crop_object_node)  # type: Element

        # Rename CropObject -> Node
        node.tag = "Node"
        id = None
        for child in node:
            # Remove the leading ML prefix from MLClassName, in case it still exists
            if child.tag == "MLClassName":
                child.tag = "ClassName"

            # Map classes to new names
            if child.tag == "ClassName":
                if child.text in class_mapping:
                    child.text = class_mapping[child.text]

            if child.tag == "Id":
                id = int(child.text)

        # Split notehead-empty into noteheadHalf or noteheadWhole
        crop_object = id_to_cropobject_mapping[id]
        if crop_object.clsname == "notehead-empty":
            notehead_has_a_stem_attached = False
            for outgoing_object in crop_object.get_outlink_objects(crop_objects):  # type: CropObject
                if outgoing_object.clsname == "stem":
                    notehead_has_a_stem_attached = True

            if notehead_has_a_stem_attached:
                node.find("ClassName").text = "noteheadHalf"
            else:
                node.find("ClassName").text = "noteheadWhole"

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

    directory_mapping = {"data/cropobjects_withstaff": "data/nodes_with_staff_annotations"}

    for source_subdirectory, destination_subdirectory in directory_mapping.items():
        source = os.path.join(source_directory, source_subdirectory)
        destination = os.path.join(destination_directory, destination_subdirectory)

        for annotation_file in tqdm(os.listdir(source), "Converting annotations"):
            annotation_file_path = os.path.join(source, annotation_file)
            crop_objects = parse_cropobject_list(annotation_file_path)
            tree = parse(annotation_file_path)
            upgraded_tree = upgrade_xml_file(tree, crop_objects)

            upgraded_tree.write(os.path.join(destination, annotation_file), encoding="utf-8", xml_declaration=True)
            prettify_xml_file(os.path.join(destination, annotation_file))
