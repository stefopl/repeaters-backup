import xml.etree.ElementTree as ET
import json
from collections import defaultdict

def xml_to_dict(element):
    result = {}

    for child in element:
        if 'type' in child.attrib:
            child_key = child.tag
            type_value = child.attrib['type']

            if child_key not in result:
                result[child_key] = {}

            result[child_key][type_value] = child.text
        else:
            child_dict = xml_to_dict(child)

            if not child_dict:
                child_dict = child.text

            if child.tag not in result:
                result[child.tag] = child_dict
            else:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = [result[child.tag], child_dict]

    return result

def xml_file_to_json(xml_file_path, json_output_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    qra_count = defaultdict(int)
    repeaters_data = {}

    repeaters_section = root.find('.//repeaters')

    for repeater in repeaters_section.findall('.//repeater'):
        repeater_data = xml_to_dict(repeater)
        qra = repeater.find('qra').text

        qra_count[qra] += 1
        key = qra

        if qra_count[qra] > 1:
            key = f"{qra}_{qra_count[qra]}"

        repeaters_data[key] = repeater_data

    data_dict = xml_to_dict(root)

    if 'repeaters' in data_dict:
        data_dict['repeaters'] = repeaters_data
    else:
        print("Error: 'rxf' or 'repeaters' not found in XML structure.")
        return

    with open(json_output_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

    print(f"XML data from {xml_file_path} saved to {json_output_path}")

xml_file_to_json('backup/przemienniki-net/Native_XML_Format/rxf.xml', 'data/przemienniki_net.json')
