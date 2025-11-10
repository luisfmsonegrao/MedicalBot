import mlflow
from mlflow.tracking import MlflowClient
from config import MODEL_NAME, EXPERIMENT_NAME

client = MlflowClient()

def get_best_run():
    exp = client.get_experiment_by_name(EXPERIMENT_NAME) #get experiment data
    runs = client.search_runs(exp.experiment_id,order_by=["metrics.accuracy DESC"]) #find all runs sorted by decreasing accuracy
    return runs[0] #return best run

def register_new_model(run_id):
    model_uri = f"runs:/{run_id}/model"
    return mlflow.register_model(model_uri,MODEL_NAME)


def promote_model(run,registered_model):
    acc = run.data.metrics["accuracy"]
    model_version = registered_model.version
    prod_models = [m for m in client.get_latest_versions(MODEL_NAME, stages=["Production"])]
    if prod_models:
        current_acc = float(prod_models[0].tags.get("accuracy", 0))
        if acc > current_acc: # Better than current production model
            client.transition_model_version_stage(MODEL_NAME, model_version, "Production", archive_existing_versions=True)
            client.set_model_version_tag(MODEL_NAME, model_version, "accuracy", str(acc))
    else: # First production model
        client.transition_model_version_stage(MODEL_NAME, model_version, "Production")
        client.set_model_version_tag(MODEL_NAME, model_version, "accuracy", str(acc))


if __name__ == "__main__":
    best_run = get_best_run()
    registered_model = register_new_model(best_run.info.run_id)
    promote_model(best_run,registered_model)


