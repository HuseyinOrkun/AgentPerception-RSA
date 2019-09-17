from scipy.spatial.distance import pdist,squareform
import scipy.io as sio
import matplotlib.pyplot as plt
import numpy
import seaborn as sns
import pandas as pd


# Input: X ndarray, An m by n array of m original observations in an n-dimensional space.
# metric: A difference metric to compare activation patterns from {'hamming', 'mahalanobis'}
# TODO: to add more distances, add args and kwargs to signature.
# TODO: check pdist for its ability to compare matrices

def create_rdm(X, metric, name):

    # Calculate distance between eah row of X
    # Condensed distance matrix RDM. For each i and j (where i < j < m),
    # where m is the number of original observations.
    # The metric dist(u=X[i], v=X[j]) is computed and stored in entry ij of RDM
    RDM = pdist(X, metric)
    RDM = squareform(RDM)
    numpy.save(name+'RDM', RDM)
    fig, ax = plt.subplots()

    colorData = sio.loadmat('colorData.mat')
    cmap = numpy.flipud(colorData['Blues9'])
    cmap = cmap[1:,:]
    ax = sns.heatmap(RDM, cmap=cmap.tolist())
    plt.savefig(name+'-RDM.png')
    return RDM

# Correlate a list of EEG RDM's with a model RDM, find the maximal correlation and report
# Will use sena's function to correlate an EEG RDM and a model RDM
# Input: A dictionary of EEG RDMs as time windows as keys and RDMs as values and a model RDM
# Output: Returns a pandas Series that contains the time window and
# biggest distance and a pandas dataframe containing all distances


def find_maximal_correlation(EEG_RDM_dict, model_RDM):

    dist_per_time_window = []
    for time_window, EEG_RDM in EEG_RDM_dict.items():

        # TODO change this function to Sena's function (if it is similarity change here accordingly)
        dist = numpy.linalg.norm(EEG_RDM - model_RDM)
        dist_per_time_window.append([time_window,dist])
    time_window_dist_df = pd.DataFrame(dist_per_time_window, columns=['time_window','Distance'])

    # if metric is similarity instead of distance (dissimilarity), change ascending to True
    time_window_dist_df_sorted = time_window_dist_df.sort_values(by='Distance')

    return time_window_dist_df_sorted.iloc[0], time_window_dist_df


if __name__ == '__main__':
    robot_drink = [1,0,0]
    robot_grasp = [1,0,0]
    robot_handwave = [1,0,0]
    robot_talk = [1,0,0]
    robot_nudge = [1,0,0]
    robot_paper = [1,0,0]
    robot_turn = [1,0,0]
    robot_wipe = [1,0,0]

    android_drink = [0,1,0]
    android_grasp = [0,1,0]
    android_handwave = [0,1,0]
    android_talk = [0,1,0]
    android_nudge = [0,1,0]
    android_paper = [0,1,0]
    android_turn = [0,1,0]
    android_wipe = [0,1,0]

    human_drink = [0,0,1]
    human_grasp = [0,0,1]
    human_handwave = [0,0,1]
    human_talk = [0,0,1]
    human_nudge = [0,0,1]
    human_paper = [0,0,1]
    human_turn = [0,0,1]
    human_wipe = [0,0,1]

    stimuli = [robot_drink, robot_grasp, robot_handwave, robot_talk, robot_nudge, robot_paper, robot_turn, robot_wipe,
               android_drink, android_grasp, android_handwave, android_talk, android_nudge, android_paper, android_turn, android_wipe,
               human_drink, human_grasp, human_handwave, human_talk, human_nudge, human_paper, human_turn, human_wipe]

    stimuli = numpy.asarray(stimuli)
    model_RDM = create_rdm(stimuli, 'hamming', 'Agent')

    EEG_rand_dict = {}

    # Simulating an EEG rdm list with random RDMs
    for i in range(1,10):
        EEG_rand_dict[str(i)] = (numpy.random.rand(24, 24))

    # Putting the model RDM to show that it will be returned as most similar
    EEG_rand_dict['11'] = model_RDM

    most_similar, time_window_dist_df = find_maximal_correlation(EEG_rand_dict, model_RDM)
    print(most_similar)
