from scipy.optimize import curve_fit
import numpy as np
import json
import sys
import matplotlib.pyplot as plt
import analyse
import utils
import models
import plots
from collections import OrderedDict

poles = 22
max_iter = 500000



combined_identifier = sys.argv[1] if len(sys.argv) > 1 else 0 # zc_map_id
poles = sys.argv[2] if len(sys.argv) > 2 else 0
poles = int(poles)
print("poles", poles)
run_ids_str = None

with open("./calibration-data/combination-report-%s.id" % (combined_identifier)) as fin:
    run_ids_str = "".join(fin.readlines())

run_ids = run_ids_str.split(",")
print("Analysing runs:", run_ids)

combined_data = utils.combine_merged_smoothed_datasets(run_ids)

# test run_ids
print("combined_data")
print(combined_data)

data_length = {
    "cw": 0,
    "ccw": 0
}

for key in combined_data.keys():
    data_length[key] = len(combined_data[key][0])
    print(key, len(combined_data[key][0]), len(combined_data[key][1]), len(combined_data[key][2]), len(combined_data[key][3]))
    print(max(combined_data[key][0]))
#key: (angles_bin, anvn_bin, bnvn_bin, cnvn_bin)

# 16384 encoder steps 0 -> 16383
# angle compression factor is 8
# rads 0 -> 2pi - ((1/16384) * 2pi)

data_to_fit_cw = combined_data["cw"] #0 angle 1 a 2 b 3 c
data_to_fit_ccw = combined_data["ccw"] #0 angle 1 a 2 b 3 c

#print("data_to_fit_cw[0]", data_to_fit_cw[0])

# now bin the data
binned_angle_abc_data = OrderedDict()
binned_angle_abc_data["cw"] = OrderedDict()
binned_angle_abc_data["ccw"] = OrderedDict()

"""{ # OrderedDict()
    "cw":{

    },
    "ccw": {

    }
}"""

for key in combined_data.keys():
    for angle in range(0, 16383):
        angle_str = str((angle/16384) * 2 * np.pi)
        binned_angle_abc_data[key][angle_str] = {"a":[], "b":[], "c":[]}


duty_max = 2047
angle_compression = 4
binned_voltage_data = OrderedDict()
binned_voltage_data["cw"] = OrderedDict()
binned_voltage_data["ccw"] = OrderedDict()

max_compressed_value = 16384 / angle_compression

for key in combined_data.keys():
    for angle_idx in range(0, 16384):
        angle = angle_idx / angle_compression
        nearest_angle_bin = round(angle)
        if (nearest_angle_bin >= max_compressed_value):
            nearest_angle_bin = 0
        str_nearest_angle_bin = str(nearest_angle_bin)
        #angle_str = str((angle_idx/16384) * 2 * np.pi)
        #binned_angle_abc_data[key][angle_str]# = {"a":[], "b":[], "c":[]}
        binned_voltage_data["cw"][str_nearest_angle_bin] = {"a":[], "b":[], "c":[]}
        binned_voltage_data["ccw"][str_nearest_angle_bin] = {"a":[], "b":[], "c":[]}

#print("binned_voltage_data", binned_voltage_data)

for key in combined_data.keys():
    for i in range (data_length[key]):
        angle = combined_data[key][0][i]
        anvn = combined_data[key][1][i]
        bnvn = combined_data[key][2][i]
        cnvn = combined_data[key][3][i]
        angle_str = str(angle)

        angle_idx = 16384 * (float(angle_str) / (2 * np.pi))
        compressed_angle_idx = round(angle_idx/angle_compression)
        if (compressed_angle_idx >= max_compressed_value):
            compressed_angle_idx = 0
        compressed_angle_str = str(compressed_angle_idx)

        if (angle_str in binned_angle_abc_data[key]):
            if anvn != 0 or anvn != 0.0:
                binned_angle_abc_data[key][angle_str]["a"].append(anvn)
                binned_voltage_data[key][compressed_angle_str]["a"].append(anvn)
            if bnvn != 0 or bnvn != 0.0:
                binned_angle_abc_data[key][angle_str]["b"].append(bnvn)
                binned_voltage_data[key][compressed_angle_str]["b"].append(bnvn)
            if cnvn != 0 or cnvn != 0.0:
                binned_angle_abc_data[key][angle_str]["c"].append(cnvn)
                binned_voltage_data[key][compressed_angle_str]["c"].append(cnvn)

        
        #else:
        #    binned_angle_abc_data[key][angle_str] = OrderedDict() # {"a":[anvn], "b":[bnvn], "c":[cnvn]}
        #    binned_angle_abc_data[key][angle_str]["a"] = [anvn]
        #    binned_angle_abc_data[key][angle_str]["b"] = [bnvn]
        #    binned_angle_abc_data[key][angle_str]["c"] = [cnvn]
        
# print(binned_angle_abc_data["ccw"], "\t")

# average ignore zeros

averaged_binned_angle_abc_data = {
    "angles": [

    ],
    "cw":{
        "a": [],
        "b": [],
        "c": []
    },
    "ccw": {
        "a": [],
        "b": [],
        "c": []
    }
}


for key in combined_data.keys():
    for angle_str in binned_angle_abc_data[key]:
        #angle_str = str((angle_idx/16384) * 2 * np.pi)
        m_a = binned_angle_abc_data[key][angle_str]["a"] # filter for 0
        m_b = binned_angle_abc_data[key][angle_str]["b"]
        m_c = binned_angle_abc_data[key][angle_str]["c"]

        if len(m_a) > 0:
            mean_a = np.mean(np.asarray(m_a))
        else:
            mean_a = 0
        averaged_binned_angle_abc_data[key]["a"].append(mean_a)

        if len(m_b) > 0:
            mean_b = np.mean(np.asarray(m_b))
        else:
            mean_b = 0
        averaged_binned_angle_abc_data[key]["b"].append(mean_b)

        if len(m_c) > 0:
            mean_c = np.mean(np.asarray(m_c))
        else:
            mean_c = 0

        averaged_binned_angle_abc_data[key]["c"].append(mean_c)

        angle = float(angle_str)
        
        
        
        if key == "cw":
            averaged_binned_angle_abc_data["angles"].append(angle)
        
print('len averaged_binned_angle_abc_data["cw"]["a"]', len(averaged_binned_angle_abc_data["cw"]["a"]))
print('len averaged_binned_angle_abc_data["cw"]["b"]', len(averaged_binned_angle_abc_data["cw"]["b"]))
print('len averaged_binned_angle_abc_data["cw"]["c"]', len(averaged_binned_angle_abc_data["cw"]["c"]))
print('len averaged_binned_angle_abc_data["ccw"]["a"]', len(averaged_binned_angle_abc_data["ccw"]["a"]))
print('len averaged_binned_angle_abc_data["ccw"]["b"]', len(averaged_binned_angle_abc_data["ccw"]["b"]))
print('len averaged_binned_angle_abc_data["ccw"]["c"]', len(averaged_binned_angle_abc_data["ccw"]["c"]))
print('len averaged_binned_angle_abc_data["angles"]', len(averaged_binned_angle_abc_data["angles"]))
print(averaged_binned_angle_abc_data["angles"])
print("---------------------")
#print("binned_voltage_data", binned_voltage_data)

averaged_compressed_binned_angle_abc_data = {
    "angles": [

    ],
    "cw":{
        "a": [],
        "b": [],
        "c": []
    },
    "ccw": {
        "a": [],
        "b": [],
        "c": []
    }
}

for key in combined_data.keys():
    for angle_str in binned_voltage_data[key]:
        m_a = binned_voltage_data[key][angle_str]["a"]
        m_b = binned_voltage_data[key][angle_str]["b"]
        m_c = binned_voltage_data[key][angle_str]["c"]

        if len(m_a) > 0:
            mean_a = np.mean(np.asarray(m_a))
        else:
            mean_a = 0
        averaged_compressed_binned_angle_abc_data[key]["a"].append(mean_a)

        if len(m_b) > 0:
            mean_b = np.mean(np.asarray(m_b))
        else:
            mean_b = 0
        averaged_compressed_binned_angle_abc_data[key]["b"].append(mean_b)

        if len(m_c) > 0:
            mean_c = np.mean(np.asarray(m_c))
        else:
            mean_c = 0

        averaged_compressed_binned_angle_abc_data[key]["c"].append(mean_c)

        angle = float(angle_str)
        
        if key == "cw":
            averaged_compressed_binned_angle_abc_data["angles"].append(angle)

print("averaged_compressed_binned_angle_abc_data", averaged_compressed_binned_angle_abc_data)

# normalise the averaged_compressed_binned_angle_abc_data
np_avg_comp_bin_cw_a = np.asarray(averaged_compressed_binned_angle_abc_data["cw"]["a"])
np_avg_comp_bin_cw_a_max = np.max(np.abs(np_avg_comp_bin_cw_a))
np_avg_comp_bin_cw_a = np.round((((np_avg_comp_bin_cw_a / np_avg_comp_bin_cw_a_max))) * duty_max)
averaged_compressed_binned_angle_abc_data["cw"]["a"] = np_avg_comp_bin_cw_a.tolist()
np_avg_comp_bin_cw_b = np.asarray(averaged_compressed_binned_angle_abc_data["cw"]["b"])
np_avg_comp_bin_cw_b_max = np.max(np.abs(np_avg_comp_bin_cw_b))
np_avg_comp_bin_cw_b = np.round((((np_avg_comp_bin_cw_b / np_avg_comp_bin_cw_b_max))) * duty_max)
averaged_compressed_binned_angle_abc_data["cw"]["b"] = np_avg_comp_bin_cw_b.tolist()
np_avg_comp_bin_cw_c = np.asarray(averaged_compressed_binned_angle_abc_data["cw"]["c"])
np_avg_comp_bin_cw_c_max = np.max(np.abs(np_avg_comp_bin_cw_c))
np_avg_comp_bin_cw_c = np.round((((np_avg_comp_bin_cw_c / np_avg_comp_bin_cw_c_max))) * duty_max)
averaged_compressed_binned_angle_abc_data["cw"]["c"] = np_avg_comp_bin_cw_c.tolist()
np_avg_comp_bin_ccw_a = np.asarray(averaged_compressed_binned_angle_abc_data["ccw"]["a"])
np_avg_comp_bin_ccw_a_max = np.max(np.abs(np_avg_comp_bin_ccw_a))
np_avg_comp_bin_ccw_a = np.round((((np_avg_comp_bin_ccw_a / np_avg_comp_bin_ccw_a_max))) * duty_max)
averaged_compressed_binned_angle_abc_data["ccw"]["a"] = np_avg_comp_bin_ccw_a.tolist()
np_avg_comp_bin_ccw_b = np.asarray(averaged_compressed_binned_angle_abc_data["ccw"]["b"])
np_avg_comp_bin_ccw_b_max = np.max(np.abs(np_avg_comp_bin_ccw_b))
np_avg_comp_bin_ccw_b = np.round((((np_avg_comp_bin_ccw_b / np_avg_comp_bin_ccw_b_max))) * duty_max)
averaged_compressed_binned_angle_abc_data["ccw"]["b"] = np_avg_comp_bin_ccw_b.tolist()
np_avg_comp_bin_ccw_c = np.asarray(averaged_compressed_binned_angle_abc_data["ccw"]["c"])
np_avg_comp_bin_ccw_c_max = np.max(np.abs(np_avg_comp_bin_ccw_c))
np_avg_comp_bin_ccw_c = np.round((((np_avg_comp_bin_ccw_c / np_avg_comp_bin_ccw_c_max))) * duty_max)
averaged_compressed_binned_angle_abc_data["ccw"]["c"] = np_avg_comp_bin_ccw_c.tolist()
# range is currently +1 to -1 and we want to shift to have what? 0 -> 1

# create csv from averaged_compressed_binned_angle_abc_data

csv_lines = []

for angle_idx in range(len(averaged_compressed_binned_angle_abc_data["angles"])):
    angle_str = averaged_compressed_binned_angle_abc_data["angles"][angle_idx]
    cw_a = averaged_compressed_binned_angle_abc_data["cw"]["a"][angle_idx]
    cw_b = averaged_compressed_binned_angle_abc_data["cw"]["b"][angle_idx]
    cw_c = averaged_compressed_binned_angle_abc_data["cw"]["c"][angle_idx]
    ccw_a = averaged_compressed_binned_angle_abc_data["ccw"]["a"][angle_idx]
    ccw_b = averaged_compressed_binned_angle_abc_data["ccw"]["b"][angle_idx]
    ccw_c = averaged_compressed_binned_angle_abc_data["ccw"]["c"][angle_idx]

    csv_lines.append("%f,%f,%f,%f,%f,%f,%f" % (float(angle_str), cw_a, cw_b, cw_c, ccw_a, ccw_b, ccw_c))

csv_data = "\n".join(csv_lines)


# now generate the cpp code
def get_voltage_element(direction, channel, data):
    lines = []
    len_data = len(data)
    len_data_minus_one = len_data - 1
    lines.append("// %s voltage coefficient channel %s over %s compressed angular steps" % (direction, channel, str(len_data)))
    lines.append("#define %s_%s_VOLTAGE_CHANNEL {\\" % (direction, channel))
    for element_idx in range(len(data)):
        element = data[element_idx]
        if (element_idx == len_data_minus_one):
            lines.append("%d }" % element)
        else:
            lines.append("%d,\\" % element)
    return "\n".join(lines)

def generate_voltage_map():
    map_definition = "const int16_t VOLTAGE_MAP[2][3][%i] = {{CW_A_VOLTAGE_CHANNEL, CW_B_VOLTAGE_CHANNEL, CW_C_VOLTAGE_CHANNEL},{CCW_A_VOLTAGE_CHANNEL, CCW_B_VOLTAGE_CHANNEL, CCW_C_VOLTAGE_CHANNEL}};" % (int(max_compressed_value))
    cw_a = get_voltage_element("CW", "A", averaged_compressed_binned_angle_abc_data["cw"]["a"])
    cw_b = get_voltage_element("CW", "B", averaged_compressed_binned_angle_abc_data["cw"]["b"])
    cw_c = get_voltage_element("CW", "C", averaged_compressed_binned_angle_abc_data["cw"]["c"])
    ccw_a = get_voltage_element("CCW", "A", averaged_compressed_binned_angle_abc_data["ccw"]["a"])
    ccw_b = get_voltage_element("CCW", "B", averaged_compressed_binned_angle_abc_data["ccw"]["b"])
    ccw_c = get_voltage_element("CCW", "C", averaged_compressed_binned_angle_abc_data["ccw"]["c"])
    return "\n\n".join(
        [
            cw_a,
            cw_b,
            cw_c,
            ccw_a,
            ccw_b,
            ccw_c,
            map_definition
        ]
        )

with open("./calibration-data/combination-direct-fit-%s.json" % (combined_identifier), "w") as fout:
    fout.write(json.dumps(averaged_compressed_binned_angle_abc_data))

with open("./calibration-data/combination-direct-fit-%s.csv" % (combined_identifier), "w") as fout:
    fout.write(csv_data)

with open("./calibration-data/combination-direct-fit-%s.cpp" % (combined_identifier), "w") as fout:
    fout.write(generate_voltage_map())

cw_averaged_voltage_data = np.asarray([averaged_binned_angle_abc_data["cw"]["a"], averaged_binned_angle_abc_data["cw"]["b"], averaged_binned_angle_abc_data["cw"]["c"]]).ravel()
ccw_averaged_voltage_data = np.asarray([averaged_binned_angle_abc_data["ccw"]["a"], averaged_binned_angle_abc_data["ccw"]["b"], averaged_binned_angle_abc_data["ccw"]["c"]]).ravel()
cw_angles = np.asarray(averaged_binned_angle_abc_data["angles"])

print("Fitting cw model")
cw_voltage_data = np.asarray([data_to_fit_cw[1], data_to_fit_cw[2], data_to_fit_cw[3]]).ravel()


print("Fitting ccw model")
ccw_voltage_data = np.asarray([data_to_fit_ccw[1], data_to_fit_ccw[2], data_to_fit_ccw[3]]).ravel()


print("Creating plot.... please wait...")
#plot_title = 'Fit parameters:\n cw angular_disp=%.2f±%.1f phase_current_disp=%.2f±%.1f\n' % (utils.rad_to_deg(angular_displacement_cw), utils.rad_to_deg(errors_cw[0]), utils.rad_to_deg(phase_current_displacement_cw), utils.rad_to_deg(errors_cw[1]))
#plot_title += 'ccw angular_disp=%.2f±%.1f phase_current_disp=%.2f±%.1f' % (utils.rad_to_deg(angular_displacement_ccw), utils.rad_to_deg(errors_ccw[0]), utils.rad_to_deg(phase_current_displacement_ccw), utils.rad_to_deg(errors_ccw[1]))
plot_title = "Raw data vs averaged data fit"

fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(60, 5))
fig.suptitle(plot_title,fontsize=8)

# .reshape(3, data_to_fit_cw[0].shape[0])
plots.create_voltage_scatter(ax[0], data_to_fit_cw[0], cw_voltage_data.reshape(3, data_to_fit_cw[0].shape[0]))
plots.create_voltage_scatter(ax[1], cw_angles, cw_averaged_voltage_data.reshape(3, cw_angles.shape[0]))

plots.create_voltage_scatter(ax[2], data_to_fit_ccw[0], ccw_voltage_data.reshape(3, data_to_fit_ccw[0].shape[0]))
plots.create_voltage_scatter(ax[3], cw_angles, ccw_averaged_voltage_data.reshape(3, cw_angles.shape[0]))

#save id file

#with open('calibration-data/raw_reconstruction_%s.id' % combined_identifier, "w") as fout:
#    fout.write(run_ids_str)

# save plot as file
print("Saving plot.... please wait...")
fout='calibration-data/raw_reconstruction_direct_comp2_%s.png' % (combined_identifier)
print(fout)
fig.savefig(fout, pad_inches=0, bbox_inches='tight')

#plt.show()
print("Done :)")
print(data_to_fit_cw[0])