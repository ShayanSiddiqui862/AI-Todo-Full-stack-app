from connection import config
from agents import Agent, Runner, function_tool
import requests

@function_tool
def ShoppingData():
    data = requests.get("https://template6-six.vercel.app/api/products")
    data = data.json()
    return data

agent = Agent(
    name="Shopping Assistant",
    instructions="You are a shopping assistant that will get data from api and let user know about the products data.",
    tools=[ShoppingData]
)

result = Runner.run_sync(agent,
                         """Can you tell about the number of products available on store
                         and can you tell about the categories""",
                         run_config=config
                         
                         
    
)
print(result.final_output)