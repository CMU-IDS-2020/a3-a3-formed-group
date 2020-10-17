from datetime import datetime
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

######################################
# Load data and cache
######################################
# @st.cache(allow_output_mutation=True)
def load(inp):
    return pd.read_csv(inp)
# https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset?select=covid_19_data.csv
df = load("covid_19_data.csv")
# Some manipulations for date and months
df['Date'] = pd.to_datetime(df['Date'])
df = df[df['Date'].dt.date < date.today()]
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
df["month"] = pd.DatetimeIndex(df['Date']).month

######################################
# Introductory text
######################################
st.title('Covid-19 Interactive Dashboard')
# st.sidebar.markdown('''
# Dataset reference:
#
# Designers: Aditya and Yuanxin
#
# Functionalities:
# ''')

######################################
# Add different fileters for users
# Generate a filtered df
######################################
st.subheader("For users")
# Select Date Range
st.write("Please specify how many months you want to view (Default last 1 months)")
last_month_value = st.slider("",
                             min_value=1, max_value=6, value=1, step=1)
max_month = df["month"].max()
df = df[df['month'] > max_month - last_month_value]

# Filter by Region
st.write("Please select contries of interest")
region_names = st.multiselect(label='', options=list(df.Region.unique())[::-1], default=["Mainland China", "Canada", "UK", "Japan", "South Korea"])
if len(region_names) > 0:
    df = df[df['Region'].isin(region_names)]


######################################
# Create interactive, multi-viewed (each view communicate with each other) plots
# histogram/bar plot, scatter plot, cascaded line plot, maps, heatmap
######################################
# Part I: Top 5 total for 3
# Part II: Curves for different contries
st.subheader('Comparision of different countries')
st.write("Select metrics to view")
option = st.selectbox('', ('Confirmed', 'Deaths', 'Recovered'))
number_versus_time  =alt.Chart(df).mark_circle().encode(
    x=alt.X('Date', title='Date'),
    y=alt.Y(option,  title=option),
    color='Region',
    tooltip = ['Confirmed', 'Deaths', 'Recovered'],
).interactive()
st.write(number_versus_time)

# Part II : Find correlations
st.subheader("Explore Correlations")
st.write("Now let's explore the correlations between pair of variables. Select your two variables here!")
variables = st.multiselect(label='', options=['Confirmed', 'Deaths', 'Recovered'], default=["Confirmed", "Deaths"])
if len(variables) > 2:
    variables = variables[:2]
scatter = alt.Chart(df).mark_point().encode(
    x=alt.X(variables[0], scale=alt.Scale(zero=False)),
    y=alt.Y(variables[1], scale=alt.Scale(zero=False)),
    color=alt.Y("Region"),
    tooltip = ['Confirmed', 'Deaths', 'Recovered']
).properties(
    width=600, height=400
)
remainder_var = [item for item in ['Confirmed', 'Deaths', 'Recovered'] if item not in variables][0]
picked = alt.selection_interval()

bar_plot_1 = alt.Chart(df).mark_bar().encode(
    x="Region",
    y="Recovered",
    color='Region',
    tooltip = ['Confirmed', 'Deaths', 'Recovered']
)
bar_plot_2 = alt.Chart(df).mark_bar().encode(
    x="Region",
    y="Confirmed",
    color='Region',
    tooltip = ['Confirmed', 'Deaths', 'Recovered']
)
bar_plot_3 = alt.Chart(df).mark_bar().encode(
    x="Region",
    y="Deaths",
    color='Region',
    tooltip = ['Confirmed', 'Deaths', 'Recovered']
)
bar_plots = bar_plot_1 + bar_plot_2 + bar_plot_3

st.write(
        scatter.encode(color=alt.condition(picked, "Region", alt.value("lightgrey")))
        .add_selection(picked) & bar_plots.transform_filter(picked))


# Part III: World Map

# Part IV: Word Cloud!
