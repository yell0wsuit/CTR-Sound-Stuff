import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom


def parse_text_file(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    instruments = []
    current_instrument = None
    current_note_region = None

    for line in lines:
        line = line.strip()
        if line.startswith("Instrument"):
            if current_instrument:
                if current_note_region:
                    current_instrument["notes"].append(current_note_region)
                    current_note_region = None
                instruments.append(current_instrument)
            current_instrument = {
                "name": line.split(" ")[1],
                "program_no": "",
                "note_count": 0,
                "notes": [],
            }
        elif line.startswith("Program Number:"):
            current_instrument["program_no"] = line.split(": ")[1]
        elif line.startswith("Note Count:"):
            try:
                note_count = int(line.split(": ")[1])
                if note_count < 0 or note_count > 128:
                    continue
                current_instrument["note_count"] = note_count
            except ValueError:
                continue
        elif line.startswith("Sample:"):
            if current_note_region:
                current_instrument["notes"].append(current_note_region)
            current_note_region = {
                "sample": line.split(": ")[1],
                "key_min": "",
                "key_max": "",
                "original_key": "",
                "volume": "",
                "pan": "",
                "attack": "",
                "hold": "",
                "decay": "",
                "sustain": "",
                "release": "",
            }
        elif line.startswith("Start Note:"):
            current_note_region["key_min"] = line.split(": ")[1]
        elif line.startswith("End Note:"):
            current_note_region["key_max"] = line.split(": ")[1]
        elif line.startswith("Base Note:"):
            current_note_region["original_key"] = line.split(": ")[1]
        elif line.startswith("Volume:"):
            current_note_region["volume"] = line.split(": ")[1]
        elif line.startswith("Pan:"):
            current_note_region["pan"] = line.split(": ")[1]
        elif line.startswith("Attack:"):
            current_note_region["attack"] = line.split(": ")[1]
        elif line.startswith("Hold:"):
            current_note_region["hold"] = line.split(": ")[1]
        elif line.startswith("Decay:"):
            current_note_region["decay"] = line.split(": ")[1]
        elif line.startswith("Sustain:"):
            current_note_region["sustain"] = line.split(": ")[1]
        elif line.startswith("Release:"):
            current_note_region["release"] = line.split(": ")[1]

    if current_note_region:
        current_instrument["notes"].append(current_note_region)
    if current_instrument:
        instruments.append(current_instrument)

    return instruments


def build_xml(instruments):
    root = ET.Element(
        "Bank",
        {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
            "xmlns": "NintendoWare.SoundFoundation.FileFormats.NintendoWare",
            "Version": "1.0.0.0",
            "Platform": "Ctr",
        },
    )

    head = ET.SubElement(root, "Head")
    title = ET.SubElement(head, "Title")
    title.text = "TestBank"

    body = ET.SubElement(root, "Body")
    bank = ET.SubElement(body, "Bank")
    items = ET.SubElement(bank, "Items")

    for instrument in instruments:
        if instrument["note_count"] == 0 or instrument["note_count"] == 856392688:
            continue  # Skip invalid instruments

        instrument_elem = ET.SubElement(
            items, "Instrument", {"Name": f"Instrument{instrument['name']}"}
        )
        parameters = ET.SubElement(instrument_elem, "Parameters")

        for i in range(10):
            ET.SubElement(parameters, f"Comment{i}")
        ET.SubElement(parameters, "ColorIndex").text = "0"
        ET.SubElement(parameters, "IsEnabled").text = "True"
        ET.SubElement(parameters, "ProgramNo").text = instrument["program_no"]
        ET.SubElement(parameters, "Volume").text = "127"
        ET.SubElement(parameters, "PitchSemitones").text = "0"
        ET.SubElement(parameters, "PitchCents").text = "0"

        envelope = ET.SubElement(parameters, "Envelope")
        env_parameters = ET.SubElement(envelope, "Parameters")

        if instrument["notes"]:
            ET.SubElement(env_parameters, "Attack").text = instrument["notes"][0][
                "attack"
            ]
            ET.SubElement(env_parameters, "Decay").text = instrument["notes"][0][
                "decay"
            ]
            ET.SubElement(env_parameters, "Sustain").text = instrument["notes"][0][
                "sustain"
            ]
            ET.SubElement(env_parameters, "Hold").text = instrument["notes"][0]["hold"]
            ET.SubElement(env_parameters, "Release").text = instrument["notes"][0][
                "release"
            ]

        ET.SubElement(parameters, "InstrumentEnvelopeMode").text = "Instrument"

        for note in instrument["notes"]:
            key_region = ET.SubElement(instrument_elem, "Items")
            key_region_elem = ET.SubElement(key_region, "KeyRegion")
            key_parameters = ET.SubElement(key_region_elem, "Parameters")

            for i in range(10):
                ET.SubElement(key_parameters, f"Comment{i}")
            ET.SubElement(key_parameters, "ColorIndex").text = "0"
            ET.SubElement(key_parameters, "IsEnabled").text = "True"
            ET.SubElement(key_parameters, "KeyMin").text = note["key_min"]
            ET.SubElement(key_parameters, "KeyMax").text = note["key_max"]

            velocity_region = ET.SubElement(key_region_elem, "Items")
            velocity_region_elem = ET.SubElement(velocity_region, "VelocityRegion")
            velocity_parameters = ET.SubElement(velocity_region_elem, "Parameters")

            for i in range(10):
                ET.SubElement(velocity_parameters, f"Comment{i}")
            ET.SubElement(velocity_parameters, "ColorIndex").text = "0"
            ET.SubElement(velocity_parameters, "IsEnabled").text = "True"
            ET.SubElement(velocity_parameters, "FilePath").text = (
                f"{note['sample']}.wav"
            )
            ET.SubElement(velocity_parameters, "WaveEncoding").text = "Adpcm"
            ET.SubElement(velocity_parameters, "OriginalKey").text = note[
                "original_key"
            ]

            vel_envelope = ET.SubElement(velocity_parameters, "Envelope")
            vel_env_parameters = ET.SubElement(vel_envelope, "Parameters")

            ET.SubElement(vel_env_parameters, "Attack").text = note["attack"]
            ET.SubElement(vel_env_parameters, "Decay").text = note["decay"]
            ET.SubElement(vel_env_parameters, "Sustain").text = note["sustain"]
            ET.SubElement(vel_env_parameters, "Hold").text = note["hold"]
            ET.SubElement(vel_env_parameters, "Release").text = note["release"]

            ET.SubElement(velocity_parameters, "VelocityMin").text = "0"
            ET.SubElement(velocity_parameters, "VelocityMax").text = "127"
            ET.SubElement(velocity_parameters, "Volume").text = note["volume"]
            ET.SubElement(velocity_parameters, "Pan").text = note["pan"]
            ET.SubElement(velocity_parameters, "PitchSemitones").text = "0"
            ET.SubElement(velocity_parameters, "PitchCents").text = "0"
            ET.SubElement(velocity_parameters, "KeyGroup").text = "0"
            ET.SubElement(velocity_parameters, "InterpolationType").text = "Polyphase"
            ET.SubElement(velocity_parameters, "InstrumentNoteOffMode").text = "Release"

    tree = ET.ElementTree(root)
    return tree


def prettify_xml(tree):
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(tree.getroot(), "utf-8")
    parsed = minidom.parseString(rough_string)
    return parsed.toprettyxml(indent="  ")


def write_xml(xml_str, filename):
    with open(filename, "w") as file:
        file.write(xml_str)


# Main function to parse the file and generate the XML
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert.py <bank_file_name_extracted_from_caesar.txt>")
        sys.exit(1)

    file_path = sys.argv[1]
    instruments = parse_text_file(file_path)
    tree = build_xml(instruments)
    pretty_xml_output = prettify_xml(tree)

    # Save the pretty XML to a file
    output_file_path = file_path.replace(".txt", "_output.cbnk")
    write_xml(pretty_xml_output, output_file_path)
