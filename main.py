#importing libraires
import ezdxf
import json
import numpy as np
import math


#loading the dxf file
doc = ezdxf.readfile('/home/kuntal/Downloads/dwgs/936/936_front_view.dxf')
msp  =  doc.modelspace()
lines = msp.query("LINE")
polylines = msp.query('LWPOLYLINE')
inserts = msp.query('INSERT')
redundant_layers = []  
#redudant layers is empty list as we want load all layers in the data  otherwise we can add the layer we want to ignore


dxf_structure ={}
def process_lines( lines, insert_handle=None, adjust_vector=None):
    '''
    function for process lines where input as modelspace lines from the dxf file
    and output a dictionary

    '''
    for line in lines:
        # read all the dxf attributes
        info = line.dxf.all_existing_dxf_attribs()
        layer_type = info["layer"]

        if layer_type not in redundant_layers: 
            start_points = tuple(info["start"].xy)
            end_points = tuple(info["end"].xy)

            if adjust_vector:
                start_points = (start_points[0] + adjust_vector.x, start_points[1] + adjust_vector.y, 0.0)
                end_points = (end_points[0] + adjust_vector.x, end_points[1] + adjust_vector.y, 0.0)

            handle = insert_handle + info["handle"] if insert_handle else info["handle"]
            data = {"start": start_points, "end": end_points, "meta": layer_type}
            dxf_structure[handle] = data


def process_polylines( msp, polylines):
    '''
    function for process polylines where input as modelspace polylines from the dxf file
    and output a dictionary
     
    '''
    polylines_handles = [poly.dxf.handle for poly in polylines]
    for handle in polylines_handles:
        split_lines = split_polyline(handle, msp)
        if split_lines:
            for idx, line in enumerate(split_lines):
                dxf_structure[handle + 'p' + str(idx)] = line


def split_polyline( handle, msp):
    '''
    function for split polylines where input as modelspace handles of polylines  from the dxf file
    and modelspace  of the dxf file
    output splitted lines of the polylines
     
    '''
    poly_entity = msp.query(f"LWPOLYLINE[handle=='{handle}']").first
    layer_type = poly_entity.dxf.layer
    if layer_type not in redundant_layers:
        output_list = np.array(poly_entity.get_points())[:, :3].tolist()

        edges_list = []
        for idx in range(len(output_list) - 1):
            start = tuple(output_list[idx])
            end = tuple(output_list[idx + 1])

            if round(start[0], 1) != round(end[0], 1) or round(start[1], 1) != round(end[1], 1):
                edges_list.append({'start': start, 'end': end, 'meta': layer_type})
        return edges_list

    return []



process_polylines(msp,polylines)
process_lines(lines)
print(dxf_structure)

with open('dxf_file.json','w') as f:
    json.dump(dxf_structure,f,indent=2)