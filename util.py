import json
import streamlit as st
import boto3
import base64

# Dictionary containing model providers, model name and model ID
model_dic = {
    'Amazon':
        {'Titan Image Generator G1': "amazon.titan-image-generator-v1"},
}


def configure_sidebar_for_image_configuration():
    image_quality = st.sidebar.selectbox("Select the Image Quality", ('Standard', 'Premium'))
    orientation = st.sidebar.radio('Select the Orientation', ['Portrait', 'Landscape'])
    image_size = st.sidebar.selectbox("Select the Image Size", ('512 x 512', '1024 x 1024'))
    num_of_images = st.sidebar.slider('Number of Images to Generate', 1, 5, 1)
    return image_quality, orientation, image_size, num_of_images


# Function to configure sidebar to get the secret access key
def configure_secret_access_key_sidebar():
    secret_key = st.sidebar.text_input('Enter the secret access key', type='password')
    if secret_key == '':
        st.sidebar.warning('Enter the secret access key to unlock the application')
        app_unlocked = False
    elif len(secret_key) == 40:
        st.sidebar.success('Proceed. Application is now unlocked', icon='️👉')
        app_unlocked = True
    else:
        st.sidebar.error('Please enter the correct credentials!', icon='⚠️')
        app_unlocked = False

    return secret_key, app_unlocked


# Function configure sidebar for model selection
def configure_sidebar_for_model_selection():
    model_provider = st.sidebar.selectbox("Select the Model Provider:", (model_dic.keys()))
    llm = st.sidebar.selectbox("Select the LLM", (model_dic[model_provider].keys()))
    model_id = model_dic[model_provider][llm]
    return model_provider, model_id


# Function to configure model payload as per given model provider. Each model provider has different ways to
# configure payload
def get_model_payload(model_provider, prompt_data, image_quality, orientation, image_size, num_of_images):
    image_height = int(image_size.split('x')[0].strip())
    image_width = int(image_size.split('x')[0].strip())
    if model_provider == 'Amazon':
        text_to_image_params = {"text": prompt_data}
        imageGenerationConfig = {"cfgScale": 8, "seed": 0, "quality": image_quality.lower(), "width": image_width,
                                 "height": image_height, "numberOfImages": num_of_images}
        return {
            "textToImageParams": text_to_image_params,
            "taskType": "TEXT_IMAGE",
            "imageGenerationConfig": imageGenerationConfig,
        }


# Function to get model response based on model provider.
def get_model_response(model_provider, response_body, num_of_images):
    image_bytes = []
    if model_provider == 'Amazon':
        for i in range(num_of_images):
            image_encoded = response_body.get("images")[i].encode("utf-8")
            image_bytes.append(base64.b64decode(image_encoded))
        return image_bytes


# Function to invoke LLM
def invoke_llm_model(prompt_data, model_provider, model_id, secret_key, image_quality, orientation, image_size,
                     num_of_images):
    bedrock = boto3.client(service_name='bedrock-runtime',
                           aws_access_key_id='AKIAYS2NUCSXLJLV3AG6',
                           aws_secret_access_key=secret_key,
                           region_name='ap-south-1')
    payload = get_model_payload(model_provider, prompt_data, image_quality, orientation, image_size, num_of_images)
    body = json.dumps(payload)
    response = bedrock.invoke_model(
        body=body,
        modelId=model_id,
        contentType="application/json",
        accept="application/json"
    )
    response_body = json.loads(response.get("body").read())
    image_bytes = get_model_response(model_provider, response_body, num_of_images)
    return image_bytes
