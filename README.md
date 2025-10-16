# DATADOCTOR AI AGENT

Datadoctor is an python-built agentic AI chatbot that uses `claude sonnet 3` to:
  - predict patient outcomes based on input feature values;
  - answer natural language questions about patients' medical records;
  - retrieve and aggregate anonymized patient data.

  ## Table of Contents
  - [Repo Contents](#Repo-contents)
  - [Detailed description](#detailed-description)
  - [Patient outcome classification model](#Patient-outcome-classification-model)
  - [Question answering + RAG](#Question-answering-+-RAG)

  ### Repo contents
  - `\src` contains the DataDoctor agentic AI chatbot source code
  - `\scripts` contains scripts used e.g. to train the predictive model, clean and upload data, etc.
  - `\notebooks` contains several jupyter notebooks used for various ends, such as exploring the dataset or testing the agent's functionalities


  ### Detailed description

  Datadoctor is an agentic AI Chatbot with several features:
  - predict patient outcomes for Chronic Obstructive Pulmonary Disease class, leveraging an extensive anonymized `patient_data` dataset. This is achieved with a Decision Tree Classifier.
  - answer natural language questions about patients' medical history, leveraging an extensive database of textual patient medical records.
  - retrieve and aggregate anonymized medical data leveraging an extensive anonymized `patient_data` dataset.
  - a `Gradio` GUI allows users to interact with the agent by writing natural language queries in a text box. It allows users to provide feedback on the quality of the agent's answers.


  ### Patient outcome classification model
  
  The DataDoctor can access a trained Decision Tree Classifier to predict the class of Chronic Obstructive Pulmonary disease, based on user-provided feature values.
  A `scikit-learn` Decision Tree Classifier was trained on the `patient_data` dataset using a subset of it's features to predict the class of Chronic Obstructive Pulmonary Disease for a given patient. 
  ANOVA, Chi-Squared and other hypothesis tests revealed that none of the features in the dataset actually has significant discriminative power in identifying the class of Chronic Obstructive Pulmonary Disease.
  As such, no further effort was spent in improving the classification model, e.g. through model-selection, cross-validation or hyperparameter tuning. Furthermore, only features 'age', 'sex', 'smoker' and 'bmi'     were included in the model, to simplify subsequent efforts.

    - `preprocess_patient_data.py` was used to clean, filter and transform the dataset
    - `train_classification_model.py` was used to train the Decision Tree Classifier used by the DataDoctor agent.
    - the function `orchestrate` inside `orchestrator.py` defines the DataDoctor's behavior. Based on the foundation model's classification of the user query, the agent decides whether to call the Decision Tree Classifier.


  ### Question answering + RAG

  The DataDoctor can answer natural language questions about patients' medical history based on an extensive set of textual medical records.
  The records were cleaned, chunked, embedded with `amazon.titan-embed-text-v2:0` and uploaded to an Amazon Bedrock Knowledge Base.
  Upon routing a user question to the underlying foundation model, the DataDoctor first searches this vector database for relevant contextual information, then augments the user query with the retrieved context to aid the foundation model.

  - the medical record documents were cleaned with `clean_markdown_files.py` and `remove_duplicate_files.py`.
  - the function `orchestrate` inside `orchestrator.py` defines the DataDoctor's behavior. Based on the foundation model's classification of the user query, the agent decides whether to call the foundation model again to answer the user's question.
  
