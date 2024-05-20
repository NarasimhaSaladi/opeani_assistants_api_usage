# import openai
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime
import os
import requests
import json

load_dotenv()
# openai.api_key = os.environ.get("OPENAI_API_KEY")
# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name, you can do something like:
# client = OpenAI(
#   api_key=os.environ.get("CUSTOM_ENV_NAME"),
# )

# client = openai.OpenAI()
model = "gpt-3.5-turbo-16k"

News_api_key=os.environ.get("NEWS_API_KEY")
def get_news(topic):
    url=(
        f"https://newsapi.org/v2/everything?q={topic}&from=2024-04-20&sortBy=publishedAt&apiKey={News_api_key}"
    )
    
    try:
        
        response=requests.get(url)
        
        if(response.status_code==200):
            # news= json.dumps(response.json(),indent=4)
            # news_json=json.load(news)
            news_string = json.dumps(response.json(), indent=4)  # Convert to string with indentation
            news_json = json.loads(news_string) 
            
            data=news_json
            # Access all the fields
            # access_all_fields = ["status", "total_results", "articles"]

            # Extract data from JSON
            status = data["status"]
            total_results = data["totalResults"]
            articles = data["articles"]
            
            processed_articles=[]
            # Loop through articles
            for article in articles:

                source_name = article["source"]["name"]
                author = article["author"]

                title = article["title"]
                description = article["description"]

                url = article["url"]
                content = article["content"]
                
                title_description = f"""
                Title: {title}
                Author: {author}
                Source: {source_name}
                Description: {description}
                URL: {url}
                """

                processed_articles.append(title_description)
                
            return processed_articles
        else:
            return []
            


            
    except requests.exceptions.RequestException as e:
        print("error occcured during API Request",e)

def main():
    # print(get_news("bitcoin"))
    news2=get_news("bitcoin")
    print(news2[0])
    
    
    
    
class AssistantManager:
    thread_id=None
    assistant_id=None
    
    def __init__(self,model:str = model)->None:
        self.client=client
        self.model=model
        self.assistant=None
        self.thread=None
        self.run=None
        self.sum=None
    if AssistantManager.assistant_id:
        self.assistant = self.client.beta.assistants.retrieve(
        assistant_id=AssistantManager.assistant_id
    )

    if AssistantManager.thread_id:
        self.thread = self.client.beta.threads.retrieve(
            thread_id=AssistantManager.thread_id
        )
    def create_assistant(self,name,instructions,tools):
        if not self.assistant:
            assistant_obj=self.client.beta.assistants.create(
                name=name,
                instruction=instructions,
                tools=tools,
                model=self.model
            )
            AssistantManager.assistant_id=assistant_obj.id
            self.assistant=assistant_obj
            
            print(f"ASS_id:{self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread_obj=self.client.beta.threads.create()
            AssistantManager.thread_id=thread_obj.id
            self.thread=thread_obj
            
            print(f"thread_id:{self.thread.id}")
        
    def add_messsages_to_thread(self,role,content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content
            )
    def run_assistant(self,instructions):
        if self.thread and sel.assistant:
            self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=instructions,)
    def process_mess(self):
        if self.thread:
            messages=self.client.beta.threads.messages.list(thread_id=self.thread_id)
            summary=[]
            
            last_mess=messages.data[0]
            response=last_mess.content[0].text.value
            role=last_mess.role
            
            summary.append(response)
            
            self.summary="\n".join(summary)
            print(f"summary ->>>>>>>>>{role.capitalize()}: ->>>>> {response}")
            
            # for msg in messages:
            #     role=msg.role
            #     content=msg.content[0].text.value
            #     print(f"summary ->>>>>>>>>{role.capitalize()}: ->>>>> {content}")
        
        return summary

    
if __name__== "__main__":
    main()
    