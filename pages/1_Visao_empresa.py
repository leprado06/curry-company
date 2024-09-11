#Libraries
import pandas as pd
import plotly.express as px
import folium
from datetime import datetime
import streamlit as st
from streamlit_folium import folium_static
from haversine import haversine


def clean_code(df1):
    """
    Esta função tem a responsabilidade de limpar o dataframe    
    Tipos de limpeza:
    1. Remocão dos dados NaN
    2. Mudança do tipo da coluna de dados
    3. Remocão dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    """
    #Limpeza de dados 'NaN'
    df1=df1.loc[df1['Delivery_person_Age'] != 'NaN ',:].copy()
    df1=df1.loc[df1['multiple_deliveries'] != 'NaN ',:].copy()
    df1=df1.loc[df1['Road_traffic_density'] != 'NaN ',:].copy()
    df1=df1.loc[df1['City'] != 'NaN ',:].copy()
    df1=df1.loc[df1['Weatherconditions'] != 'NaN ',:].copy()
    df1=df1.loc[df1['Time_taken(min)'] != 'NaN ',:].copy()
    df1=df1.loc[df1['Festival'] != 'NaN ',:].copy()

    #Conversão de tipos
    df1['Delivery_person_Age']=df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings']=df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date']=pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1['multiple_deliveries']=df1['multiple_deliveries'].astype(int)
    df1['Road_traffic_density']=df1['Road_traffic_density'].astype(str)
    df1['City']=df1['City'].astype(str)
    df1['Weatherconditions']=df1['Weatherconditions'].astype(str)
    df1['Festival']=df1['Festival'].astype(str)

    #Limpeza de texto dentro de uma coluna numérica
    df1['Time_taken(min)']=df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Weatherconditions']=df1['Weatherconditions'].apply(lambda x: x.replace('conditions',''))

    #Limpeza de espaços no final das strings
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Weatherconditions'] = df1.loc[:,'Weatherconditions'].str.lstrip()
    df1['Time_taken(min)']=df1['Time_taken(min)'].astype(int)

    df1=df1.reset_index(drop=True)

    return df1
def order_metric(df1):
    #Order Metric
    cols=['ID','Order_Date']
    pedidos_dia = df1.loc[:,cols].groupby('Order_Date').count().reset_index()
    fig=px.bar(pedidos_dia, x='Order_Date', y='ID',title='Pedidos por dia')
    return fig

def traffic_order_share(df1):
    cols=['ID','Road_traffic_density']
    pedidos_trafego = df1.loc[:,cols].groupby('Road_traffic_density').count().reset_index()
    pedidos_trafego['Percentual'] = round((pedidos_trafego.loc[:,'ID'])/(pedidos_trafego.loc[:,'ID'].sum())     ,2)
    fig=px.pie(pedidos_trafego,names='Road_traffic_density', values='Percentual', title='Pedidos por tipo de tráfego    ')
    return fig   
def traffic_order_city(df1):
    cols=['ID','City','Road_traffic_density']
    pedidos_cidade_trafego = df1.loc[:,cols].groupby(['City','Road_traffic_density']).count().reset_index( )
    fig=px.scatter(pedidos_cidade_trafego,x='City',y='Road_traffic_density',size='ID',title='Pedidos por Cidade e tipo de tráfego')
    return fig

def order_by_week(df1):
    df1['Semana'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID','Semana']
    pedidos_semana = df1.loc[:,cols].groupby('Semana').count().reset_index()
    fig=px.line(pedidos_semana, x ='Semana', y='ID',title='Pedidos por semana')
    return fig

def order_share_by_week(df1):
    cols=['ID','Semana']
    cols2=['Delivery_person_ID','Semana']
    pedidos_semana = df1.loc[:,cols].groupby('Semana').count().reset_index()
    entregadores_semana=df1.loc[:,cols2].groupby('Semana').nunique().reset_index()
    pedidos_entregadores_semana = pd.merge(pedidos_semana,entregadores_semana,how='inner')
    pedidos_entregadores_semana['order_by_delivery'] = pedidos_entregadores_semana['ID']/pedidos_entregadores_semana['Delivery_person_ID']
    fig=px.line(pedidos_entregadores_semana, x ='Semana', y='order_by_delivery',title='Pedidos por semana por entregador')
    return fig
def country_maps(df1):
    cols=['Road_traffic_density','City','Delivery_location_latitude','Delivery_location_longitude']
    df1_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).median().reset_index()
    map_= folium.Map()
    for index, location_info in df1_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']]).add_to(map_)

    folium_static(map_,width=1024,height=600)


df = pd.read_csv("/train.csv")

df1 = clean_code(df)

#BARRA LATERAL

st.header('Marketplace - Visão Empresa')
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider=st.sidebar.slider(
                        'Ate qual dia?',
                        value=datetime(2022,4,13),
                        min_value=datetime(2022,2,11),
                        max_value=datetime(2022,4,13),
                        format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

cond_climatica = st.sidebar.multiselect('Selecione a condição climática',
    ['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'],default=['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'])

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condicoes do transito?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])
st.sidebar.markdown("""---""")

linhas_selecionadas=df1['Order_Date']< date_slider
df1 = df1.loc[linhas_selecionadas,:]

linhas_selecionadas=df1['Road_traffic_density'].isin(traffic_options)
df1=df1.loc[linhas_selecionadas,:]

linhas_selecionadas = df1['Weatherconditions'].isin(cond_climatica)
df1=df1.loc[linhas_selecionadas,:]

#LAYOUT PRINCIPAL
tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric(df1)
        st.plotly_chart(fig,use_container_width=True)

    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            fig=traffic_order_share(df1)
            st.plotly_chart(fig,use_container_width=True)
             
        with col2:
            fig=traffic_order_city(df1)
            st.plotly_chart(fig,use_container_width=True)

with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.plotly_chart(fig,use_container_width=True)

    with st.container():
        fig = order_share_by_week(df1)
        st.plotly_chart(fig,use_container_width=True)

with tab3:
    country_maps(df1)
