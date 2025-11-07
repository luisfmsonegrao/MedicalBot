import gradio as gr
import requests
from .ui_config import API_KEY, API_URL

headers = {"api-key": API_KEY}

query_id_map = {}


def chat_fn(user_message, history):
    """Send message to Lambda and return reply"""
    r = requests.post(API_URL, headers=headers, json={"query": user_message})
    data = r.json()
    answer = data.get("answer", "Error")
    query_id = data.get("query_id", None)
    history.append((user_message, answer))
    query_id_map[len(history) - 1] = query_id

    return history, history

def feedback_fn(event_data: gr.LikeData):
    """
    Called when user clicks feedback buttons of an answer.
    """
    idx = event_data.index[0]
    like = event_data.liked
    query_id = query_id_map.get(idx)

    if query_id:
        payload = {
            "query_id": query_id,
            "feedback": "positive" if like else "negative"
        }
        #requests.post(f"{API_URL}/feedback", headers=headers, json=payload)
    else:
        print("Warning: no query_id found for index", idx)


with gr.Blocks() as demo:
    """Define Gradio App"""
    gr.Markdown("# 👩‍⚕️🩺 MedicalBot")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask something...")
    msg.submit(chat_fn, [msg, chatbot], [chatbot, chatbot])
    chatbot.like(feedback_fn)

if __name__ == "__main__":
    demo.launch(share=True)



