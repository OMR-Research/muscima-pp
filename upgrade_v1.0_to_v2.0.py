import argparse
import os
from copy import deepcopy
from xml.etree.ElementTree import parse, ElementTree, Element
import xml.dom.minidom

from muscima.cropobject import CropObject
from muscima.io import parse_cropobject_list
from tqdm import tqdm
from typing import List, Dict, Union

CLASS_NAME_MAPPING = {"notehead-full": "noteheadFull",
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
                      "hairpin-cresc.": "dynamicCrescendoHairpin",
                      "hairpin-decr.": "dynamicDiminuendoHairpin",
                      }

UPWARDS_FLAG_NAME_MAPPING = {"8th_flag": "flag8thUp",
                             "16th_flag": "flag16thUp",
                             "32th_flag": "flag32ndUp",
                             "64th_and_higher_flag": "flag64thUp",
                             }
DOWNWARDS_FLAG_NAME_MAPPING = {"8th_flag": "flag8thDown",
                               "16th_flag": "flag16thDown",
                               "32th_flag": "flag32ndDown",
                               "64th_and_higher_flag": "flag64thDown",
                               }


def upgrade_xml_file(element_tree: ElementTree, crop_objects: List[CropObject]) -> ElementTree:
    nodes = Element("Nodes", attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                     "xsi:noNamespaceSchemaLocation": "CVC-MUSCIMA_Schema.xsd"})

    id_to_cropobject_mapping = {o.objid: o for o in crop_objects}  # type: Dict[int, CropObject]

    for crop_object_node in element_tree.findall("*/CropObject"):
        # Copy all values from an existing crop-object
        node = deepcopy(crop_object_node)  # type: Element
        id = int(node.find("Id").text)
        crop_object = id_to_cropobject_mapping[id]

        node = remove_xml_namespace_before_id_attribute(node)
        node = rename_CropObject_to_Node(node)
        node = rename_MLClassName_to_ClassName(node)
        node = map_class_to_new_name(node)

        if crop_object.clsname == "notehead-empty":
            node = split_notehead_empty_into_notheadHalf_or_noteheadWhole(node, crop_object, crop_objects)

        if "_flag" in crop_object.clsname:
            node = split_flag_into_flagUp_or_flagDown(node, crop_object, crop_objects)

        if node is not None:
            nodes.append(node)

    return ElementTree(nodes)


def rename_CropObject_to_Node(node):
    node.tag = "Node"
    return node


def rename_MLClassName_to_ClassName(node):
    """ Removes the leading ML prefix from MLClassName, in case it still exists """
    for child in node:
        if child.tag == "MLClassName":
            child.tag = "ClassName"
    return node


def map_class_to_new_name(node):
    for child in node:
        if child.tag == "ClassName":
            if child.text in CLASS_NAME_MAPPING:
                child.text = CLASS_NAME_MAPPING[child.text]
    return node


def split_notehead_empty_into_notheadHalf_or_noteheadWhole(node: Element, notehead_empty: CropObject,
                                                           crop_objects: List[CropObject]) -> Element:
    notehead_has_a_stem_attached = False
    for outgoing_object in notehead_empty.get_outlink_objects(crop_objects):  # type: CropObject
        if outgoing_object.clsname == "stem":
            notehead_has_a_stem_attached = True

    if notehead_has_a_stem_attached:
        node.find("ClassName").text = "noteheadHalf"
    else:
        node.find("ClassName").text = "noteheadWhole"
    return node


def split_flag_into_flagUp_or_flagDown(node: Element, flag: CropObject,
                                       crop_objects: List[CropObject]) -> Union[None, Element]:
    center_of_flag = flag.top + (flag.bottom - flag.top) / 2.0

    flag_converted_successfully = False
    for outgoing_object in flag.get_inlink_objects(crop_objects):  # type: CropObject
        if "notehead" in outgoing_object.clsname:
            center_of_notehead = outgoing_object.top + (outgoing_object.bottom - outgoing_object.top) / 2.0
            flag_converted_successfully = True
            if center_of_flag < center_of_notehead:
                node.find("ClassName").text = UPWARDS_FLAG_NAME_MAPPING[node.find("ClassName").text]
                break
            else:
                node.find("ClassName").text = DOWNWARDS_FLAG_NAME_MAPPING[node.find("ClassName").text]
                break

    if not flag_converted_successfully:
        print("Found a flag that is not attached to any notehead and thus could not be converted. "
              "Skipping object (will not be included in the output). Id {0}".format(flag.uid))
        return None
    return node


def remove_xml_namespace_before_id_attribute(node):
    uid = node.attrib["{http://www.w3.org/XML/1998/namespace}id"]
    node.attrib.pop("{http://www.w3.org/XML/1998/namespace}id")
    node.attrib["id"] = uid
    return node


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
