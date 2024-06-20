import xml.etree.ElementTree as ET
import re
import sys
from xml.dom import minidom

def parse_text_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    instruments = []
    current_instrument = None

    for line in lines:
        line = line.strip()
        if line.startswith("InstrumentName="):
            if current_instrument is not None:
                instruments.append(current_instrument)
            instrument_name = line.split("=")[1]
            instrument_number = int(re.search(r"\d+", instrument_name).group())
            current_instrument = {
                "Name": instrument_name,
                "ProgramNo": instrument_number,
                "Samples": [],
            }
        elif line.startswith("Sample="):
            sample = {"Sample": line.split("=")[1]}
            current_instrument["Samples"].append(sample)
        elif (
            "=" in line
            and current_instrument is not None
            and "Samples" in current_instrument
        ):
            key, value = line.split("=", 1)
            current_instrument["Samples"][-1][key] = value

    if current_instrument is not None:
        instruments.append(current_instrument)

    return instruments

def create_xml_from_data(instruments):
    root = ET.Element("Bank", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        "Version": "1.0.0.0",
        "Platform": "Ctr",
        "xmlns": "NintendoWare.SoundFoundation.FileFormats.NintendoWare"
    })

    head = ET.SubElement(root, "Head")
    ET.SubElement(head, "Title").text = "TestBank"

    body = ET.SubElement(root, "Body")
    bank = ET.SubElement(body, "Bank")
    items = ET.SubElement(bank, "Items")

    for instrument in instruments:
        instrument_element = ET.SubElement(items, "Instrument", Name=instrument["Name"])
        parameters = ET.SubElement(instrument_element, "Parameters")

        for param in [
            "Comment",
            "Comment1",
            "Comment2",
            "Comment3",
            "Comment4",
            "Comment5",
            "Comment6",
            "Comment7",
            "Comment8",
            "Comment9",
        ]:
            ET.SubElement(parameters, param)

        ET.SubElement(parameters, "ColorIndex").text = "0"
        ET.SubElement(parameters, "IsEnabled").text = "True"
        ET.SubElement(parameters, "ProgramNo").text = str(instrument["ProgramNo"])
        ET.SubElement(parameters, "Volume").text = "127"
        ET.SubElement(parameters, "PitchSemitones").text = "0"
        ET.SubElement(parameters, "PitchCents").text = "0"

        if instrument["Samples"]:
            first_sample = instrument["Samples"][0]
            envelope = ET.SubElement(parameters, "Envelope")
            envelope_params = ET.SubElement(envelope, "Parameters")
            ET.SubElement(envelope_params, "Attack").text = first_sample[
                "Z_attackVolEnv"
            ]
            ET.SubElement(envelope_params, "Decay").text = first_sample["Z_decayVolEnv"]
            ET.SubElement(envelope_params, "Sustain").text = first_sample[
                "Z_sustainVolEnv"
            ]
            ET.SubElement(envelope_params, "Hold").text = first_sample["Z_holdVolEnv"]
            ET.SubElement(envelope_params, "Release").text = first_sample[
                "Z_releaseVolEnv"
            ]
        else:
            # Default values if no samples are available
            envelope = ET.SubElement(parameters, "Envelope")
            envelope_params = ET.SubElement(envelope, "Parameters")
            ET.SubElement(envelope_params, "Attack").text = "127"
            ET.SubElement(envelope_params, "Decay").text = "127"
            ET.SubElement(envelope_params, "Sustain").text = "127"
            ET.SubElement(envelope_params, "Hold").text = "0"
            ET.SubElement(envelope_params, "Release").text = "127"

        ET.SubElement(parameters, "InstrumentEnvelopeMode").text = "Instrument"

        for sample in instrument["Samples"]:
            items2_element = ET.SubElement(instrument_element, "Items")
            key_region_element = ET.SubElement(items2_element, "KeyRegion")
            key_params = ET.SubElement(key_region_element, "Parameters")

            for param in [
                "Comment",
                "Comment1",
                "Comment2",
                "Comment3",
                "Comment4",
                "Comment5",
                "Comment6",
                "Comment7",
                "Comment8",
                "Comment9",
            ]:
                ET.SubElement(key_params, param)

            ET.SubElement(key_params, "ColorIndex").text = "0"
            ET.SubElement(key_params, "IsEnabled").text = "True"
            ET.SubElement(key_params, "KeyMin").text = sample["Z_LowKey"]
            ET.SubElement(key_params, "KeyMax").text = sample["Z_HighKey"]

            key_items = ET.SubElement(key_region_element, "Items")

            velocity_region_element = ET.SubElement(key_items, "VelocityRegion")
            vel_params = ET.SubElement(velocity_region_element, "Parameters")

            for param in [
                "Comment",
                "Comment1",
                "Comment2",
                "Comment3",
                "Comment4",
                "Comment5",
                "Comment6",
                "Comment7",
                "Comment8",
                "Comment9",
            ]:
                ET.SubElement(vel_params, param)

            ET.SubElement(vel_params, "ColorIndex").text = "0"
            ET.SubElement(vel_params, "IsEnabled").text = "True"
            ET.SubElement(vel_params, "FilePath").text = sample["Sample"]
            ET.SubElement(vel_params, "WaveEncoding").text = "Adpcm"
            ET.SubElement(vel_params, "OriginalKey").text = sample[
                "Z_overridingRootKey"
            ]

            envelope = ET.SubElement(vel_params, "Envelope")
            envelope_params = ET.SubElement(envelope, "Parameters")
            ET.SubElement(envelope_params, "Attack").text = sample["Z_attackVolEnv"]
            ET.SubElement(envelope_params, "Decay").text = sample["Z_decayVolEnv"]
            ET.SubElement(envelope_params, "Sustain").text = sample["Z_sustainVolEnv"]
            ET.SubElement(envelope_params, "Hold").text = sample["Z_holdVolEnv"]
            ET.SubElement(envelope_params, "Release").text = sample["Z_releaseVolEnv"]

            ET.SubElement(vel_params, "VelocityMin").text = sample["Z_LowVelocity"]
            ET.SubElement(vel_params, "VelocityMax").text = sample["Z_HighVelocity"]
            ET.SubElement(vel_params, "Volume").text = "127"
            ET.SubElement(vel_params, "Pan").text = sample["Z_pan"]
            ET.SubElement(vel_params, "PitchSemitones").text = "0"
            ET.SubElement(vel_params, "PitchCents").text = "0"
            ET.SubElement(vel_params, "KeyGroup").text = "0"
            ET.SubElement(vel_params, "InterpolationType").text = "Polyphase"
            ET.SubElement(vel_params, "InstrumentNoteOffMode").text = "Release"

    return ET.tostring(root, encoding="unicode")


def prettify_xml(xml_str):
    """Return a pretty-printed XML string."""
    parsed = minidom.parseString(xml_str)
    return parsed.toprettyxml(indent="  ")


# Main function to parse the file and generate the XML
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert.py <bank_file_name_extracted_from_Wii3DSUSoundTool.txt>")
        sys.exit(1)

    file_path = sys.argv[1]
    instruments = parse_text_file(file_path)
    xml_output = create_xml_from_data(instruments)
    pretty_xml_output = prettify_xml(xml_output)

    # Save the pretty XML to a file
    output_file_path = file_path.replace(".txt", "_output.cbnk")
    with open(output_file_path, "w") as file:
        file.write(pretty_xml_output)
