import logging
import warnings
import yaml
import os
from huggingface_hub import hf_hub_download
from guidance import models, instruction
from contextlib import contextmanager

# Define package metadata, Constants
APP_NAME = 'Python-ANLI'  # this will be used as the AppName of the package
ORGANIZATION = 'ANLI'  # this will be used as appauthor in appdirs


class Config:
    """
    Setup backend engines.
    """

    # Define the default models, can be overridden by config.yaml
    DEFAULT_MODEL_IDENTIFIER = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
    DEFAULT_MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    DEFAULT_MODEL_CTX = 4096

    def __init__(self, config_path='config.yaml'):
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            warnings.warn(f"Config file not found: {config_path}. Using default config.")
            self.config = {"llm_chat": {"type": "LlamaCpp"}, "llm_completion": {"type": "LlamaCpp"}}
        # use dummy context by default except for OpenAI:
        self.unified_instruction = self.dummy_context
        # Load the model based on the configuration
        self.model_chat = self.load_model("llm_chat")
        self.model_completion = self.load_model("llm_completion")

    @contextmanager
    def dummy_context(self):
        yield

    def load_model(self, mode):
        # Determine which model class to use based on config
        backend_config = self.config.get(mode, {})
        backend_type = backend_config.get('type')

        if backend_type == 'Transformers':
            if mode == "llm_chat":
                logging.debug(f"loading chat model: {backend_config['model']}")
                return models.TransformersChat(backend_config['model'])
            else:
                logging.debug(f"loading completion model: {backend_config['model']}")
                return models.Transformers(backend_config['model'])
        elif backend_type == 'OpenAI':
            if mode == "llm_chat":
                logging.debug(f"loading chat model: {backend_config['model']}")
                return models.OpenAI(backend_config['model'], api_key=backend_config['api_key'])
            else:
                # if we use OpenAI for completion, we need to use the instruction context:
                self.unified_instruction = instruction
                logging.debug(f"loading completion model: {backend_config['model']}")
                return models.OpenAI(backend_config['model'], api_key=backend_config['api_key'])
        else:
            if backend_type != 'LlamaCpp':
                warnings.warn(f"Unsupported LLM backend type: {backend_type}. Using default: LlamaCpp")
            identifier = backend_config.get('identifier', self.DEFAULT_MODEL_IDENTIFIER)
            filename = backend_config.get('filename', self.DEFAULT_MODEL_FILENAME)
            model_path = hf_hub_download(repo_id=identifier, filename=filename)
            if mode == "llm_chat":
                logging.debug(f"loading chat model: {identifier}-{filename}")
                # return models.LlamaCppChat(model_path, n_gpu_layers=-1, main_gpu=1, n_ctx=self.DEFAULT_MODEL_CTX)
                return models.LlamaCppChat(model_path, n_ctx=self.DEFAULT_MODEL_CTX)
            else:
                logging.debug(f"loading completion model: {identifier}-{filename}")
                # return models.LlamaCpp(model_path, n_gpu_layers=-1, main_gpu=1, n_ctx=self.DEFAULT_MODEL_CTX)
                return models.LlamaCpp(model_path, n_ctx=self.DEFAULT_MODEL_CTX)

    # def process_input(self, input_text):
    #     # Ensures the model is loaded
    #     if self.model is None:
    #         raise Exception("Model is not loaded. Please check the configuration.")
    #
    #     if self.mode == 'chat':
    #         from guidance import system, user, assistant
    #
    #         with system():
    #             response = self.model + "You are a helpful assistant."
    #
    #         with user():
    #             response += f'{input_text} '
    #
    #         with assistant():
    #             response += gen("answer", stop=".")
    #
    #     elif self.mode == 'instruct':
    #         from guidance import instruction
    #
    #         with instruction():
    #             response = self.model + f'{input_text} '
    #         response += gen(stop=".")
    #     else:  # self.mode == 'completion'
    #         response = self.model + f'{input_text} ' + gen(stop='.')
    #
    #     # Further processing could include parsing the response for intents, entities, etc.
    #     # ...
    #
    #     return response

        # Process the input using the loaded model
        # The actual processing method may depend on the model you have
        # results = self.model.process(input_text)

        # Additional processing to parse intents and entities can be added here
        # This is placeholder logic and should be customized based on model output
        # intents = parse_intents(results)
        # entities = parse_entities(results)

        # Here you would return structured data based on intents and entities
        # return {
        #     'intents': intents,
        #     'entities': entities,
        # }


# Example usage:
# import datetime
# a = datetime.datetime.now()
# nlu_interface = NLUInterface(config_path='config.yaml')
# prompt = "What's the weather like today?"
# nlu_results = nlu_interface.process_input(prompt)
# b = datetime.datetime.now()
# c = b - a
# print(nlu_results)
# print(c.total_seconds())
