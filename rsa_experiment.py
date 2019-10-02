# Uses functions in other files to do the experiment
import ccn_io
import rsa



# TODO: add arguments like ml experiments e.g save path, root_path, time_window
def main():
    eeg_root_path = '/Users/huseyinelmas/Desktop/data/still/' # TODO: take this from the arguments
    time_window = 25  # TODO: take this from the arguments
    agent_action_dict = ccn_io.build_EEG_data(eeg_root_path)
    save_path = ""
    # Function from sena, this will create a dictionary which has time_window: EEG timed agent_action x (time_window*channel)
    # Meaning that, every value is an input to create RDM function.

    # windowed_eeg_dict = divide_to_windows(agent_action_dict)


    windowed_eeg_rdm_dict = {}
    # every item from this dictionary will be input to rsa.create_rdm(), results will be stored in another dictionary
    # With the same keys
    for window, eeg_data in windowed_eeg_dict:
        name = 'eeg_rdm' + window
        windowed_eeg_rdm_dict[window] = rsa.create_rdm(eeg_data, 'hamming', name)

    # Model RDM will be provided by a function
    # TODO: add model rdm, or load it
    model_RDM = None
    most_similar, time_window_dist_df = rsa.find_maximal_correlation(windowed_eeg_rdm_dict, model_RDM)

    print("Model and EEG data most similarity information\n  " + most_similar)
    print("Model and EEG data similarity graph \n")
    fig = time_window_dist_df.plot().get_figure()

    # Save fig to savepath
    fig.savefig(save_path + name + '.png')

