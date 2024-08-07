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
import regression

parser = argparse.ArgumentParser()

parser.add_argument('eeg_root_path', type=str,
                    help='directory of eeg data, to the directory that contains subject folders')
parser.add_argument('model_root_path', type=str,
                    help='directory of models, path of directory that contains models')

# Time window size will be in ms
parser.add_argument('w_size', metavar='window size', type=int,
                    help='The window size in ms e.g 2, 8 ,10 (must be a positive multitude by 2)')
parser.add_argument('save_path', metavar='output path', type=str,
                    help='Path to save the results of the experiment')
parser.add_argument("eeg_rdm_dist_metric", type=str, help="Distance metric to use to create eeg rdms")
parser.add_argument("model_rdm_dist_metric", type=str, help="Distance metric to use to create model rdms")
parser.add_argument("experiment_type", type=str, choices=["naive", "prior"],
                    help="Type of the experiment, either prior or naive")
parser.add_argument("stimulus_type", type=str, choices=["video", "still-ff", "still-mf"],
                    help="Type of the stimuli, either still-mf, still-ff or video")
parser.add_argument('--avg_subjects_rdm', dest='use_avg_rdms', action='store_true',
                    help="calculates statistics based on subject wise averaged rdms")
parser.add_argument('--sep_subjects_rdm', dest='use_avg_rdms', action='store_false',
                    help="calculates statistics based on each subject subject rdms")
parser.set_defaults(use_avg_rdms=True)
args = parser.parse_args()

if args.w_size <= 0 or args.w_size % 2 != 0:
    raise (
        argparse.ArgumentTypeError("%s is must be a positive multiple of 2 (Because 500Hz eeg was used)" % args.w_size))

# Apply Bonferroni correction?
correct = True

# Get names of the subject folders (folders starting with subj)
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

# No need to create all over, saves computation
model_RDM_dict = {}
for model_file in os.listdir(args.model_root_path):

    # Filter hidden files
    if not model_file.startswith("."):

        # Don't include flow model and video gabor model for still input types
        if ("still" in args.stimulus_type and (
                "video" in model_file or "flow" in model_file or "motion" in model_file or "avg" in model_file)
                or "video" in args.stimulus_type and ("ff" in model_file or "mf" in model_file)
                or "still-mf" in args.stimulus_type and ("ff" in model_file)
                or "still-ff" in args.stimulus_type and ("mf" in model_file)):
            continue

        # Choose rdm metric as correlation for gabor or flow models else use hamming
        model_rdm_dist_metric = 'correlation' if "gabor" in model_file or \
                                                 "flow" in model_file or \
                                                 "motion" in model_file or \
                                                 "intensity" in model_file \
            else args.model_rdm_dist_metric

        # Get the model name
        model_name = os.path.splitext(model_file)[0] + "_" + model_rdm_dist_metric

        # Check if every model rdm was already created in model_RDM_path, if it is, load that rdm
        if model_name + '.npy' in os.listdir(model_RDM_path):
            print("Model RDM for {0} with distance metric: {1} was found in {2},"
                  " loading already created Model RDM ".format(model_name, model_rdm_dist_metric, model_RDM_path))
            model_RDM_dict[model_name] = rsa_io.load_rdm(model_RDM_path + model_name)
        else:
            model = rsa_io.load_model(file_path=args.model_root_path + model_file)
            model_RDM_dict[model_name] = rsa.create_rdm(model, metric=model_rdm_dist_metric, name=model_name,
                                                        save_path=model_RDM_path)

# Compare model and eeg rdms and save statistics to a list
rdm_statistics_list = []

# VIF Analysis, reeturns the models afrer regression analysis
remaning_models = regression.vif_analysis(model_RDM_dict, args.save_path)

# get the rdms as a list and get their names
model_rdms = [model_RDM_dict[model] for model in remaning_models]

# Make the list of model rdms into one model regressor matrix (nmodelsx276)
regressor_matrix = np.column_stack(model_rdms)

regression_results_list = []
# List the electrode regions used
electrode_regions = ['central', 'frontal', 'parietal', 'temporal', 'whole_brain', 'occipital']
rsquared_adjusted = {}
for electrode_region in electrode_regions:

    # Check if eeg_rdm exists in eeg_rdm_path, if experiment is already done with this w_size and
    # eeg_rdm_distance load that rdm

    # create the name of eeg rdm file
    eeg_rdm_fname = "eeg_rdm_" + args.experiment_type + "_" + args.stimulus_type + "_" + electrode_region + "_" + \
                    str(args.w_size) + "_" + args.eeg_rdm_dist_metric

    # If  eeg_rdm exists, load
    if eeg_rdm_fname + ".hdf5" in os.listdir(eeg_rdm_path):
        print("EEG RDMs with parameters with window size: {0} and distance: "
              "{1} is already created for electrode location "
              "{2} in experiment {3},{4}, loading from {5}"
              .format(str(args.w_size), args.eeg_rdm_dist_metric, electrode_region,
                      args.experiment_type, args.stimulus_type, eeg_rdm_path + eeg_rdm_fname))
        windowed_eeg_rdm_dict, attributes = rsa_io.load_from_hdf5(eeg_rdm_fname, eeg_rdm_path, args.experiment_type,
                                                                  args.stimulus_type)
    else:

        # Dictionary where time windows are keys and EEG rdm data is value. Each EEG rdm data is
        # n_subjects x 276.
        windowed_eeg_rdm_dict = defaultdict(list)

        # For all subjects do
        for i, subject_folder in enumerate(subject_folders):
            subj_name = subject_folder[0:9]
            subj_path = args.eeg_root_path + subject_folder + "/" + electrode_region + "/action-mats/"

            # Keys are time windows, Each value in the time_window_representations is a 3D ndarray
            # with size (n_conditions, n_channels).
            time_window_representations = rsa_io.build_eeg_data(subj_path, args.w_size, subj_name,
                                                                args.experiment_type, args.stimulus_type)

            # traverse each window in time_window_representations and calculate rdm
            for window, eeg_data in time_window_representations.items():
                eeg_rdm_name = subj_name + '_eeg_rdm_' + args.experiment_type + args.stimulus_type + "_" + \
                               str(window[0]) + ":" + str(window[1]) + "_" + args.eeg_rdm_dist_metric
                windowed_eeg_rdm_dict[window].append(rsa.create_rdm(eeg_data, args.eeg_rdm_dist_metric, eeg_rdm_name))

        # Convert windowed_eeg_rdm_dict from defaultdict to dict
        windowed_eeg_rdm_dict = dict(windowed_eeg_rdm_dict)
        for window, eeg_rdm_list in windowed_eeg_rdm_dict.items():
            windowed_eeg_rdm_dict[window] = np.vstack(eeg_rdm_list)

        # Save eeg rdms to hdf5 file
        rsa_io.save_to_hdf5(electrode_region, windowed_eeg_rdm_dict, args.eeg_rdm_dist_metric, n_subjects
                            , args.w_size, eeg_rdm_fname, eeg_rdm_path, args.experiment_type, args.stimulus_type)

    # Regression
    rr, rsquares = regression.regression(windowed_eeg_rdm_dict, model_RDM_dict, args.experiment_type,
                               args.stimulus_type, electrode_region)

    # Adjusetd rsquares
    rsquared_adjusted[electrode_region] = rsquares
    regression_results_list.extend(rr)

    # Kendall tau
    for model_name, model_RDM in model_RDM_dict.items():
        for time_window, EEG_RDM_list in windowed_eeg_rdm_dict.items():

            # If average RDM will be used take avg of EEG RDM list
            if args.use_avg_rdms:
                kendall_tau, kendall_p_value = rsa.correlate_models(model_RDM, np.mean(EEG_RDM_list, 0))
                rdm_statistics_list.append([args.experiment_type, args.stimulus_type, electrode_region,
                                            model_name, time_window[0], kendall_tau, kendall_p_value])

            # Else, iterate over EEG RDM list calculate Kendall tau for each subject and append to rmd_statistics_list
            else:
                for i, EEG_RDM in enumerate(EEG_RDM_list):
                    kendall_tau, kendall_p_value = rsa.correlate_models(model_RDM, EEG_RDM)
                    rdm_statistics_list.append([args.experiment_type, args.stimulus_type, i, electrode_region,
                                                model_name, time_window[0], kendall_tau, kendall_p_value])

# Column names for the resulting df
rr_columns = ['experiment_type', 'stimuli_type', 'electrode_region', 'model_name', 'time', 'beta_value',
              't_value', 'p_value', 'lower_conf_interval', 'upper_conf_interval']

# Convert regression results list to df with column names
regression_results_df = pd.DataFrame(regression_results_list, columns=rr_columns)

# Sort by time values to have a better ordering based on time window
regression_results_df = regression_results_df.sort_values(by="time")

if args.use_avg_rdms:

    rdm_statistics_df = pd.DataFrame(rdm_statistics_list, columns=['experiment_type', 'stimulus_type',
                                                                   'electrode_region', 'model_name', 'time',
                                                                   'kendall_tau', 'kendall_p-value'])
    pkl_name = "_avg_subjects_results.pkl"

# If separated subjects add additional subject no column to the dataframe, change pkl name to seperated
else:
    rdm_statistics_df = pd.DataFrame(rdm_statistics_list, columns=['experiment_type', 'stimulus_type', 'subject_no',
                                                                   'electrode_region', 'model_name', 'time',
                                                                   'kendall_tau', 'kendall_p-value'])
    pkl_name = "_seperated_subjects_results.pkl"

# sort dataframe by time to have continuous time
rdm_statistics_df = rdm_statistics_df.sort_values(by="time")

# Save as pickle
with open(args.save_path + args.eeg_rdm_dist_metric + "_" + args.model_rdm_dist_metric + "_regression_results.pkl",
          'wb') as f:
    pickle.dump([regression_results_df, args.eeg_rdm_dist_metric, args.model_rdm_dist_metric, rsquared_adjusted], f)

with open(args.save_path + args.eeg_rdm_dist_metric + "_" + args.model_rdm_dist_metric + pkl_name, 'wb') as f:
    pickle.dump([rdm_statistics_df, args.eeg_rdm_dist_metric, args.model_rdm_dist_metric], f)
