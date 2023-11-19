import yaml
import os


class Config:
    # Define package metadata, Constants
    APP_NAME = 'Python-ANLI'  # this will be used as the AppName of the package
    ORGANIZATION = 'ANLI'  # this will be used as appauthor in appdirs

    # Define the default models, can be overridden by config.yaml
    MODEL_IDENTIFIER = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
    MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

    # MODEL_IDENTIFIER = "TheBloke/Llama-2-7b-Chat-GGUF"
    # MODEL_FILENAME = "llama-2-7b-chat.Q6_K.gguf"

    def __init__(self, config_path='config.yaml'):
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                # If a config.yaml is provided, override the model defaults
                yaml_config = yaml.load(file, Loader=yaml.FullLoader)
                self.MODEL_IDENTIFIER = yaml_config.get('model', {}).get('identifier', Config.MODEL_IDENTIFIER)
                self.MODEL_FILENAME = yaml_config.get('model', {}).get('filename', Config.MODEL_FILENAME)
        else:
            # No config.yaml provided; use the default values
            self.MODEL_IDENTIFIER = Config.MODEL_IDENTIFIER
            self.MODEL_FILENAME = Config.MODEL_FILENAME


# Usage example:
# Instantiate the Config class and use properties as needed
# config = Config('config.yaml')
# print(config.MODEL_IDENTIFIER)
