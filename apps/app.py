import streamlit as st
from PIL import Image
import base64
import boto3
import io
import json
import os


DEBUG = os.getenv("DEBUG", False)
DEFAULT_SEED = os.getenv("DEFAULT_SEED", 12345)
NEGATIVE_PROMPTS = [
    "bad anatomy", "distorted", "blurry",
    "pixelated", "dull", "unclear",
    "poorly rendered",
    "poorly Rendered face",
    "poorly drawn face",
    "poor facial details",
    "poorly drawn hands",
    "poorly rendered hands",
    "low resolution",
    "Images cut out at the top, left, right, bottom.",
    "bad composition",
    "mutated body parts",
    "blurry image",
    "disfigured",
    "oversaturated",
    "bad anatomy",
    "deformed body features",
]
# Complete preset_style list: https://platform.stability.ai/docs/api-reference#tag/v1generation/operation/textToImage
STYLES_MAP = {
    "電影感(Cinematic)": "cinematic",
    "攝影(Photographic)": "photographic",
    "漫畫(Comic Book)": "comic-book",
    "摺紙(Origami)": "origami",
    "模擬膠片(Analog Film)": "analog-film",
    "幻想藝術(Fantasy Art)": "fantasy-art",
    "線條藝術(Line Art)": "line-art",
    "霓虹龐克粉(Neon Punk)": "neon-punk",
    "三維模型(3D Model)": "3d-model",
    "数字艺术(Digital Art)": "digital-art",
    "增強(Enhance)": "enhance",
    "像素藝術(Pixel Art)": "pixel-art",
    "瓷磚紋理(Tile Texture)": "tile-texture",
    "無(None)": "None",
}

bedrock_runtime = boto3.client('bedrock-runtime')

contentType = "application/json"
accept = "application/json"
modelId = "stability.stable-diffusion-xl-v0"


@st.cache_data(show_spinner=False)
def gen_img_from_bedrock(prompt, style, seed=DEFAULT_SEED):
    body = json.dumps({
        "text_prompts": [
            {
                "text": prompt
            }
        ],
        "cfg_scale": 10,
        "seed": seed,
        "steps": 50,
        "style_preset": style,
        "negative_prompts": NEGATIVE_PROMPTS
    })
    modelId = "stability.stable-diffusion-xl"
    accept = "application/json"
    contentType = "application/json"
    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())
    image_bytes = response_body.get("artifacts")[0].get("base64")
    image_data = base64.b64decode(image_bytes.encode())
    st.session_state['image_data'] = image_data
    return image_data


def update_slider():
    st.session_state.slider = st.session_state.numeric


def update_numin():
    st.session_state.numeric = st.session_state.slider


@st.cache_data
def get_image(image_data):
    return Image.open(io.BytesIO(image_data))


if __name__ == '__main__':
    # Create the page title
    st.set_page_config(
        page_title='Amazon Bedrock Stable Diffusion', page_icon='./bedrock.png')
    st.title('Stable Diffusion Image Generator with Amazon Bedrock')
    # Create a sidebar with text examples
    with st.sidebar:
        # Selectbox
        style_key = st.sidebar.selectbox(
            "Choose image style",
            STYLES_MAP.keys(),
            index=0)

        seed_input = st.sidebar.number_input(
            "Seed", value=DEFAULT_SEED, placeholder=DEFAULT_SEED, key="numeric", on_change=update_slider)
        seed_slider = st.sidebar.slider(
            'Seed Slider', min_value=0, value=seed_input, max_value=99999, step=1, key="slider",
            on_change=update_numin, label_visibility="hidden")
        seed = seed_input | seed_slider

    prompt = st.text_input('Input your prompt')
    if not prompt:
        st.warning("Please input a prompt")
        # Block the image generation if there is no input prompt
        st.stop()

    if st.button("Generate", type="primary"):
        if len(prompt) > 0:
            st.markdown(f"""
            This will show an image using **Stable Diffusion** with your desired prompt entered : {prompt}
            """)
            # Create a spinner to show the image is being generated
            with st.spinner('Generating image based on prompt'):
                if not DEBUG:
                    style = STYLES_MAP[style_key]
                    print("Generate image with Style:{} with Seed:{} and Prompt: {}".format(
                        style_key, seed, prompt))
                    # Send request to Bedrock
                    image_data = gen_img_from_bedrock(
                        prompt=prompt, style=style, seed=seed)
                    st.success('Generated stable diffusion image')

    if st.session_state.get("image_data", None):
        image = get_image(st.session_state.image_data)
        st.image(image)

    if DEBUG:
        st.write(st.session_state)
