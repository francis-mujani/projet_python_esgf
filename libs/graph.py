#--------------------------------------------------------------------------------------------------------------------------------------------------------
# @Email:  fmujani08@gmail.com
# @Email:  mnkou@outlook.fr
# @Project:  Projet: tableau de bord de suivi d'actif en python w/ Streamlit
#--------------------------------------------------------------------------------------------------------------------------------------------------------
from matplotlib.pyplot import axis
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px 
import streamlit as st
import yfinance as yf
import numpy as np
import datetime as dt
import seaborn as sns
from indicateurs_techniques.indicateur_tech import AddIndicators



# FONCTION GRAPH 1
def graph_gauche(data, name, color):
    fig_Microsoft_data = None
    if name == "Bitcoin":
        fig_Microsoft_data = px.line(
        data,
        x=data.index,
        y="Close",
        orientation="h",
        title=f"<b>Cours de la cryptomonnaie {name} </b>",
        color_discrete_sequence=[color] * len(data),
        template="plotly_white",
        )
        fig_Microsoft_data.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=(dict(showgrid=False))
        )
    else:
        fig_Microsoft_data = px.line(
        data,
        x=data.index,
        y="Close",
        orientation="h",
        title=f"<b>Cours de l'action {name} </b>",
        color_discrete_sequence=[color] * len(data),
        template="plotly_white",
        )
        fig_Microsoft_data.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=(dict(showgrid=False))
        )
    return fig_Microsoft_data
    
# FONCTION GRAPH 2
def graph_droit(data,name, color):
    fig_Microsoft = px.bar(
    data,
    x=data.index,
    y="Volume",
    title=f"<b>Volume {name} (jour) </b>",
    color_discrete_sequence=[color] * len(data),
    template="plotly_white",
    )
    fig_Microsoft.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    return fig_Microsoft
