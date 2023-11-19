from guidance import models, gen
from anli.config import Config


class NLUInterface:
    def __init__(self, config_path=None):
        # Load the configuration
        self.config = Config(config_path)
        self.mode = 'completion'
        # Load the model based on the configuration
        self.model = self.load_model()

    def load_model(self):
        # Determine which model class to use based on config
        backend_config = self.config.data.get('llm_backend', {})
        backend_type = self.config.data.get('llm_backend', {}).get('type')

        if backend_type == 'LlamaCpp':
            model_path = self.config.get_model_path()
            return models.LlamaCpp(model_path)
        elif backend_type == 'Transformers':
            model_name = backend_config['model_name']
            return models.Transformers(model_name)
        elif backend_type == 'OpenAI':
            model_name = backend_config['model_name']
            api_key = backend_config['api_key']
            # openai has 2 modes: chat, instruct
            self.mode = self.config.data.get('llm_backend', {}).get('mode', 'completion')
            return models.OpenAI(model_name, api_key=api_key)
        else:
            raise ValueError(f"Unsupported LLM backend type: {backend_type}")

    def process_input(self, input_text):
        # Ensures the model is loaded
        if self.model is None:
            raise Exception("Model is not loaded. Please check the configuration.")

        if self.mode == 'chat':
            from guidance import system, user, assistant

            with system():
                response = self.model + "You are a helpful assistant."

            with user():
                response += f'{input_text} '

            with assistant():
                response += gen("answer", stop=".")

        elif self.mode == 'instruct':
            from guidance import instruction

            with instruction():
                response = self.model + f'{input_text} '
            response += gen(stop=".")
        else:  # self.mode == 'completion'
            response = self.model + f'{input_text} ' + gen(stop='.')

        # Further processing could include parsing the response for intents, entities, etc.
        # ...

        return response

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
import datetime
a = datetime.datetime.now()
nlu_interface = NLUInterface(config_path='config.yaml')
prompt = "What's the weather like today?"
nlu_results = nlu_interface.process_input(prompt)
b = datetime.datetime.now()
c = b - a
print(nlu_results)
print(c.total_seconds())
