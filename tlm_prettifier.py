import xml.etree.ElementTree as ET
import xml.dom.minidom

def prettify_tlm(tlm_file, output_xml=None):
    """Make .tlm file human-readable"""
    
    # Read the .tlm file
    with open(tlm_file, 'r', encoding='ISO-8859-1') as f:
        content = f.read()
    
    # Parse XML (even though it's .tlm extension)
    try:
        # Parse with ElementTree
        root = ET.fromstring(content)
        
        # Convert to string with proper indentation
        rough_string = ET.tostring(root, encoding='ISO-8859-1')
        parsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = parsed.toprettyxml(indent="  ", encoding='ISO-8859-1')
        
        # Decode from bytes
        pretty_xml_str = pretty_xml.decode('ISO-8859-1')
        
        # Remove empty lines that minidom adds
        lines = [line for line in pretty_xml_str.split('\n') if line.strip()]
        pretty_xml_str = '\n'.join(lines)
        
        # Determine output filename
        if output_xml is None:
            output_xml = tlm_file.replace('.tlm', '_pretty.xml')
        
        # Write prettified version
        with open(output_xml, 'w', encoding='ISO-8859-1') as f:
            f.write(pretty_xml_str)
        
        print(f"Prettified: {tlm_file}")
        print(f"Saved to: {output_xml}")
        
        return output_xml
        
    except Exception as e:
        print(f"❌ Error prettifying: {e}")
        return None

# Usage
prettify_tlm("ToolKit_Haas_Lathe_251007.tlm")