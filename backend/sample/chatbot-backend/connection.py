from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Configure the OpenAI client to work with Gemini API
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Define the model configuration
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# Create the run configuration
config = RunConfig(
    model=model,
    model_provider=external_client,
)

# Example agent creation using the agents library
def create_agent(name: str, instructions: str):
    """Create an agent using the agents library with the configured settings"""
    agent = Agent(
        name=name,
        instructions=instructions,
        model = model,
    )
    return agent

# Example runner creation
def create_runner(agent):
    """Create a runner for the agent"""
    runner = Runner(

    )
    return runner