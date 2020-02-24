import matplotlib.pyplot as plt

def visualize_matplotlib(rdm_statistics_df, significant_rdms, save_path,
                         eeg_rdm_dist_metric, model_rdm_dist_metric,
                         correct, alpha, electrode_region):

    models = rdm_statistics_df['Model name'].unique()
    fig, axs = plt.subplots(models.size, figsize=(10, 40))
    fig.suptitle('Correlation across time for different models \n(metric: {0})\n (Bonferroni corrected: {1})\n (Channels: {2})'.format(eeg_rdm_dist_metric, correct, electrode_region), weight='bold')

    for i, model in enumerate(models):
        model_df = rdm_statistics_df.loc[rdm_statistics_df['Model name'] == model]
        t_arr = [2*(t-100) for t, _ in model_df['Time window'].values]

        axs[i].set_title(model)
        # axs[i].fill_between(t_arr, lower_ceiling_list, upper_ceiling_list, color='grey', alpha=.5)


        sig_pts = [sig for sig, _ in
                   significant_rdms.loc[rdm_statistics_df['Model name'] == model]['Time window'].values]
        axs[i].plot(t_arr, model_df['Kendall tau'], marker='.', markeredgecolor='r', markerfacecolor='r',
                    markevery=sig_pts)


    for ax in axs.flat:
        ax.set(xlabel='Time (ms)', ylabel='Kendall tau')
        ax.axvline(x=0, color='black', alpha=0.5, linestyle='--', label='end of baseline period')

        # ax.label_outer()

    fig.tight_layout()
    fig.subplots_adjust(top=0.95)

    fig.savefig(save_path + 'plots/eeg_metric_' + eeg_rdm_dist_metric +
                '_model_metric_' + model_rdm_dist_metric + '_Bonferroni_corrected_{0}_alpha={1}_{2}'.format(correct, alpha, electrode_region) + '.png')


