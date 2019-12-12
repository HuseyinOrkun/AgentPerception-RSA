# Uses functions in other files to do the experiment
from collections import defaultdict

import rsa_io
import rsa
import argparse
import os
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('eeg_root_path', type=str,
                    help='Path to save the results of the experiment')
parser.add_argument('model_root_path', type=str,
                    help='directory of models')
parser.add_argument('w_size', metavar='window size', type=int,
                    help='The window size')
parser.add_argument('save_path', metavar='output path', type=str,
                    help='Path to save the results of the experiment')

args = parser.parse_args()
eeg_rdm_dist_metric = 'mahalanobis'
model_rdm_dist_metric = 'euclidean'


# Create modelRDMs folder in models if not exists
model_RDM_path = args.save_path + "/modelRDMs/"
if not os.path.exists(model_RDM_path):
    os.makedirs(model_RDM_path)

# Create eegRDMs folder in models if not exists
eeg_RDM_path = args.save_path +"/eegRDMs/"
if not os.path.exists(args.eeg_root_path):
    os.makedirs(args.eeg_root_path)

rdm_ready = False
for start in range(0, 400, args.w_size):
    end = start+args.w_size
    name = 'eeg_rdm_' + str(start) + ":" + str(end) + "_" + eeg_rdm_dist_metric + ".npy"
    if not name in os.listdir(eeg_RDM_path):
        rdm_ready = False

model_RDM_dict = {}
for model_file in os.listdir(args.model_root_path):
    model_name = os.path.splitext(model_file)[0] + "_" + model_rdm_dist_metric
    if not model_name + '.npy' in os.listdir(model_RDM_path):
        model = rsa_io.load_model(file_path=args.model_root_path + model_file)
        model_RDM_dict[model_name] = rsa.create_rdm(model.values, metric=model_rdm_dist_metric, name=model_name, save_path=model_RDM_path)
    else:
        model_RDM_dict[model_name] = rsa_io.load_rdm(model_RDM_path + model_name)

# every key is time point and every value is a list of corresponding rdms of different subjects
windowed_eeg_rdm_dict = defaultdict(list)

# TODO think about rdm ready later, maybe save each rdm to the corresponding subjects folder
folders = [name for name in os.listdir(args.eeg_root_path) if os.path.isdir(args.eeg_root_path + name) and name.startswith("subj")]
n_subjects = len(folders)


# Keep model performance data e.g kendall tau values
model_performance_data = {}



# For every model, run similarity for each subject
for model_name, model_RDM in model_RDM_dict.items():

    # Keep a list of subject similartiy dfs to merge at the end of subject loop
    subject_similarities = []

    # For all subjects do
    for i, folder in enumerate(folders):
        subj_name = folder[0:6]
        subj_path = args.eeg_root_path + folder + "/action-mats/"

        # windowed eeg dict: time windows as keys and a 3D matrix of size conditions, channels, trials
        windowed_eeg_dict = rsa_io.build_EEG_data(subj_path, args.w_size)

        # traverse each window in windowed_eeg_dict and calculate rdm
        for window, eeg_data in windowed_eeg_dict.items():
            name = subj_name + '_eeg_rdm_' + str(window[0]) + ":" + str(window[1]) + "_" + eeg_rdm_dist_metric
            windowed_eeg_rdm_dict[window].append(rsa.create_rdm(eeg_data, eeg_rdm_dist_metric, name, cv=True))

        # Compare a subject's all time windowed eeg rdms with a model
        subject_similarities.append(rsa.correlate_windowed(windowed_eeg_rdm_dict, subj_name, model_RDM))

    # eegRDM modelRDM similarities for all subjects and time windows for a model
    similarity_df = pd.concat(subject_similarities)

    # Calculate average of all subjects kendall tau for each window
    mean_kendall_per_window = similarity_df[['time_window','kendall_tau']].groupby(["time_window"]).mean()

    # Plot line curve of kendall average values with error bars calculated from similarity graph


