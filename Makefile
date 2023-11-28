setup: requirements.txt
	python -m venv .venv
	. ./.venv/bin/activate
	pip install --no-cache-dir -r requirements.txt
run: setup
	. ./.venv/bin/activate
	python main.py
all: setup run