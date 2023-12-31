# Run in root directory

from time import sleep
import numpy as np
import sys
from bokeh.plotting import curdoc, figure
from bokeh.plotting import output_file, save
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis
import json
from tracking.kalman import Kalman_Filter_1D
import CyKalman

# create a kalman filter for each channel a-vn, b-vn, c-vn, vn & angle
#alpha = 6
#theta_resolution_error = 0.01
#jerk_error = 0.0000002

#alpha = 6.0 #50000.0
#theta_resolution_error = 0.01 #40.0
#jerk_error = 0.0000002 # 0.000000000001

#alpha = 0.000000000005 #50000.0
#theta_resolution_error = 0.00001 #40.0
#jerk_error = 0.000000000001 # 0.000000000001
alpha = 0.0000000005 #50000.0
theta_resolution_error = 0.00001 #40.0
jerk_error = 0.0000000001 # 0.000000000001

# self, double alpha, double x_resolution_error, double x_jerk_error, bint time_is_relative = False, double x_mod_limit =-1
# 50000.0,40.0,0.000000000001, 


Kalman_a_minus_vn = CyKalman.KalmanJerk1D(alpha, theta_resolution_error, jerk_error, False, 2**14) #kalman.Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_b_minus_vn = CyKalman.KalmanJerk1D(alpha, theta_resolution_error, jerk_error, False, 2**14) #kalman.Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_c_minus_vn = CyKalman.KalmanJerk1D(alpha, theta_resolution_error, jerk_error, False, 2**14) #kalman.Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)

"""
Kalman_a_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_b_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_c_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
alpha = 50
theta_resolution_error = 1
jerk_error = 0.0000002

Kalman_angle = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
"""

Kalman_angle = CyKalman.KalmanJerk1D(alpha, theta_resolution_error, jerk_error, False, 2**14)

# parse dataset argument
run_id = sys.argv[1] if len(sys.argv) > 1 else 0 
file_in = 'calibration-data/%s/merged_capture_data.csv' % (run_id)
file_out_json = 'calibration-data/%s/kalman_smoothed_merged_capture_data.json' % (run_id)
file_out_html = 'calibration-data/%s/kalman_smoothed_merged_capture_data.html' % (run_id)

# read dataset data
std_in = None
with open(file_in) as f: 
    std_in = f.readlines()
len_std_in = len(std_in)

# create graphing columns
plot_data = ColumnDataSource(
    dict(
        time=[],
        kalman_angle=[],
        kalman_a_minus_vn=[],
        kalman_b_minus_vn=[],
        kalman_c_minus_vn=[],
        #phase_a=[],
        #phase_b=[],
        #phase_c=[],
        #vn=[],
        #angle=[]
    )
)

plot_data2 = ColumnDataSource(
    dict(
        time=[],
        phase_a=[],
        phase_b=[],
        phase_c=[],
        vn=[],
        angle=[]
    )
)



plot_width = 15000 #58000
# create chart for (phaseXi - vn and angle)
kalman_pX_minus_vn_angle_vs_time = figure(title="Plot of (kalman phase_X_minus_vn, kalman angle vs time)", plot_width=plot_width, plot_height=850, y_range=(-100, 250)) # y_range=(-60, 150)
kalman_pX_minus_vn_angle_vs_time.xaxis.axis_label = 'Time [ticks]'
kalman_pX_minus_vn_angle_vs_time.yaxis.axis_label = '(Phase X - Virtual Neutral) Voltage [steps]'
kalman_pX_minus_vn_angle_vs_time.line(source=plot_data, x='time', y='kalman_a_minus_vn', color="red", legend_label="time vs kalman_a_minus_vn")
kalman_pX_minus_vn_angle_vs_time.line(source=plot_data, x='time', y='kalman_b_minus_vn', color=(246,190,0), legend_label="time vs kalman_b_minus_vn")
kalman_pX_minus_vn_angle_vs_time.line(source=plot_data, x='time', y='kalman_c_minus_vn', color="black", legend_label="time vs kalman_c_minus_vn")
kalman_pX_minus_vn_angle_vs_time.extra_y_ranges = {"angle": Range1d(start=0, end=16834)}
kalman_pX_minus_vn_angle_vs_time.add_layout(LinearAxis(y_range_name="angle", axis_label="Angle [steps]"), 'right')
kalman_pX_minus_vn_angle_vs_time.line(source=plot_data, x='time', y='kalman_angle', color="purple", legend_label="time vs kalman_angle", y_range_name="angle")

# create chart for (phaseA,phaseB,phaseC,vn and angle vs time)

pX_vn_angle_vs_time = figure(title="Plot of (phase_X, vn, angle vs time)", plot_width=plot_width, plot_height=850, y_range=(-100, 250))
pX_vn_angle_vs_time.xaxis.axis_label = 'Time [ticks]'
pX_vn_angle_vs_time.yaxis.axis_label = '(Phase X, vn) Voltage [steps]'
pX_vn_angle_vs_time.line(source=plot_data2, x='time', y='phase_a', color="red", legend_label="time vs phase A")
pX_vn_angle_vs_time.line(source=plot_data2, x='time', y='phase_b', color=(246,190,0), legend_label="time vs phase B")
pX_vn_angle_vs_time.line(source=plot_data2, x='time', y='phase_c', color="black", legend_label="time vs phase C")
pX_vn_angle_vs_time.line(source=plot_data2, x='time', y='vn', color="blue", legend_label="time vs vn")

pX_vn_angle_vs_time.extra_y_ranges = {"angle": Range1d(start=0, end=16834)}
pX_vn_angle_vs_time.add_layout(LinearAxis(y_range_name="angle", axis_label="Angle [steps]"), 'right')
pX_vn_angle_vs_time.line(source=plot_data2, x='time', y='angle', color="purple", legend_label="time vs kalman_angle", y_range_name="angle")


# add chart to current document
doc = curdoc()
curdoc().add_root(column( pX_vn_angle_vs_time, kalman_pX_minus_vn_angle_vs_time))
#pX_vn_angle_vs_time

# function to read the array of lines of the file and append them to measurements arrays
skip_to_line = 0
def pass_data():
    angles=[]
    phase_a_measurements = []
    phase_b_measurements = []
    phase_c_measurements = []
    vn_measurements = []
    times=[]

    for line_idx in range(skip_to_line, len_std_in):
        line = std_in[line_idx]
        line_strip = line.strip()
        data_str = line_strip.split("\t")
        print(data_str)
        time = float(data_str[0])
        angle = float(data_str[1])
        phase_a = float(data_str[2])
        phase_b = float(data_str[3])
        phase_c = float(data_str[4])
        vn = float(data_str[5])

        times.append(time)
        angles.append(angle)
        phase_a_measurements.append(phase_a)
        phase_b_measurements.append(phase_b)
        phase_c_measurements.append(phase_c)
        vn_measurements.append(vn)
    
    return (
        np.asarray(times),
        np.asarray(angles),
        np.asarray(phase_a_measurements),
        np.asarray(phase_b_measurements),
        np.asarray(phase_c_measurements),
        np.asarray(vn_measurements)
        )

# process data
data = pass_data()
print(data)

# this preforms kalman on (a-vn, b-vn, c-vn and angle) and returns the results for each channel
def perform_kalman_on_data(data):
    kalman_result = ([], [], [], [], [])
    for idx in range(len_std_in - 1):
        # unpack data
        #angle = data[0][idx]
        #make up angle as its not recorded for now
        time = data[0][idx]
        angle = data[1][idx]
        phase_a = data[2][idx]
        phase_b = data[3][idx]
        phase_c = data[4][idx]
        vn = data[5][idx]

        # compute phaseXi - vn
        phase_a_minus_vn = phase_a - vn
        phase_b_minus_vn = phase_b - vn
        phase_c_minus_vn = phase_c - vn

        # compute kalman
        """(_, kalman_state_a_minus_vn) = Kalman_a_minus_vn.estimate_state_vector_eular_and_kalman((time, phase_a_minus_vn))
        (_, kalman_state_b_minus_vn) = Kalman_b_minus_vn.estimate_state_vector_eular_and_kalman((time, phase_b_minus_vn))
        (_, kalman_state_c_minus_vn) = Kalman_c_minus_vn.estimate_state_vector_eular_and_kalman((time, phase_c_minus_vn))
        (_, kalman_state_angle) = Kalman_angle.estimate_state_vector_eular_and_kalman((time, angle))"""

        Kalman_a_minus_vn.step(time, phase_a_minus_vn)
        Kalman_b_minus_vn.step(time, phase_b_minus_vn)
        Kalman_c_minus_vn.step(time, phase_c_minus_vn)
        Kalman_angle.step(time, angle)

        # unpack kalman data if it exists
        kalman_a_minus_vn = 0
        kalman_b_minus_vn = 0
        kalman_c_minus_vn = 0
        kalman_angle = 0


        kalman_a_minus_vn = Kalman_a_minus_vn.get_kalman_vector()[0]
        kalman_b_minus_vn = Kalman_b_minus_vn.get_kalman_vector()[0]
        kalman_c_minus_vn = Kalman_c_minus_vn.get_kalman_vector()[0]
        kalman_angle = Kalman_angle.get_kalman_vector()[0]

        kalman_result[0].append(time)
        kalman_result[1].append(float(int(kalman_angle) % 16384))
        kalman_result[2].append(float(kalman_a_minus_vn))
        kalman_result[3].append(float(kalman_b_minus_vn))
        kalman_result[4].append(float(kalman_c_minus_vn))

        # we have enough measurements for a valid state estimate via kalman
        """if kalman_state_a_minus_vn is not None:
            # unpack
            kalman_state_a_minus_vn = kalman_state_a_minus_vn[0]
            kalman_state_b_minus_vn = kalman_state_b_minus_vn[0]
            kalman_state_c_minus_vn = kalman_state_c_minus_vn[0]
            kalman_state_angle = kalman_state_angle[0]

            kalman_a_minus_vn = kalman_state_a_minus_vn[0]
            kalman_b_minus_vn = kalman_state_b_minus_vn[0]
            kalman_c_minus_vn = kalman_state_c_minus_vn[0]
            kalman_angle = kalman_state_angle[0]

            kalman_result[0].append(time)
            kalman_result[1].append(float(int(kalman_angle) % 16384))
            kalman_result[2].append(float(kalman_a_minus_vn))
            kalman_result[3].append(float(kalman_b_minus_vn))
            kalman_result[4].append(float(kalman_c_minus_vn))
        """


    return kalman_result

# process data
processed_data = perform_kalman_on_data(data)
# save
json_data = json.dumps(processed_data) # , indent=4

print("processed_data", len(processed_data[0]), len(processed_data[1]), len(processed_data[2]), len(processed_data[3]), len(processed_data[4]) )
# json
with open(file_out_json, "w") as fout:
    fout.write(json_data)

# save graph
#file_in
#plot_data
plot_data.data["time"] = processed_data[0]
plot_data.data["kalman_angle"] = processed_data[1]
plot_data.data["kalman_a_minus_vn"] = processed_data[2]
plot_data.data["kalman_b_minus_vn"] = processed_data[3]
plot_data.data["kalman_c_minus_vn"] = processed_data[4]
#data
plot_data2.data["time"] = data[0]
plot_data2.data["angle"] = data[1]
plot_data2.data["phase_a"] = data[2]
plot_data2.data["phase_b"] = data[3]
plot_data2.data["phase_c"] = data[4]
plot_data2.data["vn"] = data[5]



"""
       np.asarray(times),
        np.asarray(angles),
        np.asarray(phase_a_measurements),
        np.asarray(phase_b_measurements),
        np.asarray(phase_c_measurements),
        np.asarray(vn_measurements)"""

output_file(filename=file_out_html, title="Kalman filtered sensor data")
save(doc)