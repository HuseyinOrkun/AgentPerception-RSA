from scipy import io, stats
import numpy as np

model_rdm = io.loadmat('AgentRDM.mat')['AgentRDM']
eeg_rdm = io.loadmat('EEG_RDM.mat')['EEG_RDM']

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