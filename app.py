#--------------------------------------------------------------------------------------------------------------------------------------------------------
# @Email:  fmujani08@gmail.com
# @Email:  mnkou@outlook.fr
# @Project:  Projet: tableau de bord de suivi d'actif en python w/ Streamlit
#--------------------------------------------------------------------------------------------------------------------------------------------------------
import copy
import pandas as pd
from matplotlib.pyplot import axis
import matplotlib.pyplot as plt
import datetime
import plotly.express as px 
import streamlit as st
import yfinance as yf
import numpy as np
import datetime as dt
import seaborn as sns
from indicateurs_techniques.indicateur_tech import AddIndicators
from libs.graph import graph_gauche,graph_droit
import pandas_datareader as pdr
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import plotting
import plotly.express as px
import seaborn as sns
from io import BytesIO
from portefeuille.plot import plot_cum_returns, plot_efficient_frontier_and_max_sharpe
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")

# ---- READ EXCEL ----
@st.cache
def get_data_finance(symbol):
    data = yf.Ticker(symbol)
    actif = data.history(period='max')
    actif = actif.drop(['Dividends','Stock Splits'], axis=1)
    return actif

def get_data_default():
    all_data={}
    dictionaire = {
        'Nasdas':'^IXIC',
        'Natixis':'VNSYX',
        'S&P 500':'^GSPC',
        'Bitcoin':'BTC-EUR',
        'Dow Jones':'^DJI',
        'CAC 40':'^FCHI',
        'Microsoft':'MSFT',
        'APPL':'AAPL',
        'Carrefour':'CA.PA'
    }
    for i, (key, value) in enumerate(dictionaire.items()): # METTRE ENUMERATE PS : regarde stackover flow
        data = yf.Ticker(value)
        all_data[f'{key}'] = data.history(period='max')
    return all_data

# GET  ALL DATA
data_default = get_data_default()

# ---- MAINPAGE ----
st.title(":bar_chart: Dashboard")
st.header("Michelle and Francis Stock Portfolio Optimizer")
st.markdown("##")


tickers_string = st.sidebar.text_input('Entrer les symbols de vos stocks, separer par la virgule, ex. AAPL,MA,FB,MSFT,AMZN,JPM,BA', '').upper()
#print(tickers)
if tickers_string:
    start = datetime.datetime(2018,5,31)
    end = datetime.datetime(2022,5,5)
    tickers = tickers_string.split(',')
    stocks_df = pdr.DataReader(tickers, 'yahoo', start, end)['Adj Close']	
    # Plot Individual Stock Prices
    fig_price = px.line(stocks_df, title='Prix ​​des actions individuelles')
    # Plot Individual Cumulative Returns
    fig_cum_returns = plot_cum_returns(stocks_df, 'Rendements cumulatifs des actions individuelles à partir de 100 $')
    # Calculatge and Plot Correlation Matrix between Stocks
    corr_df = stocks_df.corr().round(2)
    fig_corr = px.imshow(corr_df,title = 'Correlation entre les actifs')

    # Calculate expected returns and sample covariance matrix for portfolio optimization later
    mu = expected_returns.mean_historical_return(stocks_df)
    S = risk_models.sample_cov(stocks_df)

    # Plot efficient frontier curve
    fig = plot_efficient_frontier_and_max_sharpe(mu, S)
    fig_efficient_frontier = BytesIO()
    fig.savefig(fig_efficient_frontier, format="png")

    # Get optimized weights
    ef = EfficientFrontier(mu, S)
    ef.max_sharpe(risk_free_rate=0.02)
    weights = ef.clean_weights()
    expected_annual_return, annual_volatility, sharpe_ratio = ef.portfolio_performance()
    weights_df = pd.DataFrame.from_dict(weights, orient = 'index')
    weights_df.columns = ['weights']
    # Calculate returns of portfolio with optimized weights
    stocks_df['Optimized Portfolio'] = 0
    for ticker, weight in weights.items():
        stocks_df['Optimized Portfolio'] += stocks_df[ticker]*weight

    # Plot Cumulative Returns of Optimized Portfolio
    fig_cum_returns_optimized = plot_cum_returns(stocks_df['Optimized Portfolio'], 'Rendements cumulatifs du portefeuille optimisé à partir de 100 $')
    # Display everything on Streamlit
    st.subheader("Votre portefeuille se compose de {} actifs".format(tickers_string))	
    st.plotly_chart(fig_cum_returns_optimized)

    st.subheader("Pondérations optimisées du portefeuille Max Sharpe")
    st.dataframe(weights_df)

    st.subheader("Performance optimisée du portefeuille Max Sharpe")
    st.image(fig_efficient_frontier)

    st.subheader('Rendement annuel attendu: {}%'.format((expected_annual_return*100).round(2)))
    st.subheader('Volatilité annuelle: {}%'.format((annual_volatility*100).round(2)))
    st.subheader('Ratio de Sharpe: {}'.format(sharpe_ratio.round(2)))

    st.plotly_chart(fig_corr) # fig_corr is not a plotly chart
    st.plotly_chart(fig_price)
    st.plotly_chart(fig_cum_returns)
st.markdown("""---""")
st.markdown("""---""")

############################################################ Header Dashboard for carrefour##################################################
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Prix moyen par Transaction:")
    st.subheader(f"Prix Carrefour: US $ {round(data_default['Carrefour']['Open'].tail()[0])}")
with middle_column:
    st.subheader("GROUPE CARREFOUR")
    #st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Prix moyen par Transaction:")
    st.subheader(f"US $ {round(data_default['Carrefour']['Open'].mean())}")
st.markdown("""---""")
############################################################ End header Dashboard ##################################################


############################################################ CARREFOUR ##########################################################################
Carrefour = AddIndicators(data_default['Carrefour'])
data_Carrefour = Carrefour.sort_values("Date", ascending=False)
data_fliter_carrefour = data_Carrefour.filter(['Close'])
Carrefour_filter = data_fliter_carrefour.iloc[:300]
# GRAPH 1
fig_product_sales = graph_gauche(Carrefour_filter, 'Carrefour','#eb1c00')
# GRAPH 2
all_data_by_date_Carrefour = data_Carrefour.groupby(by=["Date"]).sum()[["Volume"]].tail(10)
fig_hourly_sales = graph_droit(all_data_by_date_Carrefour, 'Carrefour', '#0564ff')
# DISPLAY GRAPH
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)
if st.checkbox('Voir les données financieres'):
    st.write(Carrefour)
st.markdown("""---""")
st.sidebar.text("INDICATEUR TECHNIQUE POUR CARREFOUR")
MACD_C = st.sidebar.checkbox('Moyenne mobile (Carrefour)')
RSI_c = st.sidebar.checkbox('RSI (Carrefour)')
BANDE_BOLINGER_C = st.sidebar.checkbox('Bandes de Bollinger (Carrefour)')
st.sidebar.markdown("""---""")
if st.checkbox("Afficher l'indicateur technique pour Carrefour"):
    if RSI_c and not BANDE_BOLINGER_C and not MACD_C:
        chart_data = data_Carrefour['RSI']
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
    if MACD_C and not BANDE_BOLINGER_C and not RSI_c:
        chart_data = data_Carrefour['MACD']
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
    if BANDE_BOLINGER_C and not RSI_c and not MACD_C:
        chart_data = data_Carrefour[['bb_bbm','bb_bbh','bb_bbl']]
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
    if (BANDE_BOLINGER_C and RSI_c and MACD_C) or (BANDE_BOLINGER_C and MACD_C) or (BANDE_BOLINGER_C and RSI_c) or (MACD_C and RSI_c):
        chart_data = data_Carrefour[['RSI','bb_bbm','bb_bbh','bb_bbl','MACD']]
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
st.markdown("""---""")

##################################################### END CARREFOUR #############################################################################


############################################################ MICROSOFT ##########################################################################
#Action MICROSOFT 
# Get data
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Prix moyen par Transaction:")
    st.subheader(f"Prix Microsoft: US $ {round(data_default['Microsoft']['Open'].tail()[0])}")
with middle_column:
    st.subheader("MICROSOFT")
    #st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Prix moyen par Transaction:")
    st.subheader(f"US $ {round(data_default['Microsoft']['Open'].mean())}")

Microsoft =  AddIndicators(data_default['Microsoft'])
data_Microsoft = Microsoft.sort_values("Date", ascending=False)
data_filter_Microsoft = data_Microsoft.filter(['Close'])
Microsoft_filter = data_filter_Microsoft.iloc[:300]
# GRAPH 1
fig_Microsoft_data = graph_gauche(Microsoft_filter, 'Microsoft','#00eb1c')
# GRAPH 2
all_data_by_date_Microsoft = data_Microsoft.groupby(by=["Date"]).sum()[["Volume"]].tail(10)
fig_Microsoft = graph_droit(all_data_by_date_Microsoft, 'Microsoft', '#ffa005')
# DISPLAY GRAPH
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_Microsoft, use_container_width=True)
right_column.plotly_chart(fig_Microsoft_data, use_container_width=True)
# DATAFRAME CARREFOUR
if st.checkbox('Voir les données financieres Microsoft'):
    st.write(Microsoft.head(100))
st.markdown("""---""")
# INDICATEUR TECHNIQUE
st.sidebar.text("INDICATEUR TECHNIQUE POUR MICROSOFT")
MACD_M = st.sidebar.checkbox('Moyenne mobile (Microsoft)')
RSI_M = st.sidebar.checkbox('RSI (Microsoft)')
BANDE_BOLINGER_M = st.sidebar.checkbox('Bandes de Bollinger (Microsoft)')
st.sidebar.markdown("""---""")

if st.checkbox("Afficher l'indicateur technique pour Microsoft"):
    if RSI_M and not BANDE_BOLINGER_M and not MACD_M:
        chart_data = data_Microsoft['RSI']
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
        st.write("L'indicateur RSI reflète la force relative des mouvements haussiers, en comparaison aux mouvements baissiers.")
    if MACD_M and not BANDE_BOLINGER_M and not RSI_M:
        chart_data = data_Microsoft['MACD']
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
        st.write("Une moyenne mobile est un indicateur qui suit la tendance en se basant sur les prix passés. Comme le nom le dit, elle suit la tendance, ce qui signifie qu'elle monte et descend avec le marché.")
    if BANDE_BOLINGER_M and not RSI_M and not MACD_M:
        chart_data = data_Microsoft[['bb_bbm','bb_bbh','bb_bbl']]
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
    if (BANDE_BOLINGER_M and RSI_M and MACD_M) or (BANDE_BOLINGER_M and MACD_M) or (BANDE_BOLINGER_M and RSI_M) or (MACD_M and RSI_M):
        chart_data = data_Microsoft[['RSI','bb_bbm','bb_bbh','bb_bbl','MACD']]
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
st.markdown("""---""")
##################################################### END MICROSOFT #############################################################################

############################################################ BITCOIN ##########################################################################
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Prix moyen par Transaction:")
    st.subheader(f"Prix Bitcoin: US $ {round(data_default['Bitcoin']['Open'].tail()[0])}")
with middle_column:
    st.subheader("BITCOIN (CRYPTO)")
with right_column:
    st.subheader("Prix moyen par Transaction:")
    st.subheader(f"US $ {round(data_default['Bitcoin']['Open'].mean())}")

#Prix de fermeture de l'action Bitcoin 
Bitcoin = AddIndicators(data_default['Bitcoin'])
data_Bitcoin = Bitcoin.sort_values("Date", ascending = False)
data_filter_Bitcoin = data_Bitcoin.filter(['Close'])
Bitcoin_filter = data_filter_Bitcoin['Close'].iloc[:300]
# GRAPH 1
fig_Bitcoin_data = graph_gauche(Bitcoin_filter, 'Bitcoin',"#ddffea")
# GRAPH 2
all_data_by_date_Bitcoin = data_Bitcoin.groupby(by=["Date"]).sum()[["Volume"]].tail(10)
fig_Bitcoin = graph_droit(all_data_by_date_Bitcoin, 'Bitcoin', '#ff6205')
# DISPLAY GRAPH
left_column_bitcoin, right_column_bitcoin = st.columns(2)
left_column_bitcoin.plotly_chart(fig_Bitcoin, use_container_width=True)
right_column_bitcoin.plotly_chart(fig_Bitcoin_data, use_container_width=True)
# DATAFRAME CARREFOUR
if st.checkbox('Voir les données financieres Bitcoin'):
    st.write(Bitcoin)

st.markdown("""---""")
st.sidebar.text("INDICATEUR TECHNIQUE POUR Bitcoin")
MACD_B = st.sidebar.checkbox('Moyenne mobile (Bitcoin)')
RSI_B = st.sidebar.checkbox('RSI (Bitcoin)')
BANDE_BOLINGER_B = st.sidebar.checkbox('Bandes de Bollinger (Bitcoin)')
st.sidebar.markdown("""---""")
if st.checkbox("Afficher l'indicateur technique pour Bitcoin"):
    if RSI_B and not BANDE_BOLINGER_B and not MACD_B:
        chart_data = data_Carrefour['RSI']
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
        st.write("L'indicateur RSI reflète la force relative des mouvements haussiers, en comparaison aux mouvements baissiers.")
    if MACD_B and not BANDE_BOLINGER_B and not RSI_B:
        chart_data = data_Carrefour['MACD']
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
        st.write("Une moyenne mobile est un indicateur qui suit la tendance en se basant sur les prix passés. Comme le nom le dit, elle suit la tendance, ce qui signifie qu'elle monte et descend avec le marché.")
    if BANDE_BOLINGER_B and not RSI_B and not MACD_B:
        chart_data = data_Carrefour[['bb_bbm','bb_bbh','bb_bbl']]
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
        st.write("es Bandes de Bollinger permettent de mesurer la volatilité d'un marché en fonction des cycles boursiers. C'est l'un des indicateurs les plus utilisés dans la finance des marchés et sur les places boursières du monde.")
    if (BANDE_BOLINGER_B and RSI_B and MACD_B) or (BANDE_BOLINGER_B and MACD_B) or (BANDE_BOLINGER_B and RSI_B) or (MACD_B and RSI_B):
        chart_data = data_Carrefour[['RSI','bb_bbm','bb_bbh','bb_bbl','MACD']]
        chart_data = chart_data.iloc[:300]
        st.line_chart(chart_data)
    
st.markdown("""---""")
##################################################### END Bitcoin #############################################################################

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)