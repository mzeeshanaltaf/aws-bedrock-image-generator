from util import *

# --- PAGE SETUP ---
# Initialize streamlit app
page_title = "Image Generator using AWS Bedrock"
page_icon = "🖼️"
st.set_page_config(page_title=page_title, page_icon=page_icon, layout="centered")

st.title("🖼️ Image Generator using AWS Bedrock")
st.write("***A Streamlit Image Generator powered by AWS Bedrock***")

st.sidebar.header('System Configuration')
secret_key, app_unlocked = configure_secret_access_key_sidebar()
model_provider, model_id = configure_sidebar_for_model_selection()

st.sidebar.divider()

st.sidebar.header('Image Configuration')
image_quality, orientation, image_size = configure_sidebar_for_image_configuration()

st.subheader("Enter the Image Description")
prompt = st.text_input('Enter the Image Description', placeholder='Enter the Image Description',
                       disabled=not app_unlocked, label_visibility="collapsed")
generate = st.button('Generate Image', type='primary', disabled=not prompt)
if generate:

    with st.spinner('Processing...'):
        model_response = invoke_llm_model(prompt, model_provider, model_id, secret_key, image_quality, orientation,
                                          image_size)
        st.image(model_response)
