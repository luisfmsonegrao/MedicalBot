# DATADOCTOR AI AGENT

Datadoctor is an python-built agentic AI chatbot that uses `claude sonnet 3` to:
  - predict patient outcomes based on input feature values;
  - answer natural language questions about patients' medical records;
  - retrieve and aggregate anonymized patient data.

  ## Table of Contents
  - [Repo Contents](#Repo-contents)
  - [Detailed description](#detailed-description)
  - [Patient outcome classification model](#Patient-outcome-classification-model)

  ### Repo contents
  - the DataDoctor agentic AI chatbot source code is in the `src` folder
  - the folder `scripts` contains utility scripts used e.g. to train the predictive model, clean and upload data, etc.
  - the `notebooks` folder contains several jupyter notebooks used for various ends, such as exploring the dataset or testing the agent's functionalities


  ### Detailed description

  Datadoctor is an agentic AI Chatbot with several features:
  - predict patient outcomes for Chronic Obstructive Pulmonary Disease class, leveraging an extensive anonymized `patient_data` dataset. This is achieved with a Decision Tree Classifier.
  - answer natural language questions about patients' medical history, leveraging an extensive database of textual patient medical records.
  - retrieve and aggregate anonymized medical data leveraging an extensive anonymized `patient_data` dataset.
  - a `Gradio` GUI allows users to interact with the agent by writing natural language queries in a text box. It allows users to provide feedback on the quality of the agent's answers.


  ### Patient outcome classification model

  A `scikit-learn` Decision Tree Classifier was trained on the `patient_data` dataset using a subset of it's features to predict the class of Chronic Obstructive Pulmonary Disease for a given patient. 
  ANOVA, Chi-Squared and other hypothesis tests revealed that none of the features in the dataset actually has significant discriminative power in identifying the class of Chronic Obstructive Pulmonary Disease.
  As such, no further effort was spent in improving the classification model, e.g. through model-selection, cross-validation or hyperparameter tuning. Furthermore, only features 'age', 'sex', 'smoker' and 'bmi'     were included in the model, to simplify subsequent efforts.
  
  
