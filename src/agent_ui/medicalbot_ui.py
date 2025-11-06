import gradio as gr
import requests
from src.config import API_KEY, API_URL

headers = {"api-key": API_KEY}

def chat_fn(user_message,history):
    """Route queries and replies"""
    r = requests.post(API_URL, headers=headers, json={"query": user_message})
    answer = r.json().get("answer", "Error")
    history.append((user_message, answer))
    return history,history

with gr.Blocks() as demo:
    """Define Gradio App"""
    gr.Markdown("# 👩‍⚕️🩺 MedicalBot")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask something...")
    msg.submit(chat_fn, [msg, chatbot], [chatbot, chatbot])
    chatbot.like(None)

if __name__ == "__main__":
    demo.launch(share=True)



