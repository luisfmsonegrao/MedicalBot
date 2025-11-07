import gradio as gr
import requests
from .ui_config import API_KEY, QUERY_API_URL, FEEDBACK_API_URL

headers = {"api-key": API_KEY}

query_id_map = {}


def chat_fn(user_message, history):
    """Send message to Lambda and return reply"""
    r = requests.post(QUERY_API_URL, headers=headers, json={"query": user_message})
    data = r.json()
    answer = data.get("answer", "Error")
    query_id = data.get("query_id", "Error")
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
    if like is True:
        feedback = "positive"
    elif like is False:
        feedback = "negative"
    else:
        feedback = "NA"
    payload = {
        "query_id": query_id,
        "feedback": feedback
    }
    requests.post(FEEDBACK_API_URL, headers=headers, json=payload)


with gr.Blocks() as demo:
    """Define Gradio App"""
    gr.Markdown("# 👩‍⚕️🩺 MedicalBot")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask something...")
    msg.submit(chat_fn, [msg, chatbot], [chatbot, chatbot])
    chatbot.like(feedback_fn)

if __name__ == "__main__":
    demo.launch(share=True)



