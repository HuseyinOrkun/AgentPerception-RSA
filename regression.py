import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from statsmodels.stats.outliers_influence import variance_inflation_factor


# Input: windowed_eeg_rdm_dict, model_rdm_dict: dictionary (nmodels keys, ndarray (276) values)
# Output: VIF dataframe and result dataframe. VIF dataframe contains VIF values for each regressor
# result_list is a list containing in each row experiment_type, stimuli_type, electrode_region model,
# time_windowbeta_coef, tvalue, pvalue, lower_conf_interval, upper_conf_interval for each paramter estimate
# Will be turned to dataframe in rsa_main.py
def regression(windowed_eeg_rdm_dict, model_rdm_dict, experiment_type, stimuli_type, electrode_region):

    # get the rdms as a list and get their names
    model_rdms = list(model_rdm_dict.values())
    models = list(model_rdm_dict.keys())

    # Make the list of model rdms into one model regressor matrix (nmodelsx276)
    regressor_matrix = np.column_stack(model_rdms)
    # Regression results as a list, will be converted to df
    regression_results_list = []

    # For each time window and, get the mean rdm across subjects, use OLS and get each beta coefficient and
    # statistic values
    for time_wind, eeg_rdm in windowed_eeg_rdm_dict.items():
        results = OLS(np.mean(eeg_rdm, 0), regressor_matrix).fit()
        for i, model in enumerate(models):
            temp = [experiment_type, stimuli_type, electrode_region, model, time_wind[0]]
            temp.extend([results.params[i], results.tvalues[i], results.pvalues[i]])
            temp.extend(results.conf_int().tolist()[i])
            regression_results_list.append(temp)

    return regression_results_list


def vif_analysis(model_rdm_dict, save_path, thresh=5):
    model_rdms = list(model_rdm_dict.values())
    models = ["constant"] + list(model_rdm_dict.keys())
    regressor_matrix = np.column_stack(model_rdms)

    # VIF calculation
    dropped = True
    while dropped:
        dropped = False
        # Make the list of model rdms into one model regressor matrix (nmodelsx276)
        vif = pd.DataFrame()
        regressor_matrix = sm.add_constant(regressor_matrix)
        vif["VIF Factor"] = [variance_inflation_factor(regressor_matrix, i) for i in range(regressor_matrix.shape[1])]
        vif["model_name"] = models

        maxloc = vif['VIF Factor'].idxmax()
        if vif['VIF Factor'].max() > thresh:
            print('dropping \'' + vif.loc[maxloc].model_name +
                  '\' at index: ' + str(maxloc))
            print(vif)
            models.remove(vif.loc[maxloc].model_name)
            regressor_matrix = np.delete(regressor_matrix, maxloc, 1)

            dropped = True
    print('Remaining variables:')
    print(models)
    vif.to_csv(save_path + "_VIF_Results.csv")

    return models
