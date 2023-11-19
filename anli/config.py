import warnings
import yaml
import os
from huggingface_hub import hf_hub_download

# Define package metadata, Constants
APP_NAME = 'Python-ANLI'  # this will be used as the AppName of the package
ORGANIZATION = 'ANLI'  # this will be used as appauthor in appdirs


class Config:

    # Define the default models, can be overridden by config.yaml
    DEFAULT_MODEL_IDENTIFIER = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
    DEFAULT_MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

    def __init__(self, config_path='config.yaml'):
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                self.data = yaml.load(file, Loader=yaml.FullLoader)
        else:
            warnings.warn(f"Config file not found: {config_path}. Using default config.")
            self.data = {"llm_backend": {"type": "LlamaCpp"}}

    def get_model_path(self):
        # data_dir = appdirs.user_data_dir(Config.APP_NAME, Config.ORGANIZATION)
        model_path = self.data.get('llm_backend', {}).get('model_path', '')

        if model_path and os.path.exists(model_path):
            return model_path

        # Default to using identifier and filename if path is not provided
        identifier = self.data.get('llm_backend', {}).get('identifier', self.DEFAULT_MODEL_IDENTIFIER)
        filename = self.data.get('llm_backend', {}).get('filename', self.DEFAULT_MODEL_FILENAME)

        # model_path = hf_hub_download(repo_id=identifier, filename=filename, cache_dir=data_dir)
        model_path = hf_hub_download(repo_id=identifier, filename=filename)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        return model_path


# Example usage:
# config = Config('config.yaml')
# model_path = config.get_model_path()
# print(model_path)
