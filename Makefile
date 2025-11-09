PYTHON = python 
POETRY = poetry 

.PHONY: clean help run install help git-push


all: help

install: 
	$(POETRY) install --only ui --no-root

run:
	$(POETRY) run $(PYTHON) -m src.agent_ui.medicalbot_ui

#test:

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.gradio')]"
	$(PYTHON) -c "import pathlib; [f.unlink() for f in pathlib.Path('.').rglob('*.pyc')]"
	if exist poetry.lock del /F /Q poetry.lock

git-push: clean
	@if not defined MSG ( \
		echo Please provide a commit message: make git-push MSG="Your message"; \
		exit /b 1 \
	)
	@git add .
	@git commit -m "$(MSG)"
	@for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
	echo $(BRANCH)
	git push origin $(BRANCH)

help:
	@echo "Available targets:"
	@echo "  install  - Install dependencies via poetry"
	@echo "  run      - Run the application"
	@echo "  clean    - Remove temporary files"
	@echo "  help     - Show help text"

