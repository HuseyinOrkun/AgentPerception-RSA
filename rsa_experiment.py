# Uses functions in other files to do the experiment
from collections import defaultdict

import ccn_io
import rsa
import argparse
import os
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

args = parser.parse_args()
rdm_dist_metric = 'euclidean'

# Create modelRDMs folder in models if not exists
model_RDM_path = "save_path/modelRDMs/"
if not os.path.exists(model_RDM_path):
    os.makedirs(model_RDM_path)

# Create eegRDMs folder in models if not exists
eeg_RDM_path = "save_path/eegRDMs/"
if not os.path.exists(args.eeg_root_path):
    os.makedirs(args.eeg_root_path)

rdm_ready = False
for start, end in range(0,400,args.w_size):
    name = 'eeg_rdm_' + str(start) + ":" + str(end) + "_" + rdm_dist_metric + ".npy"
    if not name in os.listdir(eeg_RDM_path):
        rdm_ready = False

model_RDM_dict = {}
for model_file in os.listdir(args.model_root_path):
    model_name = os.path.splitext(model_file)[0] + "_" + rdm_dist_metric
    if not model_name + '.npy' in os.listdir(model_RDM_path):
        model = ccn_io.load_model(file_path=args.model_root_path + model_file)
        model_RDM_dict[model_name] = rsa.create_rdm(model.values, metric=rdm_dist_metric, name=model_name, save_path=model_RDM_path)
    else:
        model_RDM_dict[model_name] = ccn_io.load_rdm(model_RDM_path + model_name)

# every key is time point and every value is a list of corresponding rdms of different subjects
windowed_eeg_rdm_dict = defaultdict(list)

# TODO think about rdm ready later, maybe save each rdm to the corresponding subjects folder
folders = [name for name in os.listdir(args.eeg_root_path) if os.path.isdir(args.eeg_root_path + name) and name.startswith("subj")]
n_subjects = len(folders)

# For all subjects do
for i, folder in enumerate(folders):
    subj_name = folder[0:6]
    subj_path = args.eeg_root_path + folder + "/action-mats/"

    # windowed eeg dict: time windows as keys and a 3D matrix of size conditions, trial, channels
    windowed_eeg_dict = ccn_io.build_EEG_data(subj_path, args.w_size)

    # traverse each window in windowed_eeg_dict and calculate rdm
    for window, eeg_data in windowed_eeg_dict:
        name = subj_name + '_eeg_rdm_' + str(window[0]) + ":" + str(window[1]) + "_" + rdm_dist_metric
        windowed_eeg_rdm_dict[window].append(rsa.create_rdm(eeg_data, rdm_dist_metric, name))

    # Compare each model rdm with every subjects rdm and take the mean of all kendalls' tau values.
    # What can be the statistical test here?
    # For each model in the model path run create rdm if that model rdm is not created

    for model_name, model_RDM in model_RDM_dict.items():
        time_window_dist_df = rsa.correlate_windowed(windowed_eeg_rdm_dict, subj_name, model_RDM)



