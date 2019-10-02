import os
import scipy.io as sio
import numpy as np


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
    subjFileList = []
    for folder in folders:

        # create the file path inside a sıbject's file
        file_pth = EEG_root_path + folder + '/'

        # get all the .mat files
        files = [name for name in os.listdir(file_pth) if name.endswith('.mat')]

        # Create a list of mat files for each subject
        for file in files:
            subjFileList.append(file_pth + file)
        if subjFileList:
            dataFileList.append(subjFileList)
        subjFileList = []

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
                index = [i for i, s in enumerate(list(loaded_file.keys())) if 'subj' in s]
                if not index:
                    stimuli_type = list(loaded_file.keys())[-1] + ''
                else:
                    stimuli_type = list(loaded_file.keys())[index[0]]

                # subj_agent_action is a subject's eeg data for an action agent combination
                subj_agent_action = np.asarray(loaded_file[stimuli_type])  # Check its size
                print("Shape of subj_agent_Action: " + str(subj_agent_action.shape)) # For debug purposes, remove later

                # If there is no key with the particular agent_action create a list for it, else
                if stimuli_type in agent_action_dict.keys():
                    agent_action_dict[stimuli_type].append(subj_agent_action)
                else:
                    agent_action_dict[stimuli_type] = []
                    
    # Traverse agent_action_dict, and for each value concat and average on 3rd dimension
    for agent_action, agent_action_eeg in agent_action_dict.items():

        # Concatanate trial and subjects
        agent_action_concat = np.concatenate(agent_action_eeg,2)

        # Average on trials and subjects
        agent_action_dict[agent_action] = np.mean(agent_action_concat,2)

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
            end = start+time_window_size
            key = "(" + str(start) + ", " + str(end) + ")"
            if key not in time_window_representations.keys():
                time_window_representations[key] = [v[:, start:end].flatten()]
            else:
                time_window_representations[key].append(v[:, start:end].flatten())
        time_window_representations[key] = np.asarray(time_window_representations[key])

    return time_window_representations





if __name__ == '__main__':
    test_dict = build_EEG_data('/Users/huseyinelmas/Desktop/data/still/')

    for key, val in test_dict.items():
        print(key)
        print(val.shape)