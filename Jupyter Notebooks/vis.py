import pickle
import plotly.graph_objects as go
import pandas as pd
import os.path
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import  plotly.graph_objs as go 
import plotly
from statsmodels.sandbox.stats.multicomp import multipletests
import sys
sys.path.append(os.path.abspath('../Python'))
import rsa_io
import rsa


# Set default figure parameters
default_fig_parameters = {
    "inch_width" : 10
    "inch_height" :6
    "dpi" : 600
    "width" : inch_width * dpi
    "height" : inch_height * dpi
}

# path to write figures to
figures_path = '/auto/k2/oelmas/scripts/CCN-RSA/Jupyter Notebooks/AgentPerception_Figures/New-22-03-2022/'

# load results
reg_results, rsa_results = rsa_io.read_results()

# Visualize conditions
rsa_visualization.compare_conditions(reg_results,rsa_results)
