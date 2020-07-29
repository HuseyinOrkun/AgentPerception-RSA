import numpy as np
import pandas as pd
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

    # VIF calculation
    vif = pd.DataFrame()
    vif["VIF Factor"] = [variance_inflation_factor(regressor_matrix, i) for i in range(regressor_matrix.shape[1])]
    vif["features"] = models

    # Regression results as a list, will be converted to df
    regression_results_list = []

    # Column names for the resulting df
    column_names = ['experiment_type', 'stimuli_type', 'electrode_region', 'model', 'time_window', 'beta_value',
                    't_value', 'p_value', 'lower_conf_interval', 'upper_conf_interval']

    # For each time window and, get the mean rdm across subjects, use OLS and get each beta coefficient and
    # statistic values
    for time_wind, eeg_rdm in windowed_eeg_rdm_dict.items():
        results = OLS(np.mean(eeg_rdm, 0), regressor_matrix).fit()
        for i, model in enumerate(models):
            temp = [experiment_type, stimuli_type, electrode_region, model, time_wind]
            temp.extend([results.params[i], results.tvalues[i], results.pvalues[i]])
            temp.extend(results.conf_int().tolist()[i])
            regression_results_list.append(temp)

    return vif, regression_results_list
