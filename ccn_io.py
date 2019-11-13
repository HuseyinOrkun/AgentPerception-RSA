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


def build_EEG_data(EEG_root_path):
    # name of folders of subjects
    folders = [name for name in os.listdir(EEG_root_path) if os.path.isdir(EEG_root_path + name)]

    # get first 6 characters - ex: 'subj02'
    subjList = [name[0:6] for name in folders]

    dataFileList = []
    for folder in folders:

        # create the file path inside a sıbject's file
        file_pth = EEG_root_path + folder + '/action-mats/'

        # get all the .mat files
        files = [name for name in os.listdir(file_pth) if name.endswith('.mat')]

        subjFileList = []
        # Create a list of mat files for each subject
        for file in files:
            subjFileList.append(file_pth + file)
        if subjFileList:
            dataFileList.append(subjFileList)


    # Dictionary to store each agent action combination data, each key is an agent action combination e.g.
    # human_wave etc, end each value is a 2D numpy array which is average of all trials and subjects for
    # this particular agent action combination.
    agent_action_dict = {}

    # Numpy ndarray to contain all eeg data across all time points per agent action combination concataneted by all
    # Subjects e.g. (channels x time_points x (subject x trial))

    for subjectNo, subjFileList in enumerate(dataFileList):
        if subjFileList:
            for filename in subjFileList:
                loaded_file = sio.loadmat(filename)

                # subj_agent_action is a subject's eeg data for an action agent combination
                subj_agent_action = np.asarray(loaded_file["eeg_data"])
                input_type = loaded_file["input_type"]
                experiment_type = loaded_file["experiment_type"]
                action = loaded_file["action"]
                agent = loaded_file["agent"]


                # If there is no key with the particular agent_action create a list for it, else
                if (agent, action) in agent_action_dict.keys():
                    agent_action_dict[(agent, action)].append(subj_agent_action)
                else:
                    agent_action_dict[(agent, action)] = [subj_agent_action]

    # Traverse agent_action_dict, and for each value concat and average on 3rd dimension
    for agent_action, agent_action_eeg in agent_action_dict.items():

        # Concatanate trial and subjects
        agent_action_concat = np.concatenate(agent_action_eeg, 2)

        # Average on trials and subjects
        agent_action_dict[agent_action] = np.mean(agent_action_concat, 2)

    return agent_action_dict


def construct_time_window_representations(agent_action_dict, time_window_size):
    # Check if total number of timepoints is divisable by time_window_size
    n_timepts = len(next(iter(agent_action_dict.values()))[0])
    if n_timepts % time_window_size != 0:
        raise ValueError('Total number of timepoints is not divisable by given time_window_size')

    time_window_representations = dict()
    for v in agent_action_dict.values():
        key = None
        for start in range(0, n_timepts, time_window_size):
            end = start + time_window_size

            key = (start, end)  # "(" + str(start) + ", " + str(end) + ")"
            if key not in time_window_representations.keys():
                time_window_representations[key] = [v[:, start:end].flatten()]
            else:
                time_window_representations[key].append(v[:, start:end].flatten())
        time_window_representations[key] = np.asarray(time_window_representations[key])

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
