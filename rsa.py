from scipy.spatial.distance import pdist,squareform
import scipy.io as sio
import matplotlib.pyplot as plt
import numpy
import seaborn as sns

# Input: X ndarray, An m by n array of m original observations in an n-dimensional space.
# metric: A difference metric to compare activation patterns from {'hamming', 'mahalanobis'}
# TODO: to add more distances, add args and kwargs to signature.
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
    plt.savefig(name+'RDM.png')
    plt.show()
    return RDM

if __name__ == '__main__':
    robot_drink = [1,0,0]
    robot_grasp = [1,0,0]
    robot_handwave = [1,0,0]
    robot_talk = [1,0,0]
    robot_nudge = [1,0,0]
    robot_paper = [1,0,0]
    robot_turn = [1,0,0]
    robot_wipe = [1,0,0,]

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

    print(type(create_rdm(stimuli, 'hamming', 'Agent')))