import xml.etree.ElementTree as ET
import csv
import uuid

def convert_to_exact_inventor_format(tlm_file, output_tsv):
    """Convert to EXACT Inventor CAM TSV format"""
    
    tree = ET.parse(tlm_file)
    root = tree.getroot()
    
    with open(output_tsv, 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        
        # Write version header
        writer.writerow(['version'])
        writer.writerow(['14'])
        
        # Write ALL column headers (in EXACT order from your file)
        headers = [
            'type', 'unit', 'description', 'comment', 'manufacturer', 
            'product-id', 'product-link', 'number', 'turret', 'diameter-offset',
            'length-offset', 'live-tool', 'break-control', 'manual-tool-change',
            'diameter', 'tip-diameter', 'tip-length', 'corner-radius', 
            'taper-angle', 'taper-angle2', 'flute-length', 'shoulder-length',
            'shaft-diameter', 'body-length', 'overall-length', 'number-of-flutes',
            'thread-pitch', 'coolant-support', 'coolant-mode', 'material-name',
            'spindle-rpm', 'ramp-spindle-rpm', 'clockwise', 'cutting-feedrate',
            'entry-feedrate', 'exit-feedrate', 'plunge-feedrate', 'ramp-feedrate',
            'retract-feedrate', 'holder', 'shaft', 'guid', 'holder-description',
            'holder-comment', 'holder-vendor', 'holder-product-id', 'holder-guid',
            'holder-library-name'
        ]
        writer.writerow(headers)
        
        # Map SOLIDWORKS tool types to Inventor tool types
        type_map = {
            '20': 'face mill',          # Face mill
            '2': 'flat end mill',       # End mill
            '0': 'drill',               # Drill
            '18': 'center drill',       # Center drill
            '12': 'tap',                # Tap
            '10': 'chamfer mill',       # Chamfer mill
            '15': 'ball end mill'       # Ball nose
        }
        
        for tool in root.findall('.//CompTool[@Type="0"]'):
            tool_number = tool.get('ToolNumber', '1')
            
            # Find tool definition
            tool_def = tool.find('.//CompTool[@Type="1"]')
            if tool_def is None:
                continue
                
            tool_name = tool_def.get('Name', 'Tool')
            tool_type_code = tool_def.get('ToolType', '2')
            
            # Get Inventor tool type
            inventor_type = type_map.get(tool_type_code, 'flat end mill')
            
            # Extract geometry
            diameter = '0'
            corner_radius = '0'
            flute_length = '0'
            shoulder_length = '0'
            shaft_diameter = '0'
            body_length = '0'
            overall_length = '0'
            num_flutes = '2'
            tip_length = '0'
            tip_diameter = '0'
            
            shape = tool_def.find('.//Shape')
            if shape is not None:
                # Get dimensions
                len_params = shape.find('.//LenParams')
                if len_params is not None:
                    # Diameter
                    d_elem = len_params.find('D')
                    if d_elem is not None:
                        diameter = d_elem.get('Val', '0')
                        shaft_diameter = diameter  # For mills, shaft = diameter
                    
                    # Radius/Corner radius
                    r_elem = len_params.find('R')
                    if r_elem is not None:
                        corner_radius = r_elem.get('Val', '0')
                    
                    # Cutting/Flute length (CL)
                    cl_elem = len_params.find('CL')
                    if cl_elem is not None:
                        flute_length = cl_elem.get('Val', '0')
                    
                    # Shoulder length (SL)
                    sl_elem = len_params.find('SL')
                    if sl_elem is not None:
                        shoulder_length = sl_elem.get('Val', '0')
                    
                    # Overall length (TL)
                    tl_elem = len_params.find('TL')
                    if tl_elem is not None:
                        overall_length = tl_elem.get('Val', '0')
                        body_length = str(float(overall_length) * 0.8)  # Estimate
                
                # Number of flutes
                num_flutes = shape.get('NumFlutes', '2')
                
                # Tip dimensions for drills
                if tool_type_code in ['0', '18']:  # Drill or center drill
                    tip_l_elem = len_params.find('TipL')
                    if tip_l_elem is not None:
                        tip_length = tip_l_elem.get('Val', '0')
                    tip_diameter = '0'  # For drills
            
            # Extract cutting conditions
            spindle_rpm = '3500'
            ramp_spindle_rpm = '3500'
            cutting_feedrate = '1000'
            entry_feedrate = '100'
            exit_feedrate = '100'
            plunge_feedrate = '300'
            
            cc_list = tool_def.find('.//CuttingConditionsList')
            if cc_list is not None:
                cc = cc_list.find('.//CC')
                if cc is not None:
                    milling = cc.find('.//MillingFeedSpin')
                    if milling is not None:
                        feeds = milling.find('.//Feeds')
                        spins = milling.find('.//Spins')
                        
                        if feeds is not None:
                            cutting_feedrate = feeds.get('Normal', '1000')
                            entry_feedrate = feeds.get('LeadIn', '100')
                            exit_feedrate = feeds.get('LeadOut', '100')
                            plunge_feedrate = feeds.get('Z', '300')
                        
                        if spins is not None:
                            spindle_rpm = spins.get('Rate', '3500')
                            ramp_spindle_rpm = spindle_rpm
            
            # Generate unique GUID for tool
            tool_guid = '{' + str(uuid.uuid4()).upper() + '}'
            
            # Write tool data row (ALL 48 columns in order)
            writer.writerow([
                inventor_type,                     # type
                'millimeters',                     # unit
                tool_name,                         # description
                f'Converted from SOLIDWORKS T{tool_number}',  # comment
                'SOLIDWORKS',                      # manufacturer
                f'SW-{tool_number}',               # product-id
                '',                                # product-link
                tool_number,                       # number
                '0',                               # turret (0 for milling)
                '1',                               # diameter-offset
                '1',                               # length-offset
                'no',                              # live-tool
                'no',                              # break-control
                'no',                              # manual-tool-change
                diameter,                          # diameter
                tip_diameter,                      # tip-diameter
                tip_length,                        # tip-length
                corner_radius,                     # corner-radius
                '0',                               # taper-angle
                '0',                               # taper-angle2
                flute_length,                      # flute-length
                shoulder_length,                   # shoulder-length
                shaft_diameter,                    # shaft-diameter
                body_length,                       # body-length
                overall_length,                    # overall-length
                num_flutes,                        # number-of-flutes
                '0',                               # thread-pitch (except taps)
                'no',                              # coolant-support
                'flood',                           # coolant-mode
                'hss',                             # material-name
                spindle_rpm,                       # spindle-rpm
                ramp_spindle_rpm,                  # ramp-spindle-rpm
                'yes',                             # clockwise
                cutting_feedrate,                  # cutting-feedrate
                entry_feedrate,                    # entry-feedrate
                exit_feedrate,                     # exit-feedrate
                plunge_feedrate,                   # plunge-feedrate
                cutting_feedrate,                  # ramp-feedrate (same as cutting)
                '0',                               # retract-feedrate
                '',                                # holder (optional)
                '',                                # shaft (optional)
                tool_guid,                         # guid
                '',                                # holder-description
                '',                                # holder-comment
                '',                                # holder-vendor
                '',                                # holder-product-id
                '',                                # holder-guid
                ''                                 # holder-library-name
            ])
    
    print(f"Saved to: {output_tsv}")
    print(f"Note that this particular file has the version header and all 48 columns")

# Run conversion
convert_to_exact_inventor_format(
    "ToolKit_Haas_MiniMill_251007.tlm",
    "Inventor_mill.tsv"
)