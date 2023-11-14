from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.schema.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import streamlit as st
import re
import os
import json

from typing import Dict


class CustomDallEAPIWrapper(DallEAPIWrapper):
    """Custom subclass of DallEAPIWrapper with additional parameters."""

    def dalle_image_url(
        self, prompt: str, model="dall-e-3", size="1024x1024", quality="standard"
    ) -> str:
        params = {
            "prompt": prompt,
            "n": self.n,
            "size": size,
            "quality": quality,
            "model": model,
        }
        response = self.client.create(**params)
        return response["data"][0]["url"]


def get_llm(OPENAI_MODEL=None, max_tokens=1000):
    if not OPENAI_MODEL:
        OPENAI_MODEL = os.environ.get("OPENAI_MODEL")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    llm = ChatOpenAI(
        temperature=0,
        model_name=OPENAI_MODEL,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=max_tokens,
    )
    return llm


@st.cache_data(ttl=60 * 60 * 12)  # Cache data for 12 hours
def get_html(url):
    # Load HTML content from a URL using a WebBaseLoader
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)  # Cache data for 12 hours
def get_openAPI_response(text, task, OPENAI_MODEL=None, max_tokens=1000, llm=None):
    messages = [HumanMessage(content=text)]
    llm = get_llm(OPENAI_MODEL=OPENAI_MODEL, max_tokens=max_tokens)
    with st.spinner(task):
        response = llm.invoke(messages, config={"run_name": task})
        response = str(response.content)
    return response


def generate_stats_report(text):
    prompt = f"""# Can you provide a report on the Text? The report should include document statistics, vocabulary statistics, readability score, tone type (available options are Formal, Informal, Optimistic, Worried, Friendly, Curious, Assertive, Encouraging, Surprised, or Cooperative), intent type (available options are Inform, Describe, Convince, or Tell A Story), audience type (available options are General, Knowledgeable, or Expert), style type (available options are Formal or Informal), emotion type (available options are Mild or Strong), and domain type (available options are General, Academic, Business, Technical, Creative, or Casual).

# Structure the output in a below JSON format
ReportOutput = {{
  "document_statistics": {{"Word Count": int, "Paragraphs": int, "Sentences": int}},
  "vocabulary_statistics": {{"Unique Words": int, "Lexical Density": int}},
  "readability_score": int,"tone_type": str,"intent_type": str,
  "audience_type": str, "style_type": str,"emotion_type": str,
  "domain_type": str
}}

# Text:
{text}

# Output
ReportOutput ="""
    response = get_openAPI_response(prompt, task="Getting statistics", max_tokens=200)
    try:
        response = json.loads(response)
        return response
    except:
        return None


@st.cache_data(ttl=60 * 60 * 12)  # Cache data for 12 hours
def generate_dalle_prompt(
    text, text_type="text", image_type="image", image_style=None, custom_rules=""
):
    # Define the prompt template and input variables
    if image_style:
        custom_rules += f"Generate image in a {image_style} Style."
    prompt = PromptTemplate(
        input_variables=["text", "text_type", "image_type", "custom_rules"],
        template="""Write a DALL.E prompt to generate an {image_type}" based on the following {text_type}. 
# {text_type}: {text}
# Rules: Only output the prompt in less than 100 words.
{custom_rules}
# Prompt:""",
    )
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=prompt)
    image_prompt = chain.invoke(
        input={
            "text": text,
            "text_type": text_type,
            "image_type": image_type,
            "custom_rules": custom_rules,
        },
        config={"run_name": "Dalle Prompt"},
    )
    image_prompt = image_prompt["text"]
    return image_prompt


@st.cache_data(ttl=60 * 60 * 12)  # Cache data for 12 hours
def generate_image_from_text(
    image_prompt, model="dall-e-3", size="1024x1024", quality="standard"
):
    image_url = CustomDallEAPIWrapper().dalle_image_url(
        prompt=image_prompt, model=model, size=size, quality=quality
    )
    return image_url


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    import warnings

    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="streamlit.runtime.caching.cache_data_api",
    )
    load_dotenv("./app/.env")

    # get_openAPI_response(text="Hello", task="Greetings")

    # text = "a man on moon driving car"
    # print(CustomDallEAPIWrapper().run(text))

    text = "burger on moon."
    text_type = "News Title"
    image_type = "News Image"
    image_prompt = generate_dalle_prompt(text, text_type, image_type)
    image_url = generate_image_from_text(image_prompt)
    print("Generated image Prompt:", image_prompt)
    print("Generated image URL:", image_url)
