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
from libs.graph import graph_gauche,graph_droit
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
        print(key)
        all_data[f'{key}'] = data.history(period='max')
    return all_data

@st.cache
def get_data():
    df = pd.read_excel(
        io="supermarkt_sales.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=3,
        usecols="B:R",
        nrows=1000,
    )
    # Add 'hour' column to dataframe
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df

# GET  ALL DATA
df = get_data()
data_default = get_data_default()

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
name_actif = st.sidebar.text_input("Entrez le nom de votre actif, ex:APPLE  ?")
if name_actif:
    st.write("Donnée Financieres de votre Actif ")
    data = get_data_finance(name_actif)
    data = data.sort_values("Date", ascending = False)
    data_filter = data.filter(['Close'])
    last_60_days = data[-60:].values

    st.write(data)
    chart_data = data[['Open','Close','High']].tail(200)
    st.line_chart(chart_data)
#st.sidebar.selectbox('Choississez une entreprise', ['AAPL','MSFT'])

# ---- MAINPAGE ----
st.title(":bar_chart: Dashboard")
st.markdown("##")

############################################################ Header Dashboard ##################################################
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
    st.write(Microsoft)
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