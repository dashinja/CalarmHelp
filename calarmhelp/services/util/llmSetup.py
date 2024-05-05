from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.callbacks import AsyncIteratorCallbackHandler

load_dotenv()

ChatBot = ChatOpenAI(model='gpt-4-turbo', temperature=0)

callback = AsyncIteratorCallbackHandler()

ChatBotStreamer = ChatOpenAI(model='gpt-4-turbo', temperature=0, streaming=True, callbacks=[callback], verbose=True)
