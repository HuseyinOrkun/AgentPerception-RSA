import pickle
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import json
import pandas as pd
import numpy as np
import os
import glob
import os.path
from itertools import product
from plotly.subplots import make_subplots
import  plotly.graph_objs as go
import plotly
from itertools import product


def plot_experiment_stimuli_comparisons(eeg_rdm_df, electrode_region, model_name, save_path):
    # Create subplots (TODO: in order to add Still MF need to change rows columns)
    fig = make_subplots(rows=2, cols=2, shared_yaxes=False,
                        subplot_titles=("Naive: Still vs Video", "Prior: Still vs Video",
                                        "Still: Naive vs Prior", "Video: Naive vs Prior"))

    colors = px.colors.qualitative.Plotly

    variables = eeg_rdm_df.stimulus_type

    variables = ['still', 'video']
    constants = ['naive', 'prior']
    conditions = ["naive still", "naive video", "prior still", "prior video"]
    c_no = 0

    # Plots for Naive still vs Naive video, Prior still vs Prior video
    for col_no, constant in enumerate(constants):
        for variable in variables:
            df_to_plot = eeg_rdm_df[(eeg_rdm_df["model_name"] == model_name)
                                    & (eeg_rdm_df["electrode_region"] == electrode_region)
                                    & (eeg_rdm_df["experiment_type"] == constant)
                                    & (eeg_rdm_df["stimulus_type"] == variable)]
            pos_corr = find_significant_rdms(df_to_plot)["time"].tolist()
            # Plots the kendall tau curve
            fig.add_trace(go.Scatter(x=df_to_plot["time"],
                                     y=df_to_plot["kendall_tau"],
                                     legendgroup=constant + " " + variable,
                                     mode='lines',
                                     name=constant + " " + variable,
                                     line_color=colors[conditions.index(constant + " " + variable)]),
                          row=1, col=col_no + 1)

            # Plotting the significance points in below the curves
            fig.add_trace(go.Scatter(
                mode='markers',
                legendgroup=constant + " " + variable,
                name=constant + " " + variable,
                x=pos_corr,
                y=[-.1 - (c_no * .02) for _ in range(len(pos_corr))],
                marker=dict(size=2, color=colors[conditions.index(constant + " " + variable)]),
                showlegend=False), row=1, col=col_no + 1)

            fig.update_yaxes(range=[-0.2, 0.6])
            fig.update_yaxes(title_text="Kendall-tau", row=1, col=col_no + 1)
            fig.update_xaxes(title_text="Time ms (relative to stimulus onset)", row=1, col=col_no + 1)
            c_no = c_no + 1

    # Plots for Prior Still vs Naive Still, Naive video vs Prior video
    constants = ['still', 'video']
    variables = ['naive', 'prior']
    c_no = 0
    for col_no, constant in enumerate(constants):
        for variable in variables:
            df_to_plot = eeg_rdm_df[(eeg_rdm_df["model_name"] == model_name)
                                    & (eeg_rdm_df["electrode_region"] == electrode_region)
                                    & (eeg_rdm_df["experiment_type"] == variable)
                                    & (eeg_rdm_df["stimulus_type"] == constant)]
            pos_corr = find_significant_rdms(df_to_plot)["time"].tolist()
            # Plotting the kendall tau curve
            fig.add_trace(go.Scatter(x=df_to_plot["time"],
                                     y=df_to_plot["kendall_tau"],
                                     mode='lines',
                                     legendgroup=variable + " " + constant,
                                     name=variable + " " + constant,
                                     line_color=colors[conditions.index(variable + " " + constant)]),
                          row=2, col=col_no + 1)

            # Significance dots plotting
            fig.add_trace(go.Scatter(mode='markers',
                                     legendgroup=variable + " " + constant,
                                     name=variable + " " + constant,
                                     x=pos_corr,
                                     y=[-.1 - (c_no * .02) for _ in range(len(pos_corr))],
                                     marker=dict(size=2, color=colors[conditions.index(variable + " " + constant)]),
                                     showlegend=False), row=2, col=col_no + 1)
            fig.update_yaxes(range=[-0.2, 0.6])
            fig.update_yaxes(title_text="Kendall-tau", row=1, col=col_no + 1)
            c_no = c_no + 1
    fig.update_layout(height=1000, width=1700, title=electrode_region + " " + model_name,
                      xaxis_title="Time ms (relative to stimulus onset)",
                      yaxis_title="Kendall-tau",
                      font=dict(size=18, color="#000000"))
    plotly.offline.plot(fig, filename="RSA_Results/new_plots/" +
                                      electrode_region + "_" + model_name + '_experiment_stimuli_comparison.html',
                        auto_open=False)