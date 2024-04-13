from enum import Enum


class GPTDefaults:
    GPTTypes = Enum("GPTTypes", ["NONE", "COMPLETION", "CHAT_COMPLETION"])
    gpt_models = {"text-davinci-003": (0.02, 0.02, GPTTypes.COMPLETION, 4096),
                  "gpt-3.5-turbo-instruct": (0.0010, 0.0020, GPTTypes.COMPLETION, 4096),
                  "gpt-3.5-turbo-1106": (0.0015, 0.0020, GPTTypes.CHAT_COMPLETION, 16385),
                  "gpt-4": (0.03, 0.06, GPTTypes.CHAT_COMPLETION, 8192)}


    @classmethod
    def get_model_data(cls, engine):
        if not GPTDefaults.gpt_models.get(engine):
            return "NONE", 0, 0, cls.GPTTypes.NONE, 0

        return engine, *cls.gpt_models[engine]

    @classmethod
    def get_available_models(cls):
        return cls.gpt_models.keys()