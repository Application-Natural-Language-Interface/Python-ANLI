import redis
from jsonpath_ng.ext import parse
from jsonpath_ng import Index, Child
from uuid import uuid4


class RedisVectorStoreForJSON:
    def __init__(self, index_name, default_semantic_distance_threshold=0.1,
                 redis_url="redis://localhost:6379", vectorizer=None, **kwargs):
        """
        Creates a RedisVectorStoreForJSON object.
        :param index_name:
        :param default_semantic_distance_threshold:
        :param redis_url:
        :param vectorizer: If None, use the default HFTextVectorizer ("sentence-transformers/all-mpnet-base-v2").
        Otherwise, use the provided vectorizer. We suggest to use "jinaai/jina-embeddings-v2-base-en" for English,
        but trust_remote_code=true is not supported yet. https://github.com/UKPLab/sentence-transformers/issues/2352
        """
        try:
            from redisvl.extensions.llmcache import SemanticCache
        except ImportError:
            raise ImportError(
                "`redisvl` package not found, please install it with "
                "`pip install redisvl`"
            )
        self.client = redis.Redis.from_url(redis_url, decode_responses=False, **kwargs)
        self.index_name = index_name
        self.redis_url = redis_url
        self.default_semantic_distance_threshold = default_semantic_distance_threshold
        self.vectorizer = vectorizer
        if self.vectorizer is None:
            self.vector_index = SemanticCache(
                name=f"{self.index_name}_vector_index",                     # underlying search index name
                prefix=f"{self.index_name}_vector_index:item",              # redis key prefix
                redis_url=self.redis_url,  # redis connection url string
                distance_threshold=self.default_semantic_distance_threshold,               # semantic distance threshold
                **kwargs
            )
        else:
            self.vector_index = SemanticCache(
                name=f"{self.index_name}_vector_index",                     # underlying search index name
                prefix=f"{self.index_name}_vector_index:item",              # redis key prefix
                redis_url=self.redis_url,  # redis connection url string
                vectorizer=self.vectorizer,
                distance_threshold=self.default_semantic_distance_threshold,               # semantic distance threshold
                **kwargs
            )

    def upsert_item(self, json_data: dict,
                    json_prompt_paths: [str] = None,
                    response_relative_position: int = None,
                    json_storage_id_suffix: str = None,
                    json_storage_path: str = '$'):
        """
        Inserts or updates a JSON object in Redis and optionally indexes its vector representations.
        Stores the JSON object in Redis at 'json_storage_path' in "{self.index_name}-{json_storage_id_suffix}" and
        indexes prompts and responses. The JSONPath for retrieving the prompt from RedisJSON is stored in the vector
        index under "path", and the JSON object ID is stored under "name".

        :param json_data: The JSON object to be stored.
        :param json_prompt_paths: A string or list of JSONPath expressions to extract prompts for indexing.
                                  If a string is provided, it is treated as a single path.
                                  If None, the indexing step is skipped.
                                  IMPORTANT: These paths are relative to the root of 'json_data'.
        :param response_relative_position: The relative position of the response to the prompt within a conversation.
                                           If set to None, responses are stored as empty strings. This is useful for
                                           indexing non-conversational JSON objects where a corresponding response
                                           may not exist.
        :param json_storage_id_suffix: This suffix is appended to index_name to construct a unique identifier for the
                                       JSON object in redis. A new UUID is generated if None.
                                       Specify this to update an existing object.
        :param json_storage_path: (Optional) Path in Redis where the JSON object is stored. Defaults to the root ('$').
                                  Specify this to store or update the JSON object at a specific subpath.
        :return: str - A message indicating the number of objects upserted.
        """
        # Set or generate the JSON object ID
        if json_storage_id_suffix is None:
            json_storage_id_suffix = str(uuid4())

        # Store the JSON object in Redis
        self.client.json().set(f"{self.index_name}-{json_storage_id_suffix}", json_storage_path, json_data)

        l = self.client.scard(f"{self.index_name}-collections")
        # Track the JSON object ID in a Redis set
        self.client.sadd(f"{self.index_name}-collections", json_storage_id_suffix)

        diff = self.client.scard(f"{self.index_name}-collections") - l

        # Convert json_prompt_paths to a list if it's a string
        if isinstance(json_prompt_paths, str):
            json_prompt_paths = [json_prompt_paths]

        # Index prompts and responses if paths are provided
        if json_prompt_paths is not None:
            count = 0
            for prompt_path in json_prompt_paths:
                # Extract prompt-response pairs based on the provided path and position
                pairs = self.extract_prompt_response_pairs(json_data, prompt_path,
                                                           response_relative_position=response_relative_position)
                # Store each pair's vector representation
                for prompt, response, p in pairs:
                    # Remove leading '$' from prompt_path if present
                    formatted_prompt_path = p.lstrip('$.')

                    # Merge paths
                    stored_path = f"{json_storage_path}.{formatted_prompt_path}"

                    self.vector_index.store(prompt=prompt,
                                            response=response,
                                            metadata={"name": f"{self.index_name}-{json_storage_id_suffix}",
                                                      "path": stored_path})
                    count += 1
            return f"Upsert {diff} objects to JSON_store and {count} prompts to vector_index."
        else:
            return f"Upsert {diff} objects to JSON_store, skipped vector_index."

    def search_item(self, query, num_results=1, return_fields=["response", "name", "path", "vector_distance"],
                    semantic_distance_threshold=None):
        if semantic_distance_threshold is not None:
            self.vector_index.set_threshold(semantic_distance_threshold)

        res = self.vector_index.check(prompt=query, num_results=num_results, return_fields=return_fields)

        if semantic_distance_threshold is not None:
            self.vector_index.set_threshold(self.default_semantic_distance_threshold)

        return res

    def set_default_semantic_distance_threshold(self, threshold):
        self.default_semantic_distance_threshold = threshold
        self.vector_index.set_threshold(threshold)

    def set_vectorizer(self, vectorizer):
        self.vectorizer = vectorizer
        self.vector_index = SemanticCache(
            name=f"{self.index_name}_vector_index",  # underlying search index name
            prefix=f"{self.index_name}_vector_index:item",  # redis key prefix
            redis_url=self.redis_url,  # redis connection url string
            vectorizer=self.vectorizer,
            distance_threshold=self.default_semantic_distance_threshold  # semantic distance threshold
        )

    def clear_index(self):
        """
        Clear the vector index.
        :return:
        """
        self.vector_index.clear()

    def delete_index(self):
        # Remove the underlying index
        self.vector_index.index.delete(drop=True)

    def __len__(self):
        return self.client.scard(f"{self.index_name}-collections")

    def __iter__(self):
        for key in self.client.smembers(f"{self.index_name}-collections"):
            yield key

    def __getitem__(self, item):
        return self.client.json().get(f"{self.index_name}-{item}")

    @staticmethod
    def extract_prompt_response_pairs(json_data, prompt_path, response_relative_position=None):
        """
        Extracts pairs of prompts and responses from a given JSON structure based on provided JSONPath for prompts.

        Parameters:
        - json_data: The JSON data containing the conversation. We are assuming the JSON structure is an OpenAI messages
         JSON format, i.e.:
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

            pairs.append((prompt_text, response_content, str(prompt.full_path)))

        return pairs

    @staticmethod
    def extract_utterances(redis_client, json_name, path, start_shift, end_shift):
        """
        Extracts a range of utterances from a RedisJSON object relative to the current index.

        :param redis_client: The Redis client instance.
        :param json_name: The name of the JSON object in Redis.
        :param path: The path to the current utterance in the RedisJSON object.
        :param start_shift: The start of the range relative to the current index.
        :param end_shift: The end of the range relative to the current index.
        :return: A list of utterances or None for indices out of boundary.
        """
        try:
            # Extract the base path and current index from the path
            path_parts = path.split('[')
            # Assuming index is in the rightmost part of the path
            current_index = int(path_parts[-1].split(']')[0])
            # everything before the last part is the base path
            base_path = '['.join(path_parts[:-1]).rstrip('.')

            # Fetch the conversation from the base path, since the path should have no wildcards,
            # this should return a list of 1
            conversation = redis_client.json().get(json_name, base_path)[0]

            # Calculate the range of indexes
            start_index, end_index = (max(current_index + start_shift, 0),
                                      min(current_index + end_shift, len(conversation)))

            # Extract the relevant utterances
            utterances = []
            for i in range(start_index, end_index):
                utterances.append(conversation[i])

            return utterances

        except IndexError as e:
            import warnings
            warnings.warn(f"Index out of boundary when extracting utterances: {e}")
            return []
