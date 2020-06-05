import os
from collections import defaultdict

import h5py
import numpy as np
import pandas as pd
import scipy.io as sio


# Input: EEG_root_path is the root path to the folder which has all the subjects folders.
# Each subject folder has 24 mat files e.g. human-wave, robot-wave etc
# Output: time_window_representations: Keys are time windows, Each value in the time_window_representations
# is a list of 3D ndarrays with size (n_conditions, n_trials, n_channels)

def build_eeg_data(subject_action_mats_path, time_window_size, subj_name, experiment_type, stimuli_type):
    agent_action_list = [
        "robot-drink", "robot-grasp", "robot-handwave", "robot-talk", "robot-nudge",
        "robot-paper", "robot-turn", "robot-wipe", "android-drink", "android-grasp", "android-handwave",
        "android-talk", "android-nudge", "android-paper", "android-turn", "android-wipe", "human-drink",
        "human-grasp", "human-handwave", "human-talk", "human-nudge", "human-paper", "human-turn", "human-wipe"]

    # get all the .mat files
    condition_file_paths = [subject_action_mats_path + subj_name + "_" + agent_action
                            for agent_action in agent_action_list]

    time_window_representations = defaultdict(list)

    # condition action file is the mat file of a condition of a subject and condition_file_paths is a list of condition
    # eeg mats of all conditions of a particular subject
    for i, condition_file_path in enumerate(condition_file_paths):
        loaded_file = sio.loadmat(condition_file_path)

        # subj_agent_action is a subject's eeg data for an action agent combination
        subj_agent_action = np.asarray(loaded_file["eeg_data"])
        loaded_stimmuli_type = loaded_file["input_type"][0]
        loaded_experiment_type = loaded_file["experiment_type"][0]
        action = loaded_file["action"][0]
        agent = loaded_file["agent"][0]

        #if (loaded_experiment_type.lower() != experiment_type.lower()
        #        or loaded_stimmuli_type.lower() != stimuli_type.lower()):
        #    raise Exception("Experiment type or stimuli type of loaded file does not match arguments given to python")

        # Check if total number of timepoints is divisable by time_window_size
        n_timepts = subj_agent_action.shape[1]
        n_channels = subj_agent_action.shape[0]
        n_trials = subj_agent_action.shape[2]
        if n_timepts % time_window_size != 0:
            raise ValueError('Total number of timepoints is not divisable by given time_window_size')

        for start in range(0, n_timepts, time_window_size):
            end = start + time_window_size

            # Each value in the time_window_representations is a list of vector of channels (specifying averaged trial
            # eeg responses for a condition) with length n_conditions each element
            # is (n_channels) which is te eeg data of a condition  in a time window given by the key.
            time_window_representations[(start, end)].append(
                np.mean(np.mean(subj_agent_action[:, start:end, :], axis=1), axis=1))

    for time_window, condition_eeg_data_list in time_window_representations.items():
        time_window_representations[time_window] = np.asarray(condition_eeg_data_list)
    return time_window_representations


# This function loads a model from storage given the file type and file path
# returns the model as a pandas dataframe. CSV and MAT types are supported for now.
def load_model(file_path):
    extension = os.path.splitext(os.path.basename(file_path))[1]
    model = None
    if extension == '.csv':
        model = pd.read_csv(file_path, index_col=0, skiprows=[0]).values
    elif extension == '.mat':
        model = sio.loadmat(file_path)['data']
    elif extension == '.np':
        print("Warning this is not yet tested")
        model = sio.loadmat(file_path)['model']
    return model


def load_rdm(filename):
    return np.load(filename + '.npy')


# Given the dictionary of eeg_rdms of all subject, save numpy files in a h5df format
def save_to_hdf5(electrode_region, windowed_eeg_rdm_dict, distance_metric, w_size,
                 name, path, experiment_type=None,stimulus_type=None):
    with h5py.File(path + name + ".hdf5", "w") as f:
        f.attrs["electrode_region"] = electrode_region
        f.attrs["w_size"] = w_size
        f.attrs["distance_metric"] = distance_metric
        f.attrs["experiment_type"] = experiment_type
        f.attrs["stimulus_type"] = stimulus_type
        for time_window, eeg_rdm_np in windowed_eeg_rdm_dict.items():
            tm_grp = f.create_group(str(time_window))
            tm_grp.create_dataset("rdm", data=eeg_rdm_np)


# Given path of hdf5 file, returns the windowed eeg_rdm_dict and experiment parameters
def load_from_hdf5(name, path,experiment_type,stimuli_type):
    windowed_eeg_rdm_dict = {}
    with h5py.File(path + name + ".hdf5", "r") as f:
        attributes = list(f.attrs.items())
        if (experiment_type.lower() != attributes["experiment_type"].lower()
                or stimuli_type.lower() != attributes["stimuli"].lower()):
            raise Exception("Experiment type or stimuli type of loaded file does not match arguments given to python")
        print("Dataset attributes of " + name, attributes)
        for key in list(f.keys()):
            windowed_eeg_rdm_dict[tuple(map(int, key[1:-1].split(',')))] = np.asarray(f[key]["rdm"])
        return windowed_eeg_rdm_dict, attributes


if __name__ == '__main__':
    test_dict = build_eeg_data('/Users/huseyinelmas/Desktop/data/still/')
