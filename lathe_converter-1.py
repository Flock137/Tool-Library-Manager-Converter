import xml.etree.ElementTree as ET
import csv
import uuid

def convert_lathe_tlm_to_inventor_format(tlm_file, output_tsv):
    """Convert SOLIDWORKS lathe .tlm to Inventor lathe tool format"""
    
    tree = ET.parse(tlm_file)
    root = tree.getroot()
    
    with open(output_tsv, 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        
        # Version header
        writer.writerow(['version'])
        writer.writerow(['14'])
        
        # Lathe tool headers (from your example)
        headers = [
            'type', 'unit', 'description', 'comment', 'manufacturer',
            'product-id', 'product-link', 'number', 'turret', 'compensation-offset',
            'break-control', 'manual-tool-change', 'diameter', 'tip-diameter',
            'tip-length', 'corner-radius', 'taper-angle', 'taper-angle2',
            'flute-length', 'shoulder-length', 'shaft-diameter', 'body-length',
            'overall-length', 'number-of-flutes', 'thread-pitch', 'coolant-support',
            'coolant-mode', 'material-name', 'spindle-rpm', 'ramp-spindle-rpm',
            'clockwise', 'cutting-feedrate', 'entry-feedrate', 'exit-feedrate',
            'plunge-feedrate', 'ramp-feedrate', 'retract-feedrate', 'holder',
            'shaft', 'guid', 'holder-description', 'holder-comment', 'holder-vendor',
            'holder-product-id', 'holder-guid', 'holder-library-name'
        ]
        writer.writerow(headers)
        
        # Map SOLIDWORKS lathe tool types to Inventor types
        lathe_type_map = {
            '16': 'turning general',      # Profile turning
            '18': 'turning threading',    # Threading
            '17': 'turning grooving',     # Grooving
            '19': 'turning parting',      # Parting (similar to grooving)
            '20': 'turning boring'        # Boring
        }
        
        for tool in root.findall('.//CompTool[@Type="0"]'):
            tool_number = tool.get('ToolNumber', '1')
            
            # Find turning tool (Type="5")
            turning_tool = tool.find('.//CompTool[@Type="5"]')
            if turning_tool is None:
                continue
                
            tool_name = turning_tool.get('Name', 'Lathe Tool')
            
            # Find insert definition (Type="1")
            insert_def = turning_tool.find('.//CompTool[@Type="1"]')
            if insert_def is None:
                continue
                
            insert_name = insert_def.get('Name', 'Insert')
            tool_type_code = insert_def.get('ToolType', '16')
            
            # Get Inventor lathe tool type
            inventor_type = lathe_type_map.get(tool_type_code, 'turning general')
            
            # Extract insert geometry
            shape = insert_def.find('.//Shape')
            
            # For lathe tools, key parameters are different
            corner_radius = '0'  # Nose radius
            insert_size = '0'    # Insert cutting edge length
            insert_thickness = '0'
            nose_angle = '0'
            
            if shape is not None:
                corner_radius = shape.get('InsertCornerRadius', '0')
                insert_size = shape.get('InsertCuttingEdgeLength', '0')
                insert_thickness = shape.get('InsertThickness', '0')
                nose_angle = shape.get('InsertNoseAngle', '0')
            
            # Extract tool holder geometry (from the Type="5" CompTool's Shape)
            tool_shape = turning_tool.find('.//Shape')
            shank_height = '25'  # Default
            shank_width = '25'
            tool_length = '150'
            approach_angle = '95'  # Default
            
            if tool_shape is not None:
                shank_height = tool_shape.get('ShankHeight', '25')
                shank_width = tool_shape.get('ShankWidth', '25')
                tool_length = tool_shape.get('ToolLength', '150')
                approach_angle_gui = tool_shape.get('ApproachAngleGUI', '95')
                approach_angle = approach_angle_gui
            
            # Extract cutting conditions (TURNING specific)
            cutting_feedrate = '0.1'  # mm/rev for turning
            spindle_rpm = '1000'
            
            cc = insert_def.find('.//CC')
            if cc is not None:
                turning = cc.find('.//TurningFeedSpin')
                if turning is not None:
                    feeds = turning.find('.//Feeds')
                    spins = turning.find('.//Spins')
                    
                    if feeds is not None:
                        cutting_feedrate = feeds.get('Normal', '0.1')
                    
                    if spins is not None:
                        spindle_rpm = spins.get('Normal', '1000')
            
            # Generate unique GUID
            tool_guid = '{' + str(uuid.uuid4()).upper() + '}'
            
            # Special handling for different lathe tool types
            thread_pitch = '0'
            if tool_type_code == '18':  # Threading tool
                thread_pitch = '1'  # Default, should extract from XML if available
            
            # Write lathe tool data
            writer.writerow([
                inventor_type,                     # type
                'millimeters',                     # unit
                f"{tool_name} - {insert_name}",    # description
                f'Converted from SOLIDWORKS T{tool_number}',  # comment
                'SOLIDWORKS',                      # manufacturer
                f'SW-LATHE-{tool_number}',         # product-id
                '',                                # product-link
                tool_number,                       # number
                tool_number,                       # turret (usually same as tool# for lathes)
                tool_number,                       # compensation-offset (usually same as tool#)
                'no',                              # break-control
                'no',                              # manual-tool-change
                '0',                               # diameter (not used for lathe inserts)
                '0',                               # tip-diameter
                '0',                               # tip-length
                corner_radius,                     # corner-radius (NOSE RADIUS for lathe)
                '0',                               # taper-angle
                '0',                               # taper-angle2
                insert_size,                       # flute-length (insert cutting edge length)
                shank_height,                      # shoulder-length (shank height)
                shank_width,                       # shaft-diameter (shank width)
                tool_length,                       # body-length (tool length)
                str(float(tool_length) + 20),      # overall-length (estimated)
                '1',                               # number-of-flutes (always 1 for lathe inserts)
                thread_pitch,                      # thread-pitch (for threading tools)
                'no',                              # coolant-support
                'flood',                           # coolant-mode
                'carbide',                         # material-name
                spindle_rpm,                       # spindle-rpm
                spindle_rpm,                       # ramp-spindle-rpm
                'yes',                             # clockwise
                cutting_feedrate,                  # cutting-feedrate (mm/rev)
                cutting_feedrate,                  # entry-feedrate
                cutting_feedrate,                  # exit-feedrate
                cutting_feedrate,                  # plunge-feedrate
                cutting_feedrate,                  # ramp-feedrate
                '0',                               # retract-feedrate
                '',                                # holder
                '',                                # shaft
                tool_guid,                         # guid
                '',                                # holder-description
                '',                                # holder-comment
                '',                                # holder-vendor
                '',                                # holder-product-id
                '',                                # holder-guid
                ''                                 # holder-library-name
            ])
    
    print(f"Converted lathe tools to Inventor format")
    print(f"Saved to: {output_tsv}")

# Run conversion for lathe
convert_lathe_tlm_to_inventor_format(
    "ToolKit_Haas_Lathe_251007.tlm",
    "Inventor_lathe.tsv"
)