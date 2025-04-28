build:
	@docker image build -t clean_device/python:bot .

run:
	@docker run --name bot_cont -d -t clean_device/python:bot
