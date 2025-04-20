from dotenv import dotenv_values, load_dotenv

load_dotenv()

secrets = dotenv_values(".env_dev")
