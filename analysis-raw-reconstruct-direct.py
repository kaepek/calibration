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
    for angle in range(0, 16384):
        angle_str = str((angle/16384) * 2 * np.pi)
        binned_angle_abc_data[key][angle_str] = {"a":[], "b":[], "c":[]}

for key in combined_data.keys():
    for i in range (data_length[key]):
        angle = combined_data[key][0][i]
        anvn = combined_data[key][1][i]
        bnvn = combined_data[key][2][i]
        cnvn = combined_data[key][3][i]
        angle_str = str(angle)
        if (angle_str in binned_angle_abc_data[key]):
            if anvn != 0 or anvn != 0.0:
                binned_angle_abc_data[key][angle_str]["a"].append(anvn)
            if bnvn != 0 or bnvn != 0.0:
                binned_angle_abc_data[key][angle_str]["b"].append(bnvn)
            if cnvn != 0 or cnvn != 0.0:
                binned_angle_abc_data[key][angle_str]["c"].append(cnvn)
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
fout='calibration-data/raw_reconstruction_direct_%s.png' % (combined_identifier)
print(fout)
fig.savefig(fout, pad_inches=0, bbox_inches='tight')

#plt.show()
print("Done :)")
print(data_to_fit_cw[0])