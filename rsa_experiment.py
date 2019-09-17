# Uses functions in other files to do the experiment
import ccn_io
import rsa



# TODO: add arguments like ml experiments
def main():
    eeg_root_path = '/Users/huseyinelmas/Desktop/data/still/' # TODO: take this from the arguments
    time_window = 25  # TODO: take this from the arguments
    agent_action_dict = ccn_io.build_EEG_data(eeg_root_path)

    # Function from sena, this will create a dictionary which has time_window: EEG timed agent_action x time_window channel
    # Meaning that, every value is an input to create RDM function.
    # windowed_eeg_dict = divide_to_windows(agent_action_dict)




