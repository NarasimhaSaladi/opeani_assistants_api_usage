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
    print(get_news("bitcoin"))

if __name__== "__main__":
    main()
    