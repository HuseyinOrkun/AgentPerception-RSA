# Uses functions in other files to do the experiment
from collections import defaultdict
import rsa_io
import rsa
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('eeg_root_path', type=str,
                    help='Path to save the results of the experiment')
parser.add_argument('model_root_path', type=str,
                    help='directory of models')
parser.add_argument('w_size', metavar='window size', type=int,
                    help='The window size')
parser.add_argument('save_path', metavar='output path', type=str,
                    help='Path to save the results of the experiment')
parser.add_argument("eeg_rdm_dist_metric",type=str,help="Distance metric to use to create eeg rdms")
parser.add_argument("model_rdm_dist_metric",type=str,help="Distance metric to use to create model rdms")

args = parser.parse_args()
subject_folders = [name for name in os.listdir(args.eeg_root_path) if
                   os.path.isdir(args.eeg_root_path + name) and name.startswith("subj")]
n_subjects = len(subject_folders)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
pd.set_option('display.width', None)

# Create modelRDMs folder in models if not exists
model_RDM_path = args.save_path + "modelRDMs/"
if not os.path.exists(model_RDM_path):
    os.makedirs(model_RDM_path)

# Create eegRDMs folder in models if not exists
eeg_rdm_path = args.save_path + "eegRDMs/"
if not os.path.exists(eeg_rdm_path):
    os.makedirs(eeg_rdm_path)


# Check if eeg_rdm exists in eeg_rdm_path, meaning that experiment is already done with this w_size and eeg_rdm_distance
windowed_eeg_rdm_dict = None
eeg_rdm_fname = "eeg_rdm_" + str(args.w_size) + "_" + args.eeg_rdm_dist_metric
eeg_rdm_ready = False
if eeg_rdm_fname + ".hdf5" in os.listdir(eeg_rdm_path):
    print("EEG RDMs with parameters with window size: {0} and distance: {1} is already created, loading from {2}".format(str(args.w_size) ,  args.eeg_rdm_dist_metric, eeg_rdm_path + eeg_rdm_fname))
    windowed_eeg_rdm_dict, attributes = rsa_io.load_from_hdf5(eeg_rdm_fname,eeg_rdm_path)
    eeg_rdm_ready = True

# Print information message on which files are going to be used
if eeg_rdm_ready:
    print("All rdms are already exist in {0} , loading already created rdms with window size: {1} and distance "
          "metric: {2}".format(eeg_rdm_path, args.w_size, args.eeg_rdm_dist_metric))

# Check if every model rdm was already created in model_RDM_path if all model_rdms exists
# No need to create all over, saves computation
model_RDM_dict = {}
for model_file in os.listdir(args.model_root_path):
    if not model_file.startswith("."):
        model_name = os.path.splitext(model_file)[0] + "_" + args.model_rdm_dist_metric
        if not model_name + '.npy' in os.listdir(model_RDM_path):
            model = rsa_io.load_model(file_path=args.model_root_path + model_file)
            model_RDM_dict[model_name] = rsa.create_rdm(model.values, metric=args.model_rdm_dist_metric, name=model_name,
                                                        save_path=model_RDM_path, model=True)
        else:
            print("Model RDM for {0} with distance metric: {1} was found in {2},"
                  " loading already created Model RDM ".format(model_name, args.model_rdm_dist_metric, model_RDM_path))
            model_RDM_dict[model_name] = rsa_io.load_rdm(model_RDM_path + model_name)

if not eeg_rdm_ready:
    # every key is time point and every value is a list of corresponding rdms of different subjects
    windowed_eeg_rdm_dict = defaultdict(list)

    # For all subjects do
    for i, subject_folder in enumerate(subject_folders):
        subj_name = subject_folder[0:6]
        subj_path = args.eeg_root_path + subject_folder + "/action-mats/"

        # Keys are time windows, Each value in the time_window_representations is a 3D ndarray
        # with size (n_conditions, n_trials, n_channels). Since n_trials are not same for each condition,
        # the missing values are filled with NaN.
        time_window_representations = rsa_io.build_eeg_data(subj_path, args.w_size)

        # traverse each window in time_window_representations and calculate rdm
        # TODO: values of windowed_eeg_rdm_dict may be not a list
        #  but 3d numpy array (n_subjects, n_conditions, n_conditions)
        for window, eeg_data in time_window_representations.items():
            eeg_rdm_name = subj_name + '_eeg_rdm_' + str(window[0]) + ":" + str(window[1]) + "_" + args.eeg_rdm_dist_metric
            windowed_eeg_rdm_dict[window].append(rsa.create_rdm(eeg_data, args.eeg_rdm_dist_metric, eeg_rdm_name))

    # TODO: try without vstack
    for window, eeg_rdm_list in windowed_eeg_rdm_dict.items():
        windowed_eeg_rdm_dict[window] = np.vstack(eeg_rdm_list)

    # Save eeg rdms to hdf5 file
    rsa_io.save_to_hdf5(windowed_eeg_rdm_dict, args.eeg_rdm_dist_metric, args.w_size, eeg_rdm_fname, eeg_rdm_path)


# Compare model and eeg rdms append to a list
rdm_statistics_list = []
for model_name, model_RDM in model_RDM_dict.items():
    dist_per_time_window = []
    for time_window, EEG_RDM_list in windowed_eeg_rdm_dict.items():
        kendall_tau, kendall_p_value = rsa.correlate_models(model_RDM, np.mean(EEG_RDM_list, axis=0))
        rdm_statistics_list.append([model_name, time_window, kendall_tau, kendall_p_value])

rdm_statistics_df = pd.DataFrame(rdm_statistics_list,
                                 columns=['Model name', 'Time window', 'Kendall tau', 'Kendall p-value'])
significant_rdms = rdm_statistics_df[rdm_statistics_df["Kendall p-value"]<=0.05]
print(significant_rdms.sort_values(by="Kendall tau", ascending=False))
# Calculate noise ceiling
upper_ceiling_list = []
lower_ceiling_list = []
for time_window, EEG_RDM_list in windowed_eeg_rdm_dict.items():
    lower_ceiling, upper_ceiling = rsa.calculateNoiseCeiling(EEG_RDM_list)
    lower_ceiling_list.append(lower_ceiling)
    upper_ceiling_list.append(upper_ceiling)
x = [str(wind) for wind in windowed_eeg_rdm_dict.keys()]
plt.plot(x, upper_ceiling_list)
plt.fill_between(x, lower_ceiling_list, upper_ceiling_list, color='grey', alpha=.5)
plt.show()