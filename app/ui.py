import streamlit as st
import os
from dotenv import load_dotenv

from utils import generate_dalle_prompt, generate_image_from_text, get_openAPI_response

# Constants for options
from constants import image_styles_options, image_size_option, image_model_options


def setup_sidebar():
    with st.sidebar:
        st.markdown("""# Welcome, Kanak Dahake""")
        st.markdown("---")
        st.markdown("#### My Settings")
        OPENAI_MODEL = st.radio(
            "Choose OpenAI Model",
            (
                "gpt-4-1106-preview",
                "gpt-4",
                "gpt-4-32k",
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo",
                "text-davinci-003",
            ),
            index=3,
        )
        os.environ["OPENAI_MODEL"] = OPENAI_MODEL


def setup_sidebar_about():
    with st.sidebar:
        st.markdown("---")
        with st.expander("Developer: **Kanak Dahake**", expanded=True):
            st.markdown(
                """📧 ksdusa4@gmail.com \\
🌐 [Website](https://kanakjr.in) 
👔 [LinkedIn](https://www.linkedin.com/in/kanak-dahake)
🐙 [GitHub](https://github.com/Kanakjr)"""
            )


def display_write_tab():
    col1, col2 = st.columns([1, 1], gap="medium")
    st.session_state["input_text"] = col1.text_area("Input Text:", "", height=500)
    if col1.button("Generate Answer", use_container_width=True):
        st.session_state["response_text"] = get_openAPI_response(
            text=st.session_state["input_text"], task="Write Text"
        )
    if st.session_state["response_text"]:
        col2.markdown("##### Response:")
        col2.markdown(st.session_state["response_text"])


def display_summarize_tab():
    pass


def display_generate_image_tab():
    col1, col2 = st.columns([1.2, 1], gap="medium")
    input_text = col1.text_input("Input Text:", "")
    image_style = col1.selectbox("Select Image Style (Optional):", image_styles_options, index=0)

    if col1.button(
        "Generate Prompt", key=f"generate_dalle_prompt", use_container_width=True
    ):
        st.session_state["image_prompt"] = generate_dalle_prompt(
            text=input_text, image_style=image_style
        )

    # col1.divider()
    col1.text_area("Image Prompt", value=st.session_state["image_prompt"], height=180)
    image_model = col1.selectbox("Select Model",image_model_options)
    imgcol1,imgcol2 = col1.columns([1,2])
    image_quality = imgcol1.radio("Image Quality",["standard",'hd'],horizontal=True)
    image_size = imgcol2.radio("Image Size",image_size_option,horizontal=True)

    if col1.button("Generate Image >>", use_container_width=True):
        if (
            st.session_state["image_prompt"]
            and len(st.session_state["image_prompt"]) > 10
        ):
            image_url = generate_image_from_text(
                image_prompt=st.session_state["image_prompt"],
                model=image_model,
                size=image_size,
                quality=image_quality
            )
            if image_url is None or image_url == "":
                st.error("No image was generated")
            else:
                st.session_state["image_url"] = image_url
        else:
            st.error("Please enter image prompt!")

    if st.session_state["image_url"]:
        col2.markdown("Generated Image:")
        col2.markdown(
            f'<img src="{st.session_state["image_url"]}" alt="drawing" width=100%/><br>',
            unsafe_allow_html=True,
        )


def create_tools_layout():
    # Create tabs for Write Social Post, Write Article, Generate Image, Summarize, and Build Bullets
    tab_labels_actions = [
        "📝 Write Text",
        "🖼️ Generate Image",
        "📑 Summarize",
    ]
    (
        write_tab,
        generate_image_tab,
        summarise_tab,
    ) = st.tabs(tab_labels_actions)

    with write_tab:
        display_write_tab()

    with generate_image_tab:
        display_generate_image_tab()

    with summarise_tab:
        display_summarize_tab()


def display_stats_report(stats_report):
    with st.spinner("Generating document statistics"):
        markdown = f"""
        #####
        ###### Document Statistics
        - **Readability Score**: {stats_report['readability_score']}
        - **Word Count**: {stats_report['document_statistics']['Word Count']}
        - **Paragraphs**: {stats_report['document_statistics']['Paragraphs']}
        - **Sentences**: {stats_report['document_statistics']['Sentences']}
        - **Unique Words**: {stats_report['vocabulary_statistics']['Unique Words']}
        ###### Tone and Style
        - **Tone**: {stats_report['tone_type']}
        - **Intent**: {stats_report['intent_type']}
        - **Audience**: {stats_report['audience_type']}
        - **Style**: {stats_report['style_type']}
        - **Emotion**: {stats_report['emotion_type']}
        - **Domain**: {stats_report['domain_type']}
        """
        st.info(markdown)


def initialize_session_state():
    if "image_prompt" not in st.session_state:
        st.session_state["image_prompt"] = None
    if "response_text" not in st.session_state:
        st.session_state["response_text"] = None
    if "image_url" not in st.session_state:
        st.session_state["image_url"] = None


#### MAIN CODE #########

load_dotenv("./.env")

# Set API keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


# Set Streamlit page config
st.set_page_config(page_title="AI Tools", layout="wide")
st.markdown(
    """<style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        .block-container {padding-top: 1.2rem; padding-bottom: 0rem; }
</style>""",
    unsafe_allow_html=True,
)

# Streamlit app title and description
st.title("🤖 AI Tools")

# Call the function to initialize session state
initialize_session_state()

setup_sidebar()
setup_sidebar_about()

create_tools_layout()
