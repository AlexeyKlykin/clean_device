build:
	@docker image build -t clean_device/python:bot .

run:
	@docker run --name bot_cont -d -t clean_device/python:bot

clean:
	@docker container stop bot_cont &
	@docker container rm bot_cont

all_test:
	uv run pytest -vv

run_bot:
	uv run main.py

update_readme:
	tree -f -I "__pycache__|.pyc|__init__.py" -P "*.py" >> README.md 

