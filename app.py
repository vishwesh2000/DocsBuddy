import cohere
import streamlit as st
from serpapi import GoogleSearch
import requests
from geopy.geocoders import Nominatim
from PIL import Image
from io import BytesIO

st.title("Hi there!👨‍⚕️🩺")
st.title("Welcome to *Virtual Diagnosis*")
st.write("> **This app is meant to assist medical professionals ONLY**")

co = cohere.Client('<Cohere API Key>')
prompt = st.text_input('What are the symptoms of your patient? (*Try to keep the symptoms meaningful*)')
prompt_med = st.text_input('Search a medicine here: (*Enter the correct spelling of the medicine*)')
geolocator = Nominatim(user_agent="geoapiExercises")

def get_coordinates(location):
    try:
        location = geolocator.geocode(location)
        return (location.latitude, location.longitude)
    except:
        return None

with open('symptoms_1.txt', 'r') as file:
    symptoms = [line.strip().lower() for line in file]
if prompt:
    if any(symptom in prompt.lower() for symptom in symptoms):
        response = co.generate(
            model = 'command-xlarge-nightly', #xlarge #medium #small
            prompt = f"user: Suggest prescription medications for these symptoms: {prompt}\nTLDR:", # 
            max_tokens=300,
            temperature=0.9,
            k=0,
            p=0.75,
            frequency_penalty=0,
            presence_penalty=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )

        text = format(response.generations[0].text)
        st.write('Prescription medications: %s' %text)
        st.download_button('Download example prescriptions', text)
        print("done!")

        
        params = {
        "engine": "google_shopping",
        "google_domain": "google.com",
        "q": text,
        "api_key": "<SerpApi API key>"
        }

        search = GoogleSearch(params)
        items = search.get_dict()


        for key, result in items.items():
            if "google_shopping_url" in result:
                st.caption(f'<a href="{result["google_shopping_url"]}">Click here for Google search page', unsafe_allow_html=True)
            else:
                pass

        for i in range(10):
            item = items['shopping_results'][i]
            response = requests.get(item['thumbnail'])
            st.image(Image.open(BytesIO(response.content)),
            caption=item['title'], width=400)
            st.text(item['source'])
            st.text(item['price'])
            st.caption(f'<a href="{item["link"]}">Click to buy</a>', unsafe_allow_html=True)


        address = st.text_input("Enter your location to search pharmacies near you: ( For best results, enter location in this *format: Area, City, Country*.)")

        if address:
            coordinates = get_coordinates(address)
            params = {
                "engine": "google_maps",
                "q": "Pharmacies",
                "ll": "@" + str(coordinates[0]) + "," + str(coordinates[1]) + ",15.1z",
                "type": "search",
                "api_key": "<SerpApi API key>"
                }

            search = GoogleSearch(params)
            results = search.get_dict()
            local_results = results["local_results"]
            for x in range(5):
                st.write("Name of pharmacy: ", local_results[x]["title"])
                st.write("address of pharmacy: ", local_results[x]["address"])
    
    else:
        st.write("Kindly pertain your inputs to possible medical symptoms only. Or try rephrasing.")

if prompt_med:
    params = {
    "engine": "google_shopping",
    "google_domain": "google.com",
    "q": f"{prompt_med} medicine",
    "hl": "en",
    # "gl": "in",
    "api_key": "<SerpApi API key>"
    }

    search = GoogleSearch(params)
    items = search.get_dict()


    for key, result in items.items():
        if "google_shopping_url" in result:
            st.caption(f'<a href="{result["google_shopping_url"]}">Click here for Google search page', unsafe_allow_html=True)
        else:
            pass

    for i in range(10):
        item = items['shopping_results'][i]
        response = requests.get(item['thumbnail'])
        st.image(Image.open(BytesIO(response.content)),
        caption=item['title'], width=400)
        st.text(item['source'])
        st.text(item['price'])
        st.caption(f'<a href="{item["link"]}">Click to buy</a>', unsafe_allow_html=True)
