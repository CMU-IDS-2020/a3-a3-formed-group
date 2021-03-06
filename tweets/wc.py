import streamlit as st
import pandas as pd 
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer 
import webbrowser

def load_data(file):
    covid=pd.read_csv(file,sep=',')
    return covid
url = "https://en.wikipedia.org/wiki/Lemmatisation"

##turn csv into Dictionary Object
st.cache(suppress_st_warning=True)
tweets = load_data("frequent_terms.csv").reset_index()
st.cache(suppress_st_warning=True)
min_val = int(tweets['counts'].min())
st.cache(suppress_st_warning=True)
tweets = tweets[tweets.counts <=  5*min_val]
st.cache(suppress_st_warning=True)
raw_dic = pd.Series(tweets.counts.values,index=tweets.term).to_dict()


#load interactivity elements
st.cache(suppress_st_warning=True)
st.header('Word Usage in Covid-19 Tweets (April 2020)')
st.sidebar.write("Choose Word Cloud Options")
remove_eng = st.sidebar.checkbox("Remove English Stop Words")
remove_esp = st.sidebar.checkbox("Remove Spanish Stop Words")

show_chart = st.button('Show Distribution')
slider_ph = st.empty()
value = slider_ph.slider("Choose Max Frequency", min_value=min_val, max_value=5*min_val, step=10)

#user input
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
basic_chart = alt.Chart(tweets[tweets['counts'] <= value]).mark_line().encode(
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