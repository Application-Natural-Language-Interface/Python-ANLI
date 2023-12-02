import redis
import json
from redisvl.llmcache import SemanticCache
from jsonpath_ng.ext import parse
from jsonpath_ng import Index, Child
from uuid import uuid4


class RedisVectorStoreForJSON:
    def __init__(self, index_name, js_paths, default_semantic_distance_threshold=0.1,
                 redis_url="redis://localhost:6379"):
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.index_name = index_name
        self.default_semantic_distance_threshold = default_semantic_distance_threshold
        self.vector_index = SemanticCache(
            name=f"{index_name}_vector_index",                     # underlying search index name
            prefix=f"{index_name}_vector_index:item",              # redis key prefix
            redis_url=redis_url,  # redis connection url string
            distance_threshold=self.default_semantic_distance_threshold               # semantic distance threshold
        )

    def upsert_item(self, json_data: dict,
                    json_prompt_paths: [str] = None,
                    response_relative_position: int = None,
                    json_data_id: str = None,
                    index_path: str = '$'):
        """
        upsert a JSON object in Redis and index its vector representations
        :param json_data: The JSON object to store
        :param json_prompt_paths: The paths to extract prompts from the JSON object and index. If None, skip indexing
        step. Setting it to None can be useful for update or store JSON values without changing the index.
        :param response_relative_position: The relative position of the response to the prompt. Defaults to None,
        which will store an empty string as the response.
        :param json_data_id: The ID of the JSON object. If None, generate a UUID. If you want to update an existing
        object, you need to specify the ID.
        :param index_path: The path to store the JSON object in Redis. Defaults to '$' (root). If need to update a
        subpath of the JSON object, specify the path here.
        :return: None
        """
        if json_data_id is None:
            json_data_id = str(uuid4())
        self.client.json().set(f"{self.index_name}-{json_data_id}", index_path, json_data)
        # Adding the item to the tracking set
        self.client.sadd(f"{self.index_name}-collections", json_data_id)
        if json_prompt_paths is not None:
            for prompt_path in json_prompt_paths:
                pairs = self.extract_prompt_response_pairs(json_data, prompt_path,
                                                           response_relative_position=response_relative_position)
                for prompt, response in pairs:
                    self.vector_index.store(prompt=prompt,
                                            response=response,
                                            metadata={"name": f"{self.index_name}-{json_data_id}",
                                                      "path": f"{index_path}.{prompt_path}"})

    @staticmethod
    def extract_prompt_response_pairs(json_data, prompt_path, response_relative_position=None):
        """
        Extracts pairs of prompts and responses from a given JSON structure based on provided JSONPath for prompts.

        Parameters:
        - json_data: The JSON data containing the conversation. We are assuming the JSON structure is an OpenAI messages JSON format, i.e.:
        [
            {role: "patient", content: "I'm feeling unwell..."},
            {role: "doctor", content: "What symptoms..."},
            {role: "patient", content: "I have a headache..."}
            # ... more conversation entries ...
        ]
        - prompt_path: JSONPath expression to extract prompts. Noted that the role needs to match what's in the JSON
        data. E.g. $.conversation[?(@.role == 'patient')].content. Hints: you can give your JSON to ChatGPT or other
        LLMs to generate the JSONPath expression and modify this function to suit your special needs if you are using
        a different JSON structure.
        - response_relative_position: Relative position of response to the prompt in the conversation array.
        If None, only prompts are extracted, and responses are set to an empty string.

        Returns:
        - A list of tuples (prompt, response).
        """
        prompt_expr = parse(prompt_path)
        prompts = [match for match in prompt_expr.find(json_data)]

        pairs = []
        for prompt in prompts:
            # Extract prompt text
            prompt_text = prompt.value

            # Check if response position is provided
            if response_relative_position is not None:
                conversation_index = prompt.full_path.left.right.index
                response_index = conversation_index + response_relative_position
                response_path = Child(prompt.full_path.left.left, Index(response_index))
                response_expr = parse(str(response_path))
                response_matches = response_expr.find(json_data)

                response_content = response_matches[0].value.get('content', '') if response_matches else ''
            else:
                # If no response position is provided, set response to empty
                response_content = ''

            pairs.append((prompt_text, response_content))

        return pairs


    def search_item(self, query, num_results=1, semantic_distance_threshold=None):
        # Check the cache again to see if new answer is there
        self.vector_index.check(prompt=query, num_results=num_results,)
        return self.client.json().get(f"{self.index_name}-{json_data_id}", '$')

    def __len__(self):
        return self.client.scard(f"{self.index_name}-collections")


    def append_item(self, json_paths, json_data, index_path='$'):
        self.client.json().arrappend(self.index_name, index_path, json_data)
        for path in json_paths:
            jsonpath_expr = jsonpath_ng.parse(path)
            for match in jsonpath_expr.find(json_data):
                content = match.value
                self.vector_index.store(prompt=content, response=f"{index_path}.{str(match.full_path)}")

    def _vectorize_content(self, content):
        return self.embedder.embed(content)

    def _extract_and_vectorize(self, json_data, reference):
        vectors = []
        for path in self.vector_paths:
            jsonpath_expr = jsonpath_ng.parse(path)
            for match in jsonpath_expr.find(json_data):
                content = match.value
                location = json.dumps({"reference": reference, "path": str(match.full_path)})
                vector = self._vectorize_content(content)
                vectors.append({"vector": vector, "location": location})
        return vectors

    def store_json(self, json_data, reference):
        vectors = self._extract_and_vectorize(json_data, reference)
        for vector_data in vectors:
            self.client.json().set(f"{self.index_name}:{reference}", "$", vector_data)

    def search_vectors(self, query, top_k=3):
        query_vector = self._vectorize_content(query)
        # Add logic to search for similar vectors in Redis
        # Return top_k results along with their locations

# Usage example
vector_paths = ["$.conversation[?(@.role == 'patient')].content"]
store = RedisVectorStoreForJSON("redis://localhost:6379", "patient_utterances", vector_paths, "sentence-transformers-model-name")

user_chat = {
    "patient_profile": "Patient background...",
    "conversation": [
        {"role": "patient", "content": "I'm feeling unwell..."},
        {"role": "doctor", "content": "What symptoms..."},
        {"role": "patient", "content": "I have a headache..."}
        # ... more conversation entries ...
    ]
}

store.store_json(user_chat, "chat1")
# For searching similar vectors
results = store.search_vectors("I have a fever", top_k=5)
