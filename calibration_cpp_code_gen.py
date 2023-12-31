from datetime import datetime

#template example
"""

#define CW_STATE_MAP {\
1,\
2,\
3,\
4 }

#define CCW_STATE_MAP {\
10,\
9,\
8,\
7 }

const uint32_t STATE_MAP[2][16384] = {
    CW_STATE_MAP,
    CCW_STATE_MAP,
};
"""

# template strings 

sub_map_value_join_str = ",\\\n"

sub_map_define_template = """#define %s {\
%s }"""

state_map_template = """const uint32_t STATE_MAP[2][16384] = {
    %s,
    %s,
};"""

final_code_template = """/* Auto-generated by calibration_cpp_code_gen on (%s)[DD/MM/YYYY] with identifier (%s) for combined datasets:
%s
 */

// CW State Map values over 16384 angular steps
%s

// CCW State Map values over 16384 angular steps
%s

// Combined state map CW and CCW over 16384 angular steps
%s"""

# cpp generator function
def create_cpp_state_map(combination_id, folders_descriptions, cw_template_title, cw_state_map, ccw_template_title, ccw_state_map):
    now = datetime.now().strftime("%d/%m/%y")
    cw_state_map_cpp = sub_map_define_template % (cw_template_title, sub_map_value_join_str.join(map(lambda x: str(x), cw_state_map)))
    ccw_state_map_cpp = sub_map_define_template % (ccw_template_title, sub_map_value_join_str.join(map(lambda x: str(x), ccw_state_map)))
    final_state_map_cpp = state_map_template % (cw_template_title, ccw_template_title)
    return final_code_template % (
        now,
        combination_id,
        folders_descriptions,
        cw_state_map_cpp,
        ccw_state_map_cpp,
        final_state_map_cpp
    )

import analyse
def state_map_to_state_array(state_map: analyse.State_Map):
    #angles[angle_to_save_state_str] = c_state
    output = []
    for angle_int in range(16384):
        angle_str = str(angle_int)
        c_state = state_map[angle_str]
        output.append(c_state)
    return output

        

#print(create_cpp_state_map("CW_STATE_MAP",[0,1,2,3,4,5,6,7], "CCW_STATE_MAP", [7,6,5,4,3,2,1]))
#print(sub_map_define_template % (sub_map_value_join_str.join(map(lambda x: str(x), py_cw_state_map_example))))
