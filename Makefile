PYTHON = python 
POETRY = poetry 

.PHONY: clean help run install-mlflow install-ui install-agent install help git-push register_model deploy_model


all: help

install: install-agent install-ui

install-agent:
	$(POETRY) install --no-root

install-ui: 
	$(POETRY) install --only ui --no-root

install-mlflow:
	cd mlflow-project && $(POETRY) install --no-root

run:
	$(POETRY) run $(PYTHON) -m src.agent_ui.medicalbot_ui

train_model: 
	cd mlflow-project && $(POETRY) run mlflow run . -e train --env-manager=local -P max_depth=$(MAX_DEPTH) -P criterion=$(CRITERION)  --experiment-name "COPD_classifier_experiments"

register_model:
	cd mlflow-project && $(POETRY) run mlflow run . -e register_promote --env-manager=local

deploy_model:
	cd mlflow-project && $(POETRY) run mlflow run . -e deploy --env-manager=local


#test:

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.gradio')]"
	$(PYTHON) -c "import pathlib; [f.unlink() for f in pathlib.Path('.').rglob('*.pyc')]"

git-push: clean
	@if not defined MSG ( \
		echo Please provide a commit message: make git-push MSG="Your message"; \
		exit /b 1 \
	)
	@git add .
	@git commit -m "$(MSG)"
	@for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do git push origin %%b

help:
	@echo "Available targets:"
	@echo "  install  - Install dependencies via poetry"
	@echo "  run      - Run the application"
	@echo "  clean    - Remove temporary files"
	@echo "  help     - Show help text"

