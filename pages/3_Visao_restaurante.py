#Libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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

def distance(df1):
    cols=['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['distance']=df1.loc[:,cols].apply(lambda x:haversine((x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
    avg_distance = round(df1['distance'].mean(),1)
    return avg_distance
def time_city(df1):
    cols=['Time_taken(min)','City']
    df1_aux= df1.loc[:,cols].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df1_aux.columns=['Tempo_medio','Desvio_padrao_tempo']
    df1_aux=df1_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df1_aux['City'],y=df1_aux['Tempo_medio'],error_y=dict(type='data',array=df1_aux['Desvio_padrao_tempo'])))
    fig.update_layout(barmode='group')
    return fig
def time_city_type(df1):
    cols=['Time_taken(min)','City','Type_of_order']
    df1_aux= round(df1.loc[:,cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']}),2)
    df1_aux.columns=['Tempo_medio','Desvio_padrao_tempo']
    df1_aux=df1_aux.reset_index()
    return df1_aux
def distance_city(df1):
    cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
    df1['distance']=df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
    avg_distance=df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],values=avg_distance['distance'],pull=[0,0.1,0])])
    return fig
def traffic_time(df1):
    cols=['Time_taken(min)','City','Road_traffic_density']
    df1_aux= df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    df1_aux.columns=['Tempo_medio','std']
    df1_aux=df1_aux.reset_index()
    fig=px.sunburst(df1_aux,path=['City','Road_traffic_density'], values='Tempo_medio',color='std',color_continuous_scale='RdBu',color_continuous_midpoint=np.average(df1_aux['std']))
    return fig

df = pd.read_csv("train.csv")

df1 = clean_code(df)

#BARRA LATERAL

st.header('Marketplace - Visão Restaurantes')
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

tab1,tab2 = st.tabs(['Visão Gerencial','_'])
with tab1:
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns(6,vertical_alignment='center')   
        with col1:
            delivery_unique=df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores',delivery_unique)
        with col2:
            avg_distance = distance(df1)
            col2.metric('Distância media',avg_distance)
        with col3:
            df1_aux=round(df1.loc[df1['Festival']=='Yes','Time_taken(min)'].mean(),1)
            col3.metric('Tempo Festival',df1_aux)
        with col4:
            df1_aux=round(df1.loc[df1['Festival']=='Yes','Time_taken(min)'].std(),1)
            col4.metric('DP Festival',df1_aux)           
        with col5:
            df1_aux=round(df1.loc[df1['Festival']=='No','Time_taken(min)'].mean(),1)
            col5.metric('Tempo s/ Festival',df1_aux)
        with col6:
            df1_aux=round(df1.loc[df1['Festival']=='No','Time_taken(min)'].std(),1)
            col6.metric('DP s/ Festival',df1_aux)     
    with st.container():
        col1,col2=st.columns(2)
        with col1:
            st.markdown('##### Distribuição do tempo por cidade')
            fig = time_city(df1)
            st.plotly_chart(fig,use_container_width=True)
        with col2:
            st.markdown('##### Tempo médio por cidade e tipo de pedido')
            df1_aux= time_city_type(df1)
            st.dataframe(df1_aux)
    with st.container():
        col1,col2 = st.columns(2,gap='large',vertical_alignment='center')
        with col1:
            st.markdown('##### Distribuição da distancia media por cidade ')
            fig = distance_city(df1)
            st.plotly_chart(fig,use_container_width=True,use_container_height=True)
        with col2:
            st.markdown('##### Tempo médio por tipo de transito')
            fig=traffic_time(df1)
            st.plotly_chart(fig,use_container_width=True)  
