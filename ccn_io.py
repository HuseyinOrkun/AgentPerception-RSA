import os
import scipy.io as sio
import numpy as np
import csv
from numpy import genfromtxt
import pandas as pd

# build_EEG_data takes EEG root path and loads EEG data
# Input: EEG_root_path is the root path to the folder which has all the subjects folders
# each subject folder has 24 mat files e.g. human-wave, robot-wave etc
# Output: agent_action_all_avg: all eeg_data averaged on
# name of folders of subjects


def build_EEG_data(EEG_subject_action_mats_path, time_window_size):


    # get all the .mat files
    subject_action_file_paths = [EEG_subject_action_mats_path + name
                                 for name in os.listdir(EEG_subject_action_mats_path) if name.endswith('.mat')]

    # Dictionary to store each agent action combination data, each key is an agent action combination e.g.
    # human_wave etc, and each value is a list of 2D numpy arrays with shape trial, channel
    agent_action_dict = {}

    time_window_representations = dict()

    for subject_action_file_path in subject_action_file_paths:
        loaded_file = sio.loadmat(subject_action_file_path)

        # subj_agent_action is a subject's eeg data for an action agent combination
        subj_agent_action = np.asarray(loaded_file["eeg_data"])
        input_type = loaded_file["input_type"]
        experiment_type = loaded_file["experiment_type"]
        action = loaded_file["action"]
        agent = loaded_file["agent"]

        # Check if total number of timepoints is divisable by time_window_size
        n_timepts = subj_agent_action.shape[1]
        n_channels = subj_agent_action.shape[0]
        n_trials = subj_agent_action.shape[2]
        if n_timepts % time_window_size != 0:
            raise ValueError('Total number of timepoints is not divisable by given time_window_size')

        for start in range(0, n_timepts, time_window_size):
            end = start + time_window_size
            key = (start, end)  # "(" + str(start) + ", " + str(end) + ")"
            if key not in time_window_representations.keys():
                time_window_representations[key] = [np.average(subj_agent_action[:, start:end,:], axis=1).transpose()]
            else:
                time_window_representations[key].append(np.average(subj_agent_action[:, start:end,:], axis=1).transpose())
    for key, value in time_window_representations.items():
        time_window_representations[key] = np.array(value)

    return time_window_representations


# This function loads a model from storage given the file type and file path
# returns the model as a pandas dataframe. CSV and MAT types are supported for now.
def load_model(file_path):
    extension = os.path.splitext(os.path.basename(file_path))[1]
    model = None
    if extension == '.csv':
        model = pd.read_csv(file_path, index_col=0, skiprows=[0])
    elif extension == '.mat':
        print("Warning this is not yet tested")
        model = sio.loadmat(file_path)['model']
    elif extension == '.np':
        print("Warning this is not yet tested")
        model = sio.loadmat(file_path)['model']

    return model

def load_rdm(filename):
    return np.load(filename + '.npy')


if __name__ == '__main__':
    test_dict = build_EEG_data('/Users/huseyinelmas/Desktop/data/still/')

    for key, val in test_dict.items():
        print(key)
        print(val.shape)
