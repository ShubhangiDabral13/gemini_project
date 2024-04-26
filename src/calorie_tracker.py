#importing the modules
from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image, ImageEnhance
import base64
from io import BytesIO


load_dotenv() ## load all the environment variables

#getting the api key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


#function to get the response from gemini pro and returning it
def get_gemini_repsonse(input_prompt, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input_prompt,image[0]])
    return response.text

#to get the image in the format which is required by gemini-pro vision
def input_image_setup(uploaded_file):
    # Checking it the image is been uploaded or not
    if uploaded_file is not None:
        #reading the image in bytes
        bytes_data = uploaded_file.getvalue()

        #below is the format required by google gemini pro
        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")
    

#initialize our streamlit app
#Setting the page title and the image
st.set_page_config(page_title="Health Eats Analyzer", page_icon=":apple:")


st.markdown(
    "<h1 style='color: #0D9276;'>Health Eats Analyzer</h1>",
    unsafe_allow_html=True
)

# Adding description with custom font color
st.markdown(
    "<p style='color: #164B60;font-size: 24px;'>Welcome to Health Eats Analyzer! This app analyzes the nutritional value of your food.</p>",
    unsafe_allow_html=True
)

#below are the functions to get the background image with a bit of light background 
def lighten_image(image_path, brightness_factor=1.0):
    img = Image.open(image_path)
    enhancer = ImageEnhance.Brightness(img)
    lightened_img = enhancer.enhance(brightness_factor)
    return lightened_img

def get_base64_from_image(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def set_background(image_path, brightness_factor= 0.99):
    lightened_img = lighten_image(image_path, brightness_factor)
    base64_img = get_base64_from_image(lightened_img)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
    }
    </style>
    ''' % base64_img
    st.markdown(page_bg_img, unsafe_allow_html=True)

#setting the background images
set_background('background.jpeg', brightness_factor= 0.99)
    

#uploading the meal image either in jpg, jpeg or png
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image=""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

#submit button after image has been uploaded
submit=st.button("Examine the nutritional content of the meal")

#defining the input prompt
input_prompt="""
You are an expert in nutritionist where you need to see the food items from the image
               and calculate the total calories, also provide the details of every food items with calories intake
               is below format

               1. Item 1 - no of calories
               2. Item 2 - no of calories
               ----
               ----

        Finally You can mention whether the food is healthy or not. 
        Also, provide the percentage proportion of different nutrients in the following format, 
with each value on a new line:

               1. total fat - percentage
               2. saturated fat - percentage
               3. Trans Fat
               4. cholesterol
               5. sodium
               6. total carbohydrate
               7. dietary fiber
               8. total sugars
               9. added sugars
               10. Protien 
               11. Certain Vitamins
               12. Minerals
"""

## on clicking the submit button 
if submit:
    image_data=input_image_setup(uploaded_file)
    response=get_gemini_repsonse(input_prompt,image_data)
    st.subheader("The Response is")
    st.write(response)

