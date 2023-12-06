from huggingface_hub import hf_hub_download
from guidance import models
from langchain.llms import LlamaCpp as LC_LlamaCpp
from llama_index.llms import LlamaCPP as LI_LlamaCpp
from anli.config import DEFAULT_MODEL_IDENTIFIER, DEFAULT_MODEL_FILENAME

class CombinedLlamaCpp:
    def __init__(self, model_path,
                 lc_kwargs=None,
                 li_kwargs=None,
                 model_kwargs=None,
                 **kwargs):
        # The LangChain loader is most complicated, so we do it first:
        klc = kwargs.copy()
        if model_kwargs is not None:
            klc["model_kwargs"] = model_kwargs
        else:
            klc["model_kwargs"] = {}
        klc["model_path"] = model_path
        if lc_kwargs is not None:
            klc.update(lc_kwargs)
        self.LC_llm = LC_LlamaCpp(**klc)

        dummy_model_path = hf_hub_download(repo_id=DEFAULT_MODEL_IDENTIFIER, filename=DEFAULT_MODEL_FILENAME)

        if li_kwargs is not None:
            kli = li_kwargs
        else:
            kli = {}
        kli["model_kwargs"] = {"n_gpu_layers": 0}
        # We will first load a dummy model on cpu to get the model config
        self.LI_llm = LI_LlamaCpp(model_path=dummy_model_path, **kli)
        # Then we will replace it with the actual model on the gpu:
        del self.LI_llm._model
        self.LI_llm._model = self.LC_llm.client

        # guidance can load model object directly:
        self.GU_llm = models.LlamaCpp(self.LC_llm.client)
        self.GU_chat = models.LlamaCppChat(self.LC_llm.client)
