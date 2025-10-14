import gradio as gr
import requests

API_URL = 'https://a83rxleacg.execute-api.us-east-1.amazonaws.com/datadoctor-chat'

def chat_fn(user_message,history):
    r = requests.post(API_URL, json={"query": user_message})
    answer = r.json().get("answer", "Error")
    history.append((user_message, answer))
    return history,history

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Bedrock RAG Chat via Lambda")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask something...")
    msg.submit(chat_fn, [msg, chatbot], [chatbot, chatbot])

if __name__ == "__main__":
    demo.launch(share=True)



