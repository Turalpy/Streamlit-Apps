import pandas as pd 
import numpy as np 
import streamlit as st 
from pytube import YouTube 

st.header("Download Youtube videos and audios.")
url = st.text_input("Enter the URL:")

option = st.radio("Format:",["Video","Audio"])

if st.button("Download"):
    if len(url) > 15:
        try:
            yt = YouTube(url)
            if option =="Video":
                st.write("Video is downloading...")
                yt.streams.get_highest_resolution().download()
                st.write("Video is downloaded")
            if option == "Audio":
                st.write("Audio is downloading...")
                data = yt.streams.get_audio_only().download()
                st.write("Audio is downloaded")
        except:
            st.write("Error occured")
    else:
        st.write("Please enter a valid Youtube URL")
if st.button("view"): 
    try:
	    st.video(url) 
    except:
        st.write("Error occured")





