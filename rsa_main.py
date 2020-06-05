# Uses functions in other files to do the experiment
import matplotlib as mpl
mpl.use('Agg')
from collections import defaultdict
import rsa_io
import rsa
import argparse
import os
import pandas as pd
import numpy as np
import pickle

parser = argparse.ArgumentParser()

parser.add_argument('eeg_root_path', type=str,
                    help='directory of eeg data, to the directory that contains subject folders')
parser.add_argument('model_root_path', type=str,
                    help='directory of models, path of directory that contains models')
parser.add_argument('w_size', metavar='window size', type=int,
                    help='The window size in ms e.g 1, 5')
parser.add_argument('save_path', metavar='output path', type=str,
                    help='Path to save the results of the experiment')
parser.add_argument("eeg_rdm_dist_metric",type=str,help="Distance metric to use to create eeg rdms")
parser.add_argument("model_rdm_dist_metric",type=str,help="Distance metric to use to create model rdms")
parser.add_argument("experiment_type", type=str, choices=["naive", "prior"],
                    help="Type of the experiment, either prior or naive")
parser.add_argument("stimuli_type", type=str, choices=["video", "still"],
                    help="Type of the stimuli, either still or video")
args = parser.parse_args()

# Apply Bonferroni correction?
correct = True

# Apha value for statistical analysis
alpha = 0.001
subject_folders = [name for name in os.listdir(args.eeg_root_path) if
                   os.path.isdir(args.eeg_root_path + name) and name.startswith("subj")]
subject_folders.sort()
n_subjects = len(subject_folders)

# Create modelRDMs folder in models if not exists
model_RDM_path = args.save_path + "modelRDMs/"
if not os.path.exists(model_RDM_path):
    os.makedirs(model_RDM_path)

# Create eegRDMs folder in models if not exists
eeg_rdm_path = args.save_path + "eegRDMs/"
if not os.path.exists(eeg_rdm_path):
    os.makedirs(eeg_rdm_path)

# Check if every model rdm was already created in model_RDM_path if all model_rdms exists
# No need to create all over, saves computation
model_RDM_dict = {}
for model_file in os.listdir(args.model_root_path):

    # Don't include flow model and video gabor model for still input types
    if args.stimuli_type == "still" and "flow" in model_file or args.stimuli_type == "still" and "video" in model_file:
        continue
    if not model_file.startswith("."):
        metric = args.model_rdm_dist_metric if 'gabor' not in model_file and 'optic' not in model_file \
            else 'correlation'

        model_name = os.path.splitext(model_file)[0] + "_" + metric
        if not model_name + '.npy' in os.listdir(model_RDM_path):
            model = rsa_io.load_model(file_path=args.model_root_path + model_file)
            model_RDM_dict[model_name] = rsa.create_rdm(model, metric=metric, name=model_name,
                                                        save_path=model_RDM_path)
        else:
            print("Model RDM for {0} with distance metric: {1} was found in {2},"
                  " loading already created Model RDM ".format(model_name, args.model_rdm_dist_metric, model_RDM_path))
            model_RDM_dict[model_name] = rsa_io.load_rdm(model_RDM_path + model_name)

# Compare model and eeg rdms append to a list
rdm_statistics_list = []
electrode_regions = ['central', 'frontal', 'parietal', 'temporal', 'whole_brain', 'occipital']
for electrode_region in electrode_regions:

    windowed_eeg_rdm_dict = None
    # Check if eeg_rdm exists in eeg_rdm_path,
    # meaning that experiment is already done with this w_size and eeg_rdm_distance
    # create the name of eeg rdm file
    eeg_rdm_fname = "eeg_rdm_" + args.experiment_type + "_" + args.stimuli_type + "_" + electrode_region + "_" +\
                    str(args.w_size) + "_" + args.eeg_rdm_dist_metric

    if eeg_rdm_fname + ".hdf5" in os.listdir(eeg_rdm_path):
        print("EEG RDMs with parameters with window size: {0} and distance: "
              "{1} is already created for electrode location "
              "{2} in experiment {3},{4}, loading from {5}"
              .format(str(args.w_size), args.eeg_rdm_dist_metric, electrode_region,
                      args.experiment_type, args.stimuli_type, eeg_rdm_path + eeg_rdm_fname))

        windowed_eeg_rdm_dict, attributes = rsa_io.load_from_hdf5(eeg_rdm_fname, eeg_rdm_path
                                                                  ,args.experiment_type,args.stimuli_type)
    else:
        windowed_eeg_rdm_dict = defaultdict(list)

        # For all subjects do
        for i, subject_folder in enumerate(subject_folders):
            subj_name = subject_folder[0:9]
            subj_path = args.eeg_root_path + subject_folder + "/" + electrode_region + "/action-mats/"

            # Keys are time windows, Each value in the time_window_representations is a 3D ndarray
            # with size (n_conditions, n_channels).
            time_window_representations = rsa_io.build_eeg_data(subj_path, args.w_size, subj_name,
                                                                args.experiment_type, args.stimuli_type)

            # traverse each window in time_window_representations and calculate rdm
            for window, eeg_data in time_window_representations.items():
                eeg_rdm_name = subj_name + '_eeg_rdm_' + args.experiment_type+ args.stimuli_type + "_" + \
                               str(window[0]) + ":" + str(window[1]) + "_" + args.eeg_rdm_dist_metric
                windowed_eeg_rdm_dict[window].append(rsa.create_rdm(eeg_data, args.eeg_rdm_dist_metric, eeg_rdm_name))

        for window, eeg_rdm_list in windowed_eeg_rdm_dict.items():
            windowed_eeg_rdm_dict[window] = np.vstack(eeg_rdm_list)

        # Save eeg rdms to hdf5 file
        rsa_io.save_to_hdf5(electrode_region, windowed_eeg_rdm_dict, args.eeg_rdm_dist_metric, args.w_size,
                            eeg_rdm_fname, eeg_rdm_path,args.experiment_type,args.stimuli_type)

    for model_name, model_RDM in model_RDM_dict.items():
        for time_window, EEG_RDM_list in windowed_eeg_rdm_dict.items():
            for i, EEG_RDM in enumerate(EEG_RDM_list):
                kendall_tau, kendall_p_value = rsa.correlate_models(model_RDM, EEG_RDM)
                rdm_statistics_list.append([args.experiment_type, args.stimuli_type, i, electrode_region,
                                            model_name, 2 * (time_window[0] - 100), kendall_tau, kendall_p_value])

rdm_statistics_df = pd.DataFrame(rdm_statistics_list,
                                 columns=['experiment_type', 'stimulus_type', 'subject_no', 'electrode_region',
                                          'model_name', 'time', 'kendall_tau', 'kendall_p-value'])
rdm_statistics_df = rdm_statistics_df.sort_values(by="time")

with open(
        args.save_path + args.eeg_rdm_dist_metric + "_" + args.model_rdm_dist_metric + '_seperated_subjects_results.pkl',
        'wb') as f:
    pickle.dump([rdm_statistics_df, args.eeg_rdm_dist_metric, args.model_rdm_dist_metric], f)
