from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.callbacks import AsyncIteratorCallbackHandler

load_dotenv()

# Initialize the ChatBot using the 'gpt-4-turbo' model with a temperature of 0
ChatBot = ChatOpenAI(model='gpt-4-turbo', temperature=0)

# Create a callback handler for asynchronous iteration
callback = AsyncIteratorCallbackHandler()

# Initialize the ChatBotStreamer using the 'gpt-4-turbo' model with a temperature of 0,
# enabling streaming, and providing the callback handler for handling asynchronous iteration
ChatBotStreamer = ChatOpenAI(model='gpt-4-turbo', temperature=0, streaming=True, callbacks=[callback], verbose=True)
