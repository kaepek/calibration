# KAEPEK-CALIBRATION V1.3.0

A calibration library for synchronising bldc motor voltage models with digital absolute position rotary encoders. Note for now this library is only configured for using the AS5147P encoder with [this breakout circuit](https://www.mouser.co.uk/ProductDetail/ams-OSRAM/AS5147P-TS_EK_AB?qs=Rt6VE0PE%2FOfngSpzc2DH8w%3D%3D&mgh=1&vip=1&gclid=Cj0KCQjwm6KUBhC3ARIsACIwxBjypycJOODZLcuEXv6ZZNorVRH8abVcmWROeClnLvezKtGCmwOAK5UaArH_EALw_wcB)

# Galvanically isolated ADC/Encoder circuit

[Circuit](./circuits/calibration/circuit)

![calibration circuit](./circuits/calibration/circuit/Schematic_JK-BLDC-Encoder-Calibrator-Tester4_2023-05-02.png)

![calibration pcb](./circuits/calibration/circuit/PCB_PCB_JK-BLDC-Encoder-Calibrator-Tester4_2023-05-02.png)

## Connecting AS5147P breakout circuit to the calibration circuit

Connection is made by simply connecting a 8 pin header ribbon cable between the encoder and the calibration circuit. See below:

![calibration connections](./resources/calibration_encoder_wiring.png)

Specific pin connections are mentioned below for reference:

### Encoder information table:

AS5147 pin| 5v| 3.3v| x| csn| clk| mosi| miso| GND
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
Teensy 4.0 #2 pin| 3.3v| 3.3v| x| 10| 22| 11| 12| GND

### Connecting Teensy 4.0 #1 with Teensy 4.0 #2 with two H11L1 optocouplers.

Teensy 4.0 #1 acts as a master and sends signals via two galvanically isolated optocouplers to Teensy 4.0 #2. 

### Connection information table:

H11L1 #1 RESET pin| 1 (ANODE)| 2 (CATHODE)| 3(NC)| 4(Vo)| 5 (GND)| 6(VCC)
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
Teensy 4.0 #1 pin| 3| GND| X| X| X| X
Teensy 4.0 #2 pin| X| X| X| 3| GND| 3.3V

H11L1 #2 CLK pin| 1 (ANODE)| 2 (CATHODE)| 3(NC)| 4(Vo)| 5 (GND)| 6(VCC)
:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:
Teensy 4.0 #1 pin| 8| GND| X| X| X| X
Teensy 4.0 #2 pin| X| X| X| 21| GND| 3.3V


# SBLDC-SMT circuit

[Circuit](https://github.com/kaepek/sbldc-smt/tree/e0ab160f8fc606f709ad24c7c99f17e19a991b6a/circuit)

Note that one the voltage divider grid is used for this use case which enables reading voltages from phase A,B,C and the common virtual neutral (VN).

![sbldc-smt circuit](https://github.com/kaepek/sbldc-smt/blob/e0ab160f8fc606f709ad24c7c99f17e19a991b6a/circuit/Schematic_drone-smt-3-high-power_2022-06-06.png?raw=true)

![sbldc-smt pcb](https://github.com/kaepek/sbldc-smt/blob/e0ab160f8fc606f709ad24c7c99f17e19a991b6a/circuit/PCB_pcb_2022-06-08.png?raw=true)

## Connecting KAEPEK-SBDLC-SMT-V2.4.0 circuit to the calibration circuit

Connection is made by simply connecting the 13 pin header from the KAEPEK-SBDLC-SMT-V2.4.0 pcb to the KAEPEK-Calibration circuit pcb with the surface mount components point upwards. 

Specific pin connections are mentioned below for reference:

### ADC/ADC-ETC information table:

| PHASE       | A   | B      | VN    | C     |
|-------------|-----|--------|-------|-------|
| Teensy 4.0 #1 pin         | 14  | 15     | 17    | 16    |
| COLOUR      | RED | YELLOW | GREEN | BLACK |
| TRIG        | 0   | 1      | 2     | 3     |
| DONE        | 0   | 1      | 0     | 1     |
| HW-CH       | 1   | 2      | 3     | 4     |
| ADC-CH      | 7   | 8      | 11    | 12    |

### Other pins

- Connect Teensy 4.0 #1 ground to pin 7 of KAEPEK-SBDLC-SMT#V2.4.0

# Collecting ADC/Encoder data for calibration instructions.

Need two computers to collect clean data from this setup. One needs to be a laptop (computer #1) which is disconnected from everything, networking via wifi nessesary.

1. Modify zero_crossing_adc.ino and set the PWM_FREQUENCY to full calibration logging speed e.g. 90kHz.
2. Make sure zero_crossing_adc.ino has been loaded onto the Teensy 4.0 #1.
3. Make sure AS5147P_teensy40.ino has been loaded onto the Teensy 4.0 #2.
4. Find network address of computer #1 and computer #2 by running `ifconfig` or similar. e.g. '192.168.0.15'.
5. Plug Teensy 4.0 #2 (Encoder) into computer #2.
6. Plug Teensy 4.0 #1 (ADC) into computer #1 (needs to be a fully charged laptop disconnected from everything else apart from the Teensy [not ethernet allowed]).
7. Unplug and replug Teensy 4.0 #1 into computer #1 (forcing a reset).
8. Start the network sync program on computer #1 and provide a name for this data collection run e.g. 'aug_18_test_1'. `npm run network-serial:collect-sync --run_id=aug_18_test_1`. 
9. SSH to computer #2.
10. Start the network source program on computer #2. `npm run network-serial:collect-source --device_id=1 --sync_host=10.0.0.110` .
11. Use a power drill to spin the motor at a constant high angular velocity.
12. Start the network source program on computer #1. `npm run network-serial:collect-source --device_id=0 --sync_host=0.0.0.0` .
13. After you are happy enough data has been collected stop collection by unplugging Teensy 4.0 #1.
14. Ensure `network-serial:collect-source` is stopped for both computers. By typing `Ctrl-c` into the relevant terminal sessions.
15. At this point the `network-serial:collect-sync` will merge the dataset and create an output file `./calibration-data/[run_id].jsonl` on computer #1. If this does not work try manually merging the files, see the next section below, otherwise move on to data analysis.


# Manually merging the datasets if network merge fails:

1. Each source program will write to the `/tmp` folder before network transmission is attempted. Take the `/tmp/serial-data-device-[x].jsonl` file from the `/tmp` folder's from each computer and place into a folder under `./calibration-data/[experiment-name]/` of computer #1.
2. Combine datasets into a single file `node calibration/combine-multicapture-files.js [experiment-name]`
3. Rename the resultant file the same name as the experiment name `[experiment-name].jsonl` and move to parent folder.
4. Combine the collected `[experiment-name].jsonl` `npm run combine:rotation-voltage-network-data --dataset=[experiment-name].jsonl`, you will recieve a file `[experiment-name].jsonl.matched.csv` if the successful, this program will report how successful it was in matching records high match rate is expect ~98%.
5. Proceed from step 1 from the analysis instructions.

# Data analysis:

1. Combine the collected `./calibration-data/[run_id]/raw_capture_data.jsonl` file `npm run combine:rotation-voltage-network-data --run_id=[run_id]`, you will recieve a file `merged_capture_data.csv` in the `./calibration-data/[run_id]` folder if successful, this program will report how well it matched records, high match rate is expect ~98% for good runs.
2. Inspect the `./calibration-data/[run_id]/merged_capture_data.csv` file using the command and tune the kalman settings at the top (trial and error if nessesary, looking for kalman closely following the signal without to much noise).
    - `npm run inspect:rotation-voltage-data --run_id=[run_id]`
3. When you are happy with the quality of the kalman tuning, you can now smooth the data. This will create a `kalman_smoothed_merged_capture_data.json` file within `./calibration-data/[run_id]` folder, as well as a html report file `kalman_smoothed_merged_capture_data.html`.
    - `npm run smooth:rotation-voltage-data --run_id=[run_id]`
4. With data now smoothed to minimise zero-crossing detection errors you can apply zero-crossing detection. This will create a `zero_crossing_detections.channels.all.json` which contains grouped lists of angles for each channel cluster e.g. 'zc_channel_af_data' which stands for zero crossing channel phase A falling, where a given phaseA-vn crossed zero. Also a `zero_crossing_detections.histogram.all.json` file will be created which contains any zero crossing events for each channel organised by angle.
  - `npm run detect:zero-crossing --run_id=[run_id]`
5. Now for each channel we should have `motor_poles/2` zero-crossing events, noise will prevent us knowing the exact angle where this happenes, we will in fact have a distribtion of points clustered around `motor_poles/2` centers... thus we can cluster the zero-crossing events into `motor_poles/2` groups. This will create a `kmedoids_clustered_zero_crossing_channel_detections.all.json` files, containing the clustered angles and their centroids (mean points) for each channel.
  - `npm run cluster:zero-crossing --run_id=sept2 --number_of_poles=14`.
6. Next we need to analyse how well the clustering went. Important metrics will be the mean point of each cluster, the standard deviation of each cluster and finally we need a map which identifes for each angle which channel cluster represents that point best if any. The following file is created showing this data `kmedoids_clustered_zero_crossing_channel_detections.all.analysis.json`.
  - `npm run analyse:zero-crossing-channel-clusters --run_id=sept2`
7. Next we need to see the results of the analysis, also we need to use the statistics generated to eliminate cluster outliers a program is provided to do this. A file `zero_crossing_detections.channels.outliers.json` is produced which contains the outliers detected for each channel, a file `zero_crossing_detections.channels.inliers.json` is produces which contain valid inliers per channel and finally a report file `zero_crossing_detections.channels.all.html` is generated to visualise this analysis.
  - `npm run inspect:zero-crossing --run_id=sept2`
8. Next with the outliers removed from the dataset and stored in their own file `zero_crossing_detections.channels.inliers.json`, we need to re-cluster the channels into `motor_poles/2` groups again to create a new file `kmedoids_clustered_zero_crossing_channel_detections.inliers.json`.
  - `npm run cluster-inliers:zero-crossing --run_id=sept2 --number_of_poles=14`
9. Next we need to re-analyse the re-clustered channel zero-crossing angles to create a new analysis file `kmedoids_clustered_zero_crossing_channel_detections.inliers.analysis.json`.
  - `npm run analyse-inliers:zero-crossing-channel-clusters --run_id=sept2`
10. Next we need to see the results of the re-analysis post outlier elimination.
  - `npm run inspect-inliers:zero-crossing --run_id=sept2`

[Good ADC capture with Kalman filtering example output of smooth:rotation-voltage-data](./resources/kalman_smoothed_merged_capture_data.html)

# Analysis super command

`npm run perform-all-analysis --run_id=[run_id]`

`npm run perform-all-analysis --run_id=16sept_4_cw`
`npm run perform-all-analysis --run_id=16sept_ccw`

# Combing cw/ccw runs

`npm run combine-datasets:zero-crossing-inliers --run_ids=16sept_ccw,16sept_4_cw`

# Analysing the combined reports

So when generating a report a html file and an id file will be created with an identifier e.g.
`combination-report-lqwkwldkjpvgmrbeqcop.id` where `lqwkwldkjpvgmrbeqcop` would be the identifier for
a set of results.

One can fit a sine wave to the zc data:

`npm run fit-sine:zc --combination_identifier=lqwkwldkjpvgmrbeqcop`

One can fit a sine wave to the raw voltage data:

`npm run fit-sine:raw --combination_identifier=lqwkwldkjpvgmrbeqcop`

# Troubleshooting:

- Permission denied when trying to run `network-serial:collect-source`
  - Change permissions for Teensy device `sudo chmod a+rw /dev/ttyACM0`
- One voltage channel 's(A,B,C) peak (in inspect) is larger than the other one.
  - Check circuit connections
  - Disconnect laptop from mains.

# Documentation
Requires running `npm run generate:docs`

-  [JS Docs](../docs/global.html)

# 3rd party useful component information:

## H11L1 Opto-isolator

- [Datasheet](https://www.mouser.com/datasheet/2/149/H11L1M-1010369.pdf)

## AS5147P Encoder

- [Datasheet](https://ams.com/documents/20143/36005/AS5147P_DS000328_2-00.pdf)
