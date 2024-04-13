import openai
from decouple import config
from tiktoken import encoding_for_model
from helpers.gpt_defaults import GPTDefaults

clientGPT = openai.OpenAI(api_key=config('OPENAI_API_KEY', default='no_key'))


class AllGPT(GPTDefaults):
    client = clientGPT

    # if a user is given on init, it will overwrite the response function user
    def __init__(self, engine="gpt-3.5-turbo-1106", verbose=False, user=None):
        self.engine, self.price_in, self.price_out, self.engine_type, self.context_window_size = self.get_model_data(
            engine)
        self.verbose = verbose
        self.user = user

        if self.engine_type == self.GPTTypes.NONE:
            raise ValueError("The engine type you chose doesn't exist.")

        try:
            self.tokenizer = encoding_for_model(self.engine)
        except KeyError as e:
            raise e

    def respond(self,
                completion_input,
                temperature: float = 0,
                best_of: int = 1,
                stop: str = "",
                # engine=None,
                max_tokens: int = config('OPENAI_MAX_TOKENS', default=150, cast=int),
                timeout: int = config('OPENAI_TIMEOUT', default=60, cast=int),
                user: str = config('OPENAI_USER', default='user'),
                frequency_penalty: float = 0,
                presence_penalty: float = 0,
                seed=None
                ):
        try:
            # we need to compress these parameters; seed will be optional for chat completion
            response = None
            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0
            finish = ""
            if self.engine_type == self.GPTTypes.CHAT_COMPLETION and type(completion_input) is list:
                result = self.client.chat.completions.create(
                    model=self.engine,
                    messages=completion_input,
                    temperature=temperature,
                    frequency_penalty=frequency_penalty,
                    max_tokens=max_tokens,
                    presence_penalty=presence_penalty,
                    seed=seed,
                    user=user
                )

                response = {
                    "content": result.choices[0].message.content,
                    "role": result.choices[0].message.role
                }

                prompt_tokens = result.usage.prompt_tokens
                completion_tokens = result.usage.completion_tokens
                total_tokens = result.usage.total_tokens
                finish = result.choices[0].finish_reason

            if self.engine_type == self.GPTTypes.COMPLETION and type(completion_input) is str:
                result = self.client.completions.create(
                    prompt=completion_input,
                    temperature=temperature,
                    best_of=best_of,
                    stop=stop,
                    model=self.engine,
                    max_tokens=max_tokens,
                    frequency_penalty=presence_penalty,
                    presence_penalty=frequency_penalty,
                    timeout=timeout,  # in seconds
                    user=user
                )
                response = result.choices[0].text
                finish = result.choices[0].finish_reason
                prompt_tokens = result.usage.prompt_tokens
                completion_tokens = result.usage.completion_tokens
                total_tokens = result.usage.total_tokens

            if self.verbose:
                print(
                    f"GENERATION METRICS: prompt - {prompt_tokens}, completion - {completion_tokens}, total - {total_tokens}")

            price = (prompt_tokens * self.price_in) + (completion_tokens * self.price_out)
            price = price / 1000

            return response, finish, price, total_tokens
        except openai.APIError as e:
            return f"{e.message}", "api error", 0, 0
        except openai.InternalServerError as e:
            return f"{e.message}", "service unavailable", 0, 0

    def evaluate(self, completion_input, completion_tokens=0):
        input_tokens = 0
        if self.engine_type == self.GPTTypes.COMPLETION:
            input_tokens = len(self.tokenizer.encode(completion_input))
        if self.engine_type == self.GPTTypes.CHAT_COMPLETION:
            input_tokens = self._evaluate_messages(completion_input)

        if self.verbose and self.context_window_size > (input_tokens + completion_tokens):
            print(f"Context window size for {self.engine} was surpassed. Please split you input.")

        estimated_price = (input_tokens * self.price_in) + (completion_tokens * self.price_out)
        estimated_price = estimated_price / 1000
        return input_tokens, estimated_price

    def _evaluate_messages(self, messages):
        # this is an estimate for the newer models with their chat format
        tokens_per_message = 3
        tokens_per_name = 1

        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(self.tokenizer.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3
        return num_tokens

    def split_context(self, text, window_size=2000, split_by_context_window=False, redundancy=0):
        tokenized_text = self.tokenizer.encode(text)

        if split_by_context_window:
            redundancy = 0
            window_size = self.context_window_size

        redundancy = window_size * redundancy
        if self.verbose and redundancy + window_size > self.context_window_size:
            print(f"Windows size is bigger than context window size for {self.engine}. Please lower the window size "
                  f"or the redundancy percentage.")

        if redundancy + window_size > self.context_window_size:
            window_size = self.context_window_size - redundancy

        windows_number = int(len(tokenized_text) / window_size) + (1 if len(tokenized_text) % window_size != 0 else 0)

        text_list = []
        for i in range(0, windows_number):
            text_list.append(tokenized_text[i * window_size:((i + 1) * window_size) + redundancy])

        text_list = [self.tokenizer.decode(text) for text in text_list]
        return text_list

    @staticmethod
    def chat_to_prompt(chat):
        if type(chat) is list:
            task = " ".join([msg["content"] for msg in chat if msg["role"] == "system" and not msg.get("name")])
            examples = "\n".join(
                f"\t{msg['name']}: {msg['content']}" for msg in chat if msg["role"] == "system" and msg.get("name"))
            user_context = " ".join([f"{msg['role']}: {msg['content']}" for msg in chat if msg["role"] == "user"])
            return f"EXAMPLES:\n{examples}\nTASK:\n{task}\n{user_context}\n"

        raise TypeError("Input should be of type list")


if __name__ == "__main__":
    example_messages = [
        {
            "role": "system",
            "content": "You are a helpful, pattern-following assistant that translates corporate jargon into plain English.",
        },
        {
            "role": "system",
            "name": "example_user",
            "content": "New synergies will help drive top-line growth.",
        },
        {
            "role": "system",
            "name": "example_assistant",
            "content": "Things working well together will increase revenue.",
        },
        {
            "role": "system",
            "name": "example_user",
            "content": "Let's circle back when we have more bandwidth to touch base on opportunities for increased leverage.",
        },
        {
            "role": "system",
            "name": "example_assistant",
            "content": "Let's talk later when we're less busy about how to do better.",
        },
        {
            "role": "user",
            "content": "This late pivot means we don't have time to boil the ocean for the client deliverable.",
        },
    ]

    for engine_name in GPTDefaults.get_available_models():
        completion = None

        all_gpt = AllGPT(engine_name)
        if GPTDefaults.gpt_models[engine_name][2] == GPTDefaults.GPTTypes.COMPLETION:
            completion = AllGPT.chat_to_prompt(example_messages)
        else:
            completion = example_messages

        print(engine_name, all_gpt.respond(completion, max_tokens=200, temperature=1))