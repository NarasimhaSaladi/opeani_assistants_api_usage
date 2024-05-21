# Import necessary libraries
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime
import os
import requests
import json
import openai
import streamlit as st

# Load environment variables
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Define model and client
model = "gpt-3.5-turbo-16k"
News_api_key = os.environ.get("NEWS_API_KEY")

# Define a function to get news based on a topic
def get_news(topic):
    url = f"https://newsapi.org/v2/everything?q={topic}&from=2024-04-20&sortBy=publishedAt&apiKey={News_api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            news_json = response.json()
            articles = news_json["articles"]
            processed_articles = []
            for article in articles:
                title_description = f"""
                Title: {article["title"]}
                Author: {article["author"]}
                Source: {article["source"]["name"]}
                Description: {article["description"]}
                URL: {article["url"]}
                """
                processed_articles.append(title_description)
            return processed_articles
        else:
            return []
    except requests.exceptions.RequestException as e:
        print("Error occurred during API Request", e)
        return []

# Define the AssistantManager class
class AssistantManager:
    thread_id = None
    assistant_id = None
    
    def __init__(self, model: str = model) -> None:
        self.client = openai
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

        if AssistantManager.assistant_id:
            self.assistant = self.client.Assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )

        if AssistantManager.thread_id:
            self.thread = self.client.Threads.retrieve(
                thread_id=AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.Assistants.create(
                name=name,
                instruction=instructions,
                tools=tools,
                model=self.model
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"ASS_id: {self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.Threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"thread_id: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.Threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content
            )

    def run_assistant(self, instructions):
        if self.thread and self.assistant:
            self.run = self.client.Threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions
            )

    def process_messages(self):
        if self.thread:
            messages = self.client.Threads.messages.list(thread_id=self.thread.id)
            summary = []
            for msg in messages['data']:
                role = msg['role']
                content = msg['content'][0]['text']['value']
                summary.append(f"{role.capitalize()}: {content}")
            self.summary = "\n".join(summary)
            return summary

    def call_required_func(self, req_actions):
        if not self.run:
            return
        tool_outputs = []
        for action in req_actions['tool_calls']:
            func_name = action["function"]["name"]
            arguments = json.loads(action['function']['arguments'])
            if func_name == "get_news":
                output = get_news(topic=arguments['topic'])
                final_string = "\n".join(output)
                tool_outputs.append({
                    "tool_call_id": action["id"],
                    "output": final_string
                })
            else:
                raise ValueError(f"Unknown function {func_name}")
        self.client.Threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=tool_outputs
        )

    def get_summary(self):
        return self.summary

    def wait_for_completed(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.Threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=self.run.id
                )
                if run_status.status == "completed":
                    self.process_messages()
                    break
                elif run_status.status == "requires_action":
                    self.call_required_func(
                        req_actions=run_status.required_action
                    )

    def run_steps(self):
        run_steps = self.client.Threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
        return run_steps

def main():
    manager = AssistantManager()

    # Streamlit interface
    st.title("News Summarizer")

    with st.form(key="user_input_form"):
        instructions = st.text_input("Enter a topic")
        submit_button = st.form_submit_button(label="Run Assistant")

        if submit_button:
            manager.create_assistant(
                name="News Summarizer",
                instructions="You are an expert in analyzing news",
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "get_news",
                        "description": "Get the list of articles for the news summarizer",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "topic": {
                                    "type": "string",
                                    "description": "The topic for the news e.g. bitcoin"
                                }
                            },
                            "required": ["topic"]
                        }
                    }
                }]
            )
            manager.create_thread()
            manager.add_message_to_thread(
                role="user",
                content=f"Summarize the news on this topic: {instructions}"
            )
            manager.run_assistant(instructions="Summarize the news")
            manager.wait_for_completed()

            summary = manager.get_summary()
            st.write(summary)

            st.text("Run Steps")
            st.code(manager.run_steps(), line_numbers=True)

if __name__ == "__main__":
    main()
