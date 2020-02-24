# Uses functions in other files to do the experiment
from collections import defaultdict
import rsa_io
import rsa
import rsa_visualization as vis
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import pickle

mpl.use('Agg')

parser = argparse.ArgumentParser()
parser.add_argument('eeg_root_path', type=str,
                    help='Path to save the results of the experiment')
parser.add_argument('model_root_path', type=str,
                    help='directory of models')
parser.add_argument('w_size', metavar='window size', type=int,
                    help='The window size')
parser.add_argument('save_path', metavar='output path', type=str,
                    help='Path to save the results of the experiment')
parser.add_argument("eeg_rdm_dist_metric",type=str,help="Distance metric to use to create eeg rdms")
parser.add_argument("model_rdm_dist_metric",type=str,help="Distance metric to use to create model rdms")

args = parser.parse_args()

# Apply Bonferroni correction?
correct = True

# Apha value for statistical analysis
alpha = 0.001
subject_folders = [name for name in os.listdir(args.eeg_root_path) if
                   os.path.isdir(args.eeg_root_path + name) and name.startswith("subj")]
n_subjects = len(subject_folders)


#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows',None)
#pd.set_option('display.width', None)

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

    if not model_file.startswith("."):
        metric = args.model_rdm_dist_metric if 'gabor' not in model_file and 'optic' not in model_file else 'correlation'

        model_name = os.path.splitext(model_file)[0] + "_" + metric
        if not model_name + '.npy' in os.listdir(model_RDM_path):
            model = rsa_io.load_model(file_path=args.model_root_path + model_file)
            model_RDM_dict[model_name] = rsa.create_rdm(model, metric=metric, name=model_name,
                                                        save_path=model_RDM_path, model=True)
        else:
            print("Model RDM for {0} with distance metric: {1} was found in {2},"
                  " loading already created Model RDM ".format(model_name, args.model_rdm_dist_metric, model_RDM_path))
            model_RDM_dict[model_name] = rsa_io.load_rdm(model_RDM_path + model_name)

# Make a list of brain regions and do the analysis, also add whole_brain i didn't have those files
electrode_regions = ['central', 'frontal', 'parietal', 'temporal', 'whole_brain']
#electrode_regions = ['occipital']
for electrode_region in electrode_regions:

    # Check if eeg_rdm exists in eeg_rdm_path, meaning that experiment is already done with this w_size and eeg_rdm_distance
    windowed_eeg_rdm_dict = None

    # create the name of eeg rdm file
    eeg_rdm_fname = "eeg_rdm_" + electrode_region + "_" + str(args.w_size) + "_" + args.eeg_rdm_dist_metric
    if eeg_rdm_fname + ".hdf5" in os.listdir(eeg_rdm_path):
        print("EEG RDMs with parameters with window size: {0} and distance: {1} is already created, loading from {2}".format(str(args.w_size) ,  args.eeg_rdm_dist_metric, eeg_rdm_path + eeg_rdm_fname))
        windowed_eeg_rdm_dict, attributes = rsa_io.load_from_hdf5(eeg_rdm_fname, eeg_rdm_path)
    else:
        windowed_eeg_rdm_dict = defaultdict(list)

        # For all subjects do
        for i, subject_folder in enumerate(subject_folders):
            subj_name = subject_folder[0:9]
            subj_path = args.eeg_root_path + subject_folder + "/" + electrode_region + "/action-mats/"

            # Keys are time windows, Each value in the time_window_representations is a 3D ndarray
            # with size (n_conditions, n_trials, n_channels). Since n_trials are not same for each condition,
            # the missing values are filled with NaN.
            time_window_representations = rsa_io.build_eeg_data(subj_path, args.w_size, subj_name)

            # traverse each window in time_window_representations and calculate rdm
            for window, eeg_data in time_window_representations.items():
                eeg_rdm_name = subj_name + '_eeg_rdm_' + str(window[0]) + \
                               ":" + str(window[1]) + "_" + args.eeg_rdm_dist_metric
                windowed_eeg_rdm_dict[window].append(rsa.create_rdm(eeg_data, args.eeg_rdm_dist_metric, eeg_rdm_name))

        for window, eeg_rdm_list in windowed_eeg_rdm_dict.items():
            windowed_eeg_rdm_dict[window] = np.vstack(eeg_rdm_list)

        # Save eeg rdms to hdf5 file
        rsa_io.save_to_hdf5(electrode_region, windowed_eeg_rdm_dict, args.eeg_rdm_dist_metric, args.w_size, eeg_rdm_fname, eeg_rdm_path)


    # Compare model and eeg rdms append to a list
    rdm_statistics_list = []
    for model_name, model_RDM in model_RDM_dict.items():
        dist_per_time_window = []
        for time_window, EEG_RDM_list in windowed_eeg_rdm_dict.items():
            kendall_tau, kendall_p_value = rsa.correlate_models(model_RDM, np.mean(EEG_RDM_list, axis=0))
            rdm_statistics_list.append([model_name, time_window, kendall_tau, kendall_p_value])

    pd.options.display.width = 100
    rdm_statistics_df = pd.DataFrame(rdm_statistics_list,
                                     columns=['Model name', 'Time window', 'Kendall tau', 'Kendall p-value'])
    pos_corr_rdms =  rdm_statistics_df[rdm_statistics_df["Kendall tau"]>0]

    n_test = 1
    if correct:
        n_test = 400
    significant_rdms = pos_corr_rdms[pos_corr_rdms["Kendall p-value"]/2 <= (alpha/n_test)]
    print(significant_rdms.sort_values(by="Kendall tau", ascending=False))

    # Calculate noise ceiling
    #upper_ceiling_list = []
    #lower_ceiling_list = []
    #for time_window, EEG_RDM_list in windowed_eeg_rdm_dict.items():
    #    lower_ceiling, upper_ceiling = rsa.calculate_noise_ceiling(EEG_RDM_list)
    #    lower_ceiling_list.append(lower_ceiling)
    #    upper_ceiling_list.append(upper_ceiling)


    # Time winodws are sorted alphabetically in hdf5
    # Sort by time windows to sort numerically
    rdm_statistics_df = rdm_statistics_df.sort_values(by="Time window")

    # Saving the objects:
    with open(args.save_path+electrode_region+'_results.pkl', 'wb') as f:
        pickle.dump([rdm_statistics_df, significant_rdms,
                         args.eeg_rdm_dist_metric, args.model_rdm_dist_metric,
                         correct, alpha, electrode_region], f)

    #vis.visualize_matplotlib(rdm_statistics_df, significant_rdms, args.save_path,
    #                     args.eeg_rdm_dist_metric, args.model_rdm_dist_metric,
    #                     correct, alpha, electrode_region)


