import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.langchain import CallbackHandler

load_dotenv()

langfuse_handler = CallbackHandler()


def make_gemini_request(query: str) -> str:
    """This method takes in a string query and returns the gemini response"""

    try:
        llm = ChatGoogleGenerativeAI(
            google_api_key=os.environ["GEMINI_KEY"], model="gemini-2.5-flash-lite"
        )

        messages = [
            SystemMessage("You are a helpful assistant who follow user requests."),
            HumanMessage(query),
        ]

        res = llm.invoke(messages, config={"callbacks": [langfuse_handler]})

        return str(res.content)
    except Exception:
        return "Unable to process the query"
