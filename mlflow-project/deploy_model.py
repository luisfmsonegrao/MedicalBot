import mlflow
from mlflow.tracking import MlflowClient
import os
import joblib, json
from config import MODEL_NAME, DEPLOY_PATH

client = MlflowClient()

#get current production model
def get_production_model():
    model_uri = f"models:/{MODEL_NAME}/Production"
    return mlflow.sklearn.load_model(model_uri)

def get_model_metadata():
    prod_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
    if not prod_versions:
        raise ValueError("No Production model found in MLflow registry.")
    prod_model = prod_versions[0]
    version = prod_model.version
    run_id = prod_model.run_id
    metadata = {
        "model_name": MODEL_NAME,
        "version": version,
        "run_id": run_id    
    }
    return metadata

# Load model and save to joblib
def deploy_model(model):
    joblib.dump(model, os.path.join(DEPLOY_PATH,MODEL_NAME))

#save model metadata
def write_metadata(metadata):
    with open(os.path.join(DEPLOY_PATH,"model_metadata.json"),"w") as f:
        json.dump(metadata,f)

if __name__ == "__main__":
    model = get_production_model()
    metadata = get_model_metadata()
    deploy_model(model)
    write_metadata(metadata)


