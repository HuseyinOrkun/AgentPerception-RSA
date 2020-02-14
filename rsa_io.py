import os
import scipy.io as sio
import numpy as np
import pandas as pd
import h5py
from collections import defaultdict


# Input: EEG_root_path is the root path to the folder which has all the subjects folders.
# Each subject folder has 24 mat files e.g. human-wave, robot-wave etc
# Output: time_window_representations: Keys are time windows, Each value in the time_window_representations
# is a list of 3D ndarrays with size (n_conditions, n_trials, n_channels)

def build_eeg_data(subject_action_mats_path, time_window_size, subj_name):

    agent_action_list = [
        "robot-drink","robot-grasp","robot-handwave","robot-talk","robot-nudge",
        "robot-paper","robot-turn","robot-wipe","android-drink","android-grasp","android-handwave",
        "android-talk","android-nudge","android-paper","android-turn","android-wipe","human-drink",
        "human-grasp","human-handwave","human-talk","human-nudge","human-paper","human-turn","human-wipe"]

    # get all the .mat files
    condition_file_paths = [subject_action_mats_path + subj_name + "_" + agent_action
                                 for agent_action in agent_action_list]

    time_window_representations = defaultdict(list)
    max_n_trials = 0
    n_conditions = len(condition_file_paths)

    # condition action file is the mat file of a condition of a subject and condition_file_paths is a list of condition
    # eeg mats of all conditions of a particular subject
    for condition_file_path in condition_file_paths:
        loaded_file = sio.loadmat(condition_file_path)

        # subj_agent_action is a subject's eeg data for an action agent combination
        subj_agent_action = np.asarray(loaded_file["eeg_data"])
        input_type = loaded_file["input_type"]
        experiment_type = loaded_file["experiment_type"]
        action = loaded_file["action"]
        agent = loaded_file["agent"]
        print("Input Type: {0}, Experiment type: {1}, Action Type: {2}, Agent Type: {3}".format(input_type, experiment_type, agent, action))

        # Check if total number of timepoints is divisable by time_window_size
        n_timepts = subj_agent_action.shape[1]
        n_channels = subj_agent_action.shape[0]
        n_trials = subj_agent_action.shape[2]
        if n_trials > max_n_trials:
            max_n_trials = n_trials
        if n_timepts % time_window_size != 0:
            raise ValueError('Total number of timepoints is not divisable by given time_window_size')

        for start in range(0, n_timepts, time_window_size):
            end = start + time_window_size
            key = (start, end)
            
            # Each value in the time_window_representations is a list of 3D ndarrays
            # with length n_conditions each element is (n_trials, n_channels).
            time_window_representations[key].append(np.average(subj_agent_action[:, start:end, :], axis=1).transpose())

    # Since n_trials are not same for each condition, the missing values are filled
    # with NaN in the code below. Also, now each value in time_window_representations is a 3D array 
    # with shape (n_conditions, max_n_trials, n_channels)
    for time_window, condition_eeg_data_list in time_window_representations.items():
        b = np.full((n_conditions, max_n_trials, n_channels), np.nan)
        for condition_no, trial_eeg_data in enumerate(condition_eeg_data_list):
            n_trials = trial_eeg_data.shape[0]
            n_channels = trial_eeg_data.shape[1]
            b[condition_no, :n_trials, :n_channels] = trial_eeg_data
        time_window_representations[time_window] = b
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
        model = sio.loadmat(file_path)
    elif extension == '.np':
        print("Warning this is not yet tested")
        model = sio.loadmat(file_path)['model']

    return model


def load_rdm(filename):
    return np.load(filename + '.npy')


# Given the dictionary of eeg_rdms of all subject, save numpy files in a h5df format
def save_to_hdf5(electrode_region, windowed_eeg_rdm_dict, distance_metric, w_size, name, path):
    with h5py.File(path + name + ".hdf5", "w") as f:
        f.attrs["electrode_region"] = electrode_region
        f.attrs["w_size"] = w_size
        f.attrs["distance_metric"] = distance_metric
        for time_window, eeg_rdm_np in windowed_eeg_rdm_dict.items():
            tm_grp=f.create_group(str(time_window))
            tm_grp.create_dataset("rdm", data=eeg_rdm_np)


# Given path of hdf5 file, returns the windowed eeg_rdm_dict and experiment parameters
def load_from_hdf5(name, path):
    windowed_eeg_rdm_dict = {}
    with h5py.File(path + name + ".hdf5", "r") as f:
        attributes = list(f.attrs.items())
        print("Dataset attributes of " + name, attributes)
        for key in list(f.keys()):
              windowed_eeg_rdm_dict[tuple(map(int, key[1:-1].split(',')))] = np.asarray(f[key]["rdm"])
        return windowed_eeg_rdm_dict, attributes

if __name__ == '__main__':
    test_dict = build_eeg_data('/Users/huseyinelmas/Desktop/data/still/')

    for key, val in test_dict.items():
        print(key)
        print(val.shape)
