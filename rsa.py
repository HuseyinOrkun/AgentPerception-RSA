from scipy.spatial.distance import pdist,squareform
from scipy import io, stats
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy import stats
from sklearn.discriminant_analysis import _cov
from sklearn.model_selection import LeaveOneOut
from itertools import combinations



# Input: X ndarray, An m by n array of m original observations in an n-dimensional space.
# metric: A difference metric to compare activation patterns from {'hamming', 'mahalanobis'}


def create_rdm(X, metric, name, cv=False, save_path=''):

    # Calculate distance between eah row of X
    # Condensed distance matrix RDM. For each i and j (where i < j < m),
    # where m is the number of original observations.
    # The metric dist(u=X[i], v=X[j]) is computed and stored in entry ij of RDM
    if not cv:

        # average on the trial axis ignoring nan values, then calculate distance
        X = np.nanmean(X, axis=1)

        RDM = pdist(X, metric)
        RDM = squareform(RDM)

    elif cv and metric == "mahalanobis":
        RDM = cv_mahalonobis(X)

        #
        # fig, ax = plt.subplots()
        # colorData = io.loadmat('colorData.mat')
        # cmap = np.flipud(colorData['Blues9'])
        # cmap = cmap[1:,:]
        # ax = sns.heatmap(RDM, cmap=cmap.tolist())
        # ax.set_title(name)
        # plt.savefig(save_path+name+'-RDM.png')
    else:
        # RDM = np.full((X.shape[0], X.shape[0]), fill_value=np.nan)
        raise NotImplementedError

    np.save(save_path + name, RDM)

    return RDM


def cv_mahalonobis(X, cv_scheme=LeaveOneOut()):

    # TODO: check if true

    # Get data dimensions
    n_conditions = X.shape[0]
    trial_indices = X.shape[1]
    n_channels = X.shape[2]

    cond_list = np.arange(n_conditions)

    min_n_trials = np.min(np.argwhere(np.isnan(X))[:,1])


    # Divide to train and test using leave one out, do
    RDM_list = []
    for train_indices, test_indices in cv_scheme.split(range(trial_indices)):

        if not np.max(test_indices) > min_n_trials-1:
            # Get data for the current fold
            train_data = X[:, train_indices, :]
            train_data = np.nanmean(train_data, axis=1)

            test_data = X[:, test_indices, :]
            test_data = np.mean(test_data, axis=1)

            not_nan_trial_indices = train_indices[train_indices < min_n_trials]

            # Calculate the cov matrix of the training set
            sigma = np.mean([_cov(X[condition, not_nan_trial_indices,:], shrinkage='auto') for condition in range(n_conditions)],axis=0)

            RDM = np.zeros((n_conditions, n_conditions))

            # for each pair of conditions in n_conditions, create 2 vectors k than do the multiplication
            # multiply c train inverse of cov, test transpose and c transpose
            for comb in combinations(cond_list, 2):

                k = comb[0]
                j = comb[1]
                c = np.zeros(n_conditions)
                c[k] = -1
                c[j] = 1

                RDM[j,k] = RDM[k,j] = c @ train_data @ sigma @ test_data.transpose() @ c.transpose() # as in Walther

            RDM_list.append(RDM)
        # End of if

    RDM = np.mean(RDM_list, axis=0)

    return RDM







  
# Should we really concat upper and lower triangles
# the correlation doubles
def correlate_models(model_rdm, eeg_rdm):

    # upper triangle. k=1 excludes the diagonal elements.
    xu, yu = np.triu_indices_from(model_rdm, k=1)
    # lower triangle
    xl, yl = np.tril_indices_from(model_rdm, k=-1)  # Careful, here the offset is -1

    # combine
    x = np.concatenate((xl, xu))
    y = np.concatenate((yl, yu))
    off_model_rdm = model_rdm[x,y]

    # upper triangle. k=1 excludes the diagonal elements.
    xu, yu = np.triu_indices_from(eeg_rdm, k=1)
    # lower triangle
    xl, yl = np.tril_indices_from(eeg_rdm, k=-1)  # Careful, here the offset is -1

    # combine
    x = np.concatenate((xl, xu))
    y = np.concatenate((yl, yu))
    off_eeg_rdm = eeg_rdm[x,y]

    # Kendall’s tau is a measure of the correspondence between two rankings. Values
    # close to 1 indicate strong agreement, values close to -1 indicate strong disagreement.
    # The two-sided p-value for a hypothesis test whose null hypothesis is an absence of
    # association, i.e. tau = 0.
    kendall_tau, kendall_p_value = stats.kendalltau(off_model_rdm, off_eeg_rdm)
    return kendall_tau, kendall_p_value

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

    stimuli = np.asarray(stimuli)
    model_RDM = create_rdm(stimuli, 'hamming', 'Agent')

    EEG_rand_dict = {}

    # Simulating an EEG rdm list with random RDMs
    for i in range(1,10):
        EEG_rand_dict[str(i)] = (np.random.rand(24, 24))

    # Putting the model RDM to show that it will be returned as most similar
    EEG_rand_dict['11'] = model_RDM

    most_similar, time_window_dist_df = correlate_windowed(EEG_rand_dict, model_RDM)
    print(most_similar)

    print(type(create_rdm(stimuli, 'hamming', 'Agent')))

    # correlate_models test
    model_rdm = io.loadmat('AgentRDM.mat')['AgentRDM']
    try:
        eeg_rdm = io.loadmat('EEG_RDM.mat')['EEG_RDM']
    except:
        eeg_rdm = np.ones(shape=(24, 24))

    print(correlate_models(model_rdm, eeg_rdm))
