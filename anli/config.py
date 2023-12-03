import logging
import warnings
import yaml
import os
from huggingface_hub import hf_hub_download
from guidance import models, instruction
from contextlib import contextmanager
from .utils import RedisVectorStoreForJSON

# Define package metadata, Constants
APP_NAME = 'Python-ANLI'  # this will be used as the AppName of the package
ORGANIZATION = 'ANLI'  # this will be used as appauthor in appdirs


class BaseConfig:
    """Base configuration class for the package"""

    def __init__(self, config_file='config.yaml'):
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            warnings.warn(f"Config file not found: {config_file}. Using default config.")
            self.config = {"llm_chat": {"type": "LlamaCpp"},
                           "llm_completion": {"type": "LlamaCpp"},
                           "redis": {"url": "redis://localhost:6379"}}


class LLMInterface(BaseConfig):
    """
    Setup LLM backend engines.
    """

    # Define the default models, can be overridden by config.yaml
    DEFAULT_MODEL_IDENTIFIER = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
    DEFAULT_MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    DEFAULT_MODEL_CTX = 4096

    def __init__(self, config_file='config.yaml'):
        super().__init__(config_file)
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
                return models.LlamaCppChat(model_path, n_gpu_layers=int(backend_config.get('n_gpu_layers', 0)),
                                           n_ctx=self.DEFAULT_MODEL_CTX)
            else:
                logging.debug(f"loading completion model: {identifier}-{filename}")
                return models.LlamaCpp(model_path, n_gpu_layers=int(backend_config.get('n_gpu_layers', 0)),
                                       n_ctx=self.DEFAULT_MODEL_CTX)


class RedisConfig(BaseConfig):
    """
    Setup Redis backend engines.
    """

    def __init__(self, config_file='config.yaml'):
        super().__init__(config_file)
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
