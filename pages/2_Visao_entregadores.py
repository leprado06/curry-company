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
def top_delivers(df1,top_asc):
    cols=['Delivery_person_ID','Time_taken(min)','City']
    entregadores_lentos=(df1.loc[:,cols].groupby(['City','Delivery_person_ID'])
                                        .mean()
                                        .sort_values(['City','Time_taken(min)'],ascending=top_asc)
                                        .reset_index())
    df1_aux01=entregadores_lentos.loc[entregadores_lentos['City'] == 'Metropolitian',:].head(10)
    df1_aux02=entregadores_lentos.loc[entregadores_lentos['City'] == 'Urban',:].head(10)
    df1_aux03=entregadores_lentos.loc[entregadores_lentos['City'] == 'Semi-Urban',:].head(10)
    entregadores_lentos_city=pd.concat([df1_aux01,df1_aux02,df1_aux03]).reset_index(drop=True)
    return entregadores_lentos_city

df = pd.read_csv("train.csv")

df1 = clean_code(df)

#BARRA LATERAL

st.header('Marketplace - Visão Entregadores')
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

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        
        col1,col2,col3,col4 = st.columns(4, gap='large',vertical_alignment='center')
        with col1:
            maior_idade=df1['Delivery_person_Age'].max()
            st.metric(label='### Maior Idade',value=maior_idade)
        with col2:
            menor_idade=df1['Delivery_person_Age'].min()
            st.metric(label='### Menor Idade',value=menor_idade)
        with col3:
            melhor_condicao=df1['Vehicle_condition'].max()
            st.metric(label='### Melhor Condicao',value=melhor_condicao)
        with col4:
            pior_condicao=df1['Vehicle_condition'].min()
            st.metric(label='### Pior Condicao',value=pior_condicao)
    with st.container():
        col1,col2 = st.columns(2, gap='large',vertical_alignment='center')
        with col1:
            st.markdown('##### Média de avaliações por entregador')
            cols=['Delivery_person_ID','Delivery_person_Ratings']
            rating=(round(df1.loc[:,cols].groupby('Delivery_person_ID')
                                         .mean()
                                         .reset_index(),2))
            rating.columns=['ID','Ratings']
            st.dataframe(rating.sort_values(by='Ratings',ascending=False))
        with col2:
            with st.container():
                st.markdown('##### Média de avaliações por transito')
                cols=['Delivery_person_Ratings','Road_traffic_density']
                rating_med=(round(df1.loc[:,cols].groupby('Road_traffic_density')
                                                 .agg({'Delivery_person_Ratings': ['mean','std']}),2))
                rating_med.columns = ['Média','Desvio Padrao']
                rating_med.reset_index()
                st.dataframe(rating_med)
            with st.container():
                st.markdown('##### Média de avaliações por clima')
                cols=['Delivery_person_Ratings','Weatherconditions']
                rating_avg_std_weatherconditions=(round(df1.loc[:,cols].groupby('Weatherconditions')
                                                                       .agg({'Delivery_person_Ratings':['mean','std']}),2)  )
                rating_avg_std_weatherconditions.columns=['Média','Desvio Padrão']
                st.dataframe(rating_avg_std_weatherconditions)
    with st.container():
        col1, col2 = st.columns(2, gap='large',vertical_alignment='center')
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df3=top_delivers(df1,top_asc=True)
            st.dataframe(df3)
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3=top_delivers(df1,top_asc=False)
            st.dataframe(df3)
