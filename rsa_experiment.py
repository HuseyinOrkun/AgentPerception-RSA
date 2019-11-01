# Uses functions in other files to do the experiment
import ccn_io
import rsa
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('eeg_root_path', type=str,
                    help='Path to save the results of the experiment')
parser.add_argument('model_path', type=str,
                    help='Root path of the model data')
parser.add_argument('w_size', metavar='window size', type=int,
                    help='The window size')
parser.add_argument('save_path', metavar='output path', type=str,
                    help='Path to save the results of the experiment')

args = parser.parse_args()

agent_action_dict = ccn_io.build_EEG_data(args.eeg_root_path)

# Function from sena, this will create a dictionary which has
# time_window: EEG timed agent_action x (time_window*channel)
# Meaning that, every value is an input to create RDM function.
windowed_eeg_dict = ccn_io.construct_time_window_representations(agent_action_dict, args.w_size)

# every item from this dictionary will be input to rsa.create_rdm(), results will be stored in another dictionary
# With the same keys
windowed_eeg_rdm_dict = {}

for window, eeg_data in windowed_eeg_dict:
    name = 'eeg_rdm_' + window
    windowed_eeg_rdm_dict[window] = rsa.create_rdm(eeg_data, 'mahalanobis', name)

# Model RDM will be provided by a function
model = ccn_io.load_model(file_path=args.model_path, file_type='csv')
model_RDM = rsa.create_rdm(model.values, metric='mahalanobis', name='ModelRDM')
most_similar, time_window_dist_df = rsa.find_maximal_correlation(windowed_eeg_rdm_dict, model_RDM)

print("Model and EEG data most similarity information\n  " + most_similar)
print("Model and EEG data similarity graph \n")
fig = time_window_dist_df.plot().get_figure()

# Save fig to savepath
fig.savefig(args.save_path + 'Similarity Plot.png')

