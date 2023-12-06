import logging
import warnings
import yaml
import os
from contextlib import contextmanager

# Define package metadata, Constants
APP_NAME = 'Python-ANLI'  # this will be used as the AppName of the package
ORGANIZATION = 'ANLI'  # this will be used as appauthor in appdirs

# Define the default models, can be overridden by config.yaml
DEFAULT_MODEL_IDENTIFIER = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
DEFAULT_MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
DEFAULT_MODEL_CTX = 4096
DEFAULT_N_GPU_LAYERS = 0

class BaseConfig:
    """Base configuration class for the package"""

    def __init__(self, config_file='config.yaml', config=None):
        if config is not None:
            self.config = config
        elif os.path.exists(config_file):
            with open(config_file, 'r') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            warnings.warn(f"Config file not found: {config_file}. Using default config.")
            self.config = {"llm": {"n_gpu_layers": 0},
                           "redis": {"url": "redis://localhost:6379"}}


class LLMInterface(BaseConfig):
    """
    Setup LLM backend engines.
    """


    def __init__(self, config_file='config.yaml', config=None):
        super().__init__(config_file=config_file, config=config)
        # Load the model based on the configuration
        self.model_path = None
        self.models = self.load_model()

    def load_model(self):
        from huggingface_hub import hf_hub_download
        from guidance import models, instruction
        # Determine which model class to use based on config
        backend_config = self.config.get('llm', {})
        backend_type = backend_config.get('type')

        if backend_type == 'Transformers':
            logging.debug(f"loading chat model: {backend_config['model']}")
            return models.TransformersChat(backend_config['model'])
        elif backend_type == 'OpenAI':
            return {
                "GU_instruct":models.OpenAI(backend_config['instruct'], api_key=backend_config['api_key']),
                "GU_chat":models.OpenAIChat(backend_config['chat'], api_key=backend_config['api_key']),
            }
        else:
            if backend_type != 'LlamaCpp':
                raise f"Unsupported LLM backend type: {backend_type}. Using default: LlamaCpp"
            from .llms import CombinedLlamaCpp
            from langchain.callbacks.manager import CallbackManager
            from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
            from llama_index.llms.llama_utils import (
                messages_to_prompt,
                completion_to_prompt,
            )
            # This is for LangChain
            # Callbacks support token-wise streaming
            callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

            identifier = backend_config.get('identifier', DEFAULT_MODEL_IDENTIFIER)
            filename = backend_config.get('filename', DEFAULT_MODEL_FILENAME)
            n_gpu_layers = backend_config.get('n_gpu_layers', DEFAULT_N_GPU_LAYERS)
            self.model_path = hf_hub_download(repo_id=identifier, filename=filename)
            return CombinedLlamaCpp(model_path=self.model_path,
                                    n_ctx=DEFAULT_MODEL_CTX,
                                    n_gpu_layers=n_gpu_layers,
                                    lc_kwargs={"callback_manager":callback_manager},
                                    li_kwargs={"messages_to_prompt":messages_to_prompt,
                                               "completion_to_prompt":completion_to_prompt})


class RedisConfig(BaseConfig):
    """
    Setup Redis backend engines.
    """

    def __init__(self, config_file='config.yaml', config=None):
        super().__init__(config_file=config_file, config=config)
        # Load the model based on the configuration
        self.redis_url = self.config.get("redis", {}).get("url", "redis://localhost:6379")
        if self.redis_url.startswith("rediss://"):
            import base64
            import tempfile
            cert_base64 = self.config["redis"].get('certificate_base64', None)
            if cert_base64 is None:
                raise ValueError("rediss:// url needs certificate_base64 in config.yaml")
            # Decode the base64-encoded certificate
            cert_decoded = base64.b64decode(cert_base64)
            # Write the certificate to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_cert_file:
                temp_cert_file.write(cert_decoded)
                self.ssl_ca_certs = temp_cert_file.name
                self.ssl = True
        else:
            self.ssl = False
            self.ssl_ca_certs = None

    def __del__(self):
        # Delete the temporary certificate file
        # TODO: it depends on the Python garbage collector which can be unpredictable.
        if self.ssl_ca_certs is not None:
            os.remove(self.ssl_ca_certs)
