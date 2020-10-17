from datetime import datetime
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

##wordcloud imports
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer 
import webbrowser


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

url = "https://en.wikipedia.org/wiki/Lemmatisation"
##load Dataframe for Wordcloud
st.cache(suppress_st_warning=True)
tweets = load("tweets/frequent_terms.csv").reset_index()
min_val = int(tweets['counts'].min())
tweets = tweets[tweets.counts <=  5*min_val]
raw_dic = pd.Series(tweets.counts.values,index=tweets.term).to_dict()

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

#load interactivity elements
st.cache(suppress_st_warning=True)
st.header('Word Usage in Covid-19 Tweets (April 2020)')
st.sidebar.write("Choose Word Cloud Options")
remove_eng = st.sidebar.checkbox("Remove English Stop Words")
remove_esp = st.sidebar.checkbox("Remove Spanish Stop Words")

show_chart = st.button('Show Distribution')
slider_ph = st.empty()
value = slider_ph.slider("Choose Max Frequency", min_value=min_val, max_value=5*min_val, value = 2*min_val, step=10)

#user text input
custom = st.sidebar.text_input('Add Custom Stopwords (comma separated)')
custom = custom.split(',')

lemma = st.sidebar.checkbox("Lemmatize")

#create stopwords list
st.cache(suppress_st_warning=True)
stop_words = []
if(custom):
    stop_words += custom
if(remove_eng):
    stop_words +=  stopwords.words('english')
if(remove_esp):
    stop_words +=  stopwords.words('spanish')


#create chart
st.cache(suppress_st_warning=True)
basic_chart = alt.Chart(tweets[tweets['counts'] <= value]).mark_bar().encode(
    x='index',
    y='counts'
).interactive()


#create lemmatized dictionary
st.cache(suppress_st_warning=True) 
lemmatizer = WordNetLemmatizer()
lemma_dic = {lemmatizer.lemmatize(k.strip()): v for k, v in raw_dic.items()}

#choose dictionary to generate wordcloud
st.cache(suppress_st_warning=True)   
if(lemma):
    dic = {k:v for k,v in lemma_dic.items() if v <= value and k not in stop_words}
    st.sidebar.write("Words will be Lemmatized")
    if st.sidebar.button("More Info (External Link)"):
        webbrowser.open_new_tab(url)
else:
    dic = {k:v for k,v in raw_dic.items() if v <= value and k not in stop_words}

#create wordcloud
st.cache(suppress_st_warning=True)
wordcloud = WordCloud().generate_from_frequencies(frequencies=dic)
fig = plt.figure()
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
st.pyplot(fig)
if(show_chart):
    st.altair_chart(basic_chart)