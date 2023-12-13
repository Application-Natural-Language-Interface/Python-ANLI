class StreamSentence:
    """
    A class to process text streams and send complete sentences or meaningful phrases.

    This class is designed to be used in a streaming context where text data comes in chunks.
    It assembles these chunks into complete sentences or phrases, based on punctuation and
    checks for at least one space in the chunk to determine completeness.

    Attributes:
        buffer (str): A buffer to hold incoming text chunks.
        send (function): A function that handles the sending of complete text chunks.

    Methods:
        process_chunk(chunk): Processes a single chunk of text from the stream.
        end_stream(): Handles any remaining text after the stream ends and sends a "<END>" signal.

    # Example usage
    def send(text):
        # Replace this function with your actual sending logic
        print(f"Sending: {text}")

    stream_processor = StreamSentence(send)

    # Assuming `chain.stream("ice cream")` is your stream generator
    for chunk in chain.stream("ice cream"):
        stream_processor.process_chunk(chunk)

    stream_processor.end_stream()
    """
    def __init__(self, send_function, end_string: str="<END>"):
        """
        Initializes the StreamProcessor with a specified send function.

        Args:
            send_function (function): A function that will be used to send the processed text.
            end_string (string): A string to be sent to indicate end of streaming. Default: <END>
        """
        self.buffer = ""
        self.send = send_function
        self.end_string = end_string

    @staticmethod
    def is_valid_chunk(chunk):
        """
        Determines if a text chunk is valid for sending based on its content.

        A chunk is considered valid if it contains at least one space, indicating it being more
        than a single short word or abbreviation. So "Hi John" or "Hold on" are valid.

        Args:
            chunk (str): The text chunk to be evaluated.

        Returns:
            bool: True if the chunk is valid, False otherwise.
        """
        return ' ' in chunk

    def process_chunk(self, chunk):
        """
        Processes a chunk of text, appending it to the buffer and sending complete sentences.

        This method should be called for each chunk of text received from the stream.
        It checks for punctuation marks to determine the end of sentences or phrases,
        and sends them using the send function if they're valid.

        Args:
            chunk (str): A chunk of text from the stream.
        """
        self.buffer += chunk
        # Define punctuation marks where splitting can occur
        punctuation_marks = '.!?,;:'

        while any(mark in self.buffer for mark in punctuation_marks):
            # Find the earliest punctuation mark to split
            split_points = [self.buffer.find(mark) for mark in punctuation_marks if mark in self.buffer]
            split_point = min(split_points)

            # Extracting the sentence or phrase
            sentence = self.buffer[:split_point+1].strip()
            if self.is_valid_chunk(sentence):
                self.send(sentence)
                self.buffer = self.buffer[split_point+1:].strip()
            else:
                break  # Avoids splitting too short phrases

    def end_stream(self):
        """
        Finalizes the stream processing.

        This method sends any remaining text in the buffer as a final chunk,
        and then sends a "<END>" signal to indicate the end of the stream.
        """
        # Sending any remaining text in the buffer
        if self.buffer.strip():
            self.send(self.buffer.strip())

        # Sending the "<END>" string
        self.send(self.end_string)

