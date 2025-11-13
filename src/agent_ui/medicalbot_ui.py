import gradio as gr
import requests
from .ui_config import API_KEY, QUERY_API_URL, FEEDBACK_API_URL
import pandas as pd
import uuid

headers = {"api-key": API_KEY}

query_id_map = {}


def chat_fn(user_message, session_id, history):
    """
    Send message to Lambda and return reply.
    """
    query_id = str(uuid.uuid4())
    r = requests.post(QUERY_API_URL, headers=headers, json={"session_id": session_id, "query_id": query_id, "query": user_message})
    data = r.json()
    answer = data.get("answer", "Error")
    answer_text = answer.get('text')
    answer_data = answer.get('data')
    if answer_data:   
        answer_text, answer_data = format_answer(answer_text,answer_data)
    history.append((user_message, answer_text))
    query_id_map[len(history) - 1] = query_id
    return history, history, answer_data

def format_answer(answer_text,answer_data):
    """
    Format answers that should be presented in tabular format.
    """
    answer_df = pd.DataFrame(answer_data)
    answer_str = f"Here is the data for query {answer_text}:"
    return answer_str, answer_df


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
    """
    Define Gradio App
    """
    session_id = gr.State(str(uuid.uuid4()))
    gr.Markdown("# 👩‍⚕️🩺 MedicalBot")
    chatbot = gr.Chatbot()
    dataframe = gr.DataFrame(label="Results Table", interactive=True)
    msg = gr.Textbox(placeholder="Ask something...")
    msg.submit(chat_fn, [msg, session_id, chatbot], [chatbot, chatbot, dataframe])
    chatbot.like(feedback_fn)

if __name__ == "__main__":
    demo.launch(share=True)



