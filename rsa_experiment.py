# Uses functions in other files to do the experiment
import ccn_io
import rsa
import argparse
import os

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

rdm_ready = True
for start, end in range(0,400,args.w_size):
    name = 'eeg_rdm_' + str(start) + ":" + str(end) + "_" + rdm_dist_metric + ".npy"
    if not name in os.listdir(eeg_RDM_path):
        rdm_ready = False

# every item from this dictionary will be input to rsa.create_rdm(), results will be stored in another dictionary
# With the same keys
windowed_eeg_rdm_dict = {}

if rdm_ready:
    for rdm_file_name in os.listdir(eeg_RDM_path):
        window = rdm_file_name.split("_")[2].strip('()').split(":")
        windowed_eeg_rdm_dict[(int(window[0]), int(window[1]))] = ccn_io.load_rdm(rdm_file_name)
else:
    agent_action_dict = ccn_io.build_EEG_data(args.eeg_root_path)

    # Function from sena, this will create a dictionary which has
    # time_window: EEG timed agent_action x (time_window*channel)
    # every value is an input to create RDM function.
    windowed_eeg_dict = ccn_io.construct_time_window_representations(agent_action_dict, args.w_size)

    # traverse each window in windowed_eeg_dict if the rdm of that window is
    for window, eeg_data in windowed_eeg_dict:
        name = 'eeg_rdm_' + str(window[0]) + ":" + str(window[1]) +"_" + rdm_dist_metric
        if not name + '.npy' in os.listdir(eeg_RDM_path):
            windowed_eeg_rdm_dict[window] = rsa.create_rdm(eeg_data, rdm_dist_metric, name, eeg_RDM_path)
        else:
            windowed_eeg_rdm_dict[window] = ccn_io.load_rdm(eeg_RDM_path + name)


# For each model in the model path run create rdm if that model rdm is not created
for model_file in os.listdir(args.model_root_path):
    model_name = os.path.splitext(model_file)[0] + "_" + rdm_dist_metric
    if not model_name + '.npy' in os.listdir(model_RDM_path):
        model = ccn_io.load_model(file_path=args.model_root_path + model_file)
        model_RDM = rsa.create_rdm(model.values, metric=rdm_dist_metric, name=model_name, save_path=model_RDM_path)
    else:
        model_RDM = ccn_io.load_rdm(model_RDM_path + model_name)

    most_similar, time_window_dist_df = rsa.find_maximal_correlation(windowed_eeg_rdm_dict, model_RDM)
    print("For model:\n", model_name, "most similar eeg window\n  " + most_similar)
    print("Model and EEG data similarity graph \n")
    fig = time_window_dist_df.plot().get_figure()

    # Save fig to savepath
    fig.savefig(args.save_path + model_name + '-Similarity Plot.png')

