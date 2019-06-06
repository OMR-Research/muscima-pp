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
                      "staccato-dot": "articulationStaccato",
                      "tenuto": "articulationTenuto",
                      "accent": "articulationAccent",
                      "strong_accent": "articulationMarcato",
                      "thin_barline": "barline",
                      "thick_barline": "barlineHeavy",
                      "dotted_barline": "barlineDotted",
                      "tuple_bracket/line": "tupleBracket",
                      "repeat_measure": "repeat1Bar",
                      "numeral_0": "numeral0",
                      "numeral_1": "numeral1",
                      "numeral_2": "numeral2",
                      "numeral_3": "numeral3",
                      "numeral_4": "numeral4",
                      "numeral_5": "numeral5",
                      "numeral_6": "numeral6",
                      "numeral_7": "numeral7",
                      "numeral_8": "numeral8",
                      "numeral_9": "numeral9",
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

DYNAMICS_LETTER_NAME_MAPPING = {"letter_p": "dynamicLetterP",
                                "letter_m": "dynamicLetterM",
                                "letter_f": "dynamicLetterF",
                                "letter_s": "dynamicLetterS",
                                "letter_z": "dynamicLetterZ",
                                }


def upgrade_xml_file(element_tree: ElementTree, crop_objects: List[CropObject]) -> ElementTree:
    nodes = Element("Nodes", attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                     "xsi:noNamespaceSchemaLocation": "CVC-MUSCIMA_Schema.xsd"})

    id_to_cropobject_mapping = {o.objid: o for o in crop_objects}  # type: Dict[int, CropObject]

    crop_object_nodes = element_tree.findall("*/CropObject")
    for crop_object_node in crop_object_nodes:
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

        if crop_object.clsname == "fermata":
            node = split_fermata_into_fermataAbove_or_fermataBelow(node, crop_object, crop_objects)

        if "_flag" in crop_object.clsname:
            node = split_flag_into_flagUp_or_flagDown(node, crop_object, crop_objects)

        if "letter_" in crop_object.clsname:
            new_node = introduce_dymanic_letter_x(node, crop_object, crop_objects, crop_object_nodes)
            if new_node is not None:
                nodes.append(new_node)

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
    for incoming_object in flag.get_inlink_objects(crop_objects):  # type: CropObject
        if "notehead" in incoming_object.clsname:
            center_of_notehead = incoming_object.top + (incoming_object.bottom - incoming_object.top) / 2.0
            flag_converted_successfully = True
            if center_of_flag < center_of_notehead:
                node.find("ClassName").text = UPWARDS_FLAG_NAME_MAPPING[node.find("ClassName").text]
                break
            else:
                node.find("ClassName").text = DOWNWARDS_FLAG_NAME_MAPPING[node.find("ClassName").text]
                break

    if not flag_converted_successfully:
        print("Found a flag that is not attached to any notehead and thus could not be converted. "
              "Skipping object {0} (will not be included in the output).".format(flag.uid))
        return None
    return node


def split_fermata_into_fermataAbove_or_fermataBelow(node: Element, fermata: CropObject,
                                                    crop_objects: List[CropObject]) -> Union[None, Element]:
    center_of_fermata = fermata.top + (fermata.bottom - fermata.top) / 2.0

    if len(fermata.get_inlink_objects(crop_objects)) == 0:
        print("Found a fermata that is not attached to anything. "
              "Defaulting to fermataAbove. {0} ".format(fermata.uid))
        node.find("ClassName").text = "fermataAbove"

    for incoming_object in fermata.get_inlink_objects(crop_objects):  # type: CropObject
        center_of_incoming_object = incoming_object.top + (incoming_object.bottom - incoming_object.top) / 2.0
        if center_of_fermata < center_of_incoming_object:
            node.find("ClassName").text = "fermataAbove"
            break
        else:
            node.find("ClassName").text = "fermataBelow"
            break
    return node


def introduce_dymanic_letter_x(node: Element, letter: CropObject, crop_objects: List[CropObject],
                               crop_object_nodes: List[Element]) -> Union[None, Element]:
    if letter.clsname not in ["letter_p", "letter_m", "letter_f", "letter_s", "letter_z"]:
        return None

    inlink_objects = letter.get_inlink_objects(crop_objects) # type: List[CropObject]
    letter_has_no_incoming_connection = len(inlink_objects) < 1
    if letter_has_no_incoming_connection:
        return None

    letter_belongs_to_dynamics = inlink_objects[0].clsname == "dynamics_text"
    if not letter_belongs_to_dynamics:
        return None

    new_class_name = DYNAMICS_LETTER_NAME_MAPPING[letter.clsname]
    dynamics_letter = deepcopy(letter)
    new_node = deepcopy(node)  # type: Element
    dynamics_letter.clsname = new_class_name
    new_node.find("ClassName").text = new_class_name

    objids = [c.objid for c in crop_objects]
    new_id = max(objids) + 1
    dynamics_letter.objid = new_id
    new_node.find("Id").text = str(new_id)
    new_node.attrib["id"] = new_node.attrib["id"].replace("___{0}".format(letter.objid), "___{0}".format(new_id))

    inlink_objects[0].outlinks.append(new_id)
    inlink_node = [n for n in crop_object_nodes if n.find("Id").text == str(inlink_objects[0].objid)][0]
    inlink_node.find("Outlinks").text += " {0}".format(new_id)
    crop_objects.append(dynamics_letter)

    return new_node


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
