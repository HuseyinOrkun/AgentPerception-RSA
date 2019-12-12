# Uses functions in other files to do the experiment
from collections import defaultdict

import rsa_io
import rsa
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

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
#rdm_statistics_df = pd.DataFrame(columns=['Subject name', 'Model name', 'Time window', 'Kendall tau', 'Kendall p-value'])

rdm_statistics_list =[]

# For all subjects do
for i, folder in enumerate(folders):
    subj_name = folder[0:6]
    subj_path = args.eeg_root_path + folder + "/action-mats/"

    # Keys are windows.
    # Each value in the time_window_representations is a 3D ndarray
    # with size (n_conditions, n_trials, n_channels). Since n_trials
    # are not same for each condition, the missing values are filled
    # with NaN.
    time_window_representations = rsa_io.build_EEG_data(subj_path, args.w_size)

    # traverse each window in time_window_representations and calculate rdm
    for window, eeg_data in time_window_representations.items():

        name = subj_name + '_eeg_rdm_' + str(window[0]) + ":" + str(window[1]) + "_" + eeg_rdm_dist_metric
        windowed_eeg_rdm_dict[window].append(rsa.create_rdm(eeg_data, eeg_rdm_dist_metric, name, cv=True))

    # Compare each model rdm with every subjects rdm and take the mean of all kendalls' tau values.
    # What can be the statistical test here?
    # For each model in the model path run create rdm if that model rdm is not created

    # TODO edit the comments
    # Correlate a list of EEG RDM's with a model RDM, find the maximal correlation and report
    # Will use sena's function to correlate an EEG RDM and a model RDM
    # Input: A dictionary of EEG RDMs as time windows as keys and RDMs as values and a model RDM
    # Output: Returns a pandas Series that contains the time window and
    # biggest distance and a pandas dataframe containing all distances

    for model_name, model_RDM in model_RDM_dict.items():
        dist_per_time_window = []
        for time_window, EEG_RDM_list in windowed_eeg_rdm_dict.items():

            kendall_tau, kendall_p_value = rsa.correlate_models(model_RDM, EEG_RDM_list[i])
            rdm_statistics_list.append([subj_name, model_name, time_window, kendall_tau, kendall_p_value])


upper_ceiling_list = []
lower_ceiling_list = []
for time_window, EEG_RDM_list in windowed_eeg_rdm_dict.items():
    lower_ceiling, upper_ceiling = rsa.calculateNoiseCeiling(EEG_RDM_list)
    lower_ceiling_list.append(lower_ceiling)
    upper_ceiling_list.append(upper_ceiling_list)

rdm_statistics_df = pd.DataFrame(rdm_statistics_list, columns=['Subject name', 'Model name', 'Time window', 'Kendall tau', 'Kendall p-value'])

subj_avg_df = rdm_statistics_df.groupby(["Time window", "Model name"]).mean().reset_index()
ind = subj_avg_df.groupby('Model name')['Kendall tau'].idxmax()
summary = subj_avg_df.loc[ind]
print(summary)

pivoted = subj_avg_df.pivot(index='Time window', columns='Model name', values='Kendall tau')
print(pivoted)
pivoted.plot()
plt.show()



print('end')






