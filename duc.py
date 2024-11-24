import os
import base64
import openai
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.tools import DuckDuckGoSearchResults  # Import for web search

# Load environment variables from .env file
load_dotenv()

api_key = st.secrets["general"]["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI()


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def encode_image_streamlit(uploaded_image):
    return base64.b64encode(uploaded_image.read()).decode('utf-8')


# Streamlit app
st.title("Image Content Analyzer")
st.write("Upload an image.")

# Upload image
uploaded_image = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    # Display the uploaded image
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # Encode the image in base64 format
    base64_image = encode_image_streamlit(uploaded_image)

    # Interact with OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is in this image? From the image only provide me the things that are available in the image. If it's a product, please write the name of the product,its brand,product model and product size.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )

        # Extract the products or items from the response
        identified_products = response.choices[0].message.content

        # Display the analysis result
        st.write("Analysis Result:")
        st.write(identified_products)

        # Hardcoded prompt to find the average price of each identified product
        st.write("Searching for the average price of each identified product...")

        # Perform web search using DuckDuckGoSearchResults
        def search_query(query):
            search = DuckDuckGoSearchResults()
            results = search.invoke(query)
            return results

        # Process each product
        products = identified_products.split(",")  # Assuming products are comma-separated
        for product in products:
            query = f"Find the average price of {product.strip()}"
            st.write(f"Searching for: {query}")
            results = search_query(query)
            st.write(f"Search results for {product.strip()}:")
            st.write(results)

    except Exception as e:
        st.error(f"An error occurred: {e}")
