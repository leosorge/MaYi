# Generatore d'immagini 
# Usa stable diffusion base
# attraverso API huggingface

import streamlit as st
import requests

# Recupera il token dai secrets o da variabile d'ambiente
API_TOKEN = st.secrets["HF_TOKEN"]

def query_image_model(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return response.content
