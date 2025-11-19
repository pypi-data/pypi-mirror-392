import os
import dotenv
import yaml
import time

from enum import Enum
from pathlib import Path
from typing import Optional, Union
from pydantic import BaseModel

import openai
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.completion_usage import CompletionUsage

from aoai.profile import AOAIProfile, default_profile, reasoning_profile


class AOAIChatCompletionResponse(BaseModel):
    raw_response: ChatCompletion
    response_text: str
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    total_tokens: int
    execution_profile_name: str
    execution_start_time: float
    execution_end_time: float
    total_execution_time: float



class AOAIExecutor:
    def __init__(self, 
                 dotenv_path: str = ".env",
                 profiles_dir: str = "aoai_profiles",
                 default_profile_name: str = "default"):
        # load environment variables from .env file
        self.dotenv_path = Path(dotenv_path)
        print("Loading environment variables from:", self.dotenv_path.absolute())
        dotenv.load_dotenv(dotenv_path=self.dotenv_path)
        print("Initializing azure openai client...")
        self.client = openai.AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        # check authentication
        models = self.client.models.list()
        print("Azure OpenAI client initialized successfully.")
        # print available models
        available_models = [model for model in models.data if model.lifecycle_status=="generally-available"]
        print("Available models:")
        for model in sorted(available_models, key=lambda v: v.created_at):
            print(f" - {model.id}")
        # load profiles
        self.profiles_dir = Path(profiles_dir)
        print("Profiles directory set to:", self.profiles_dir.absolute())
        n_profiles = len(list(self.profiles_dir.glob("*.yaml")))
        print(f"Found {n_profiles} profile(s) in profiles directory.")
        if n_profiles == 0:
            self._initialize_default_profiles()
        print("Validating profiles...")
        self._validate_profiles()
        self.default_profile_name = default_profile_name
        print("Default profile name set to:", self.default_profile_name)
    
    def _initialize_default_profiles(self):
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        default_profile_path = self.profiles_dir / "default.yaml"
        profile_dict = default_profile.model_dump(exclude_unset=True)
        with open(default_profile_path, "w") as f:
            yaml.dump(profile_dict, f)
        print("Default profile created at:", default_profile_path.absolute())

        reasoning_profile_path = self.profiles_dir / "reasoning.yaml"
        profile_dict = reasoning_profile.model_dump(exclude_unset=True)
        with open(reasoning_profile_path, "w") as f:
            yaml.dump(profile_dict, f)
        print("Reasoning profile created at:", reasoning_profile_path.absolute())

    def _validate_profiles(self):
        for profile_path in self.profiles_dir.glob("*.yaml"):
            with open(profile_path, "r") as f:
                profile_dict = yaml.safe_load(f)
            profile = AOAIProfile.model_validate(profile_dict)
            print(f"Profile '{profile.name}' is valid.")

    def _load_profile(self, profile_name: str) -> AOAIProfile:
        profile_path = self.profiles_dir / f"{profile_name}.yaml"
        if not profile_path.exists():
            raise ValueError(f"Profile '{profile_name}' does not exist in profiles directory.")
        with open(profile_path, "r") as f:
            profile_dict = yaml.safe_load(f)
        profile = AOAIProfile.model_validate(profile_dict)
        return profile

    def _cvt_profile_into_chat_completion_params(self, profile: AOAIProfile) -> dict:
        params = {}
        params["model"] = profile.model
        if not profile.is_unset("temperature"):
            params["temperature"] = profile.temperature
        if not profile.is_unset("top_p"):
            params["top_p"] = profile.top_p
        if not profile.is_unset("frequency_penalty"):
            params["frequency_penalty"] = profile.frequency_penalty
        if not profile.is_unset("max_tokens"):
            params["max_tokens"] = profile.max_tokens
        if not profile.is_unset("reasoning_effort"):
            params["reasoning_effort"] = profile.reasoning_effort
        return params

    def execute_prompt_texts(
        self, 
        instruction_prompt: str,
        input_prompt: str,
        response_format: Optional[ResponseFormat] = None,
        profile_name: str = None,
        omit_raw_response: bool = False
    ) -> Union[tuple[ChatCompletion, AOAIChatCompletionResponse], AOAIChatCompletionResponse]:
        messages = []
        if instruction_prompt:
            messages.append(ChatCompletionSystemMessageParam(content=instruction_prompt, role="system"))
        if input_prompt:
            messages.append(ChatCompletionUserMessageParam(content=input_prompt, role="user"))
        return self.execute(
            messages=messages,
            response_format=response_format,
            profile_name=profile_name,
            omit_raw_response=omit_raw_response
        )

    def execute(self, messages: list[ChatCompletionMessageParam],
                response_format: Optional[ResponseFormat] = None,
                profile_name: str = None,
                omit_raw_response: bool = False) \
    -> Union[tuple[ChatCompletion, AOAIChatCompletionResponse], AOAIChatCompletionResponse]:
        # load profile
        if profile_name is None:
            profile_name = self.default_profile_name
        print("Using profile:", profile_name)
        profile = self._load_profile(profile_name)

        chat_params = self._cvt_profile_into_chat_completion_params(profile)
        if response_format is not None:
            chat_params["response_format"] = response_format

        start_time = time.time()
        print("Sending chat completion request...")
        response = self.client.chat.completions.create(
            messages=messages,
            **chat_params
        )
        end_time = time.time()
        total_execution_time = end_time - start_time
        print("Chat completion response received in {:.2f} seconds.".format(total_execution_time))
        
        input_tokens = 0
        output_tokens = 0
        reasoning_tokens = 0
        total_tokens = 0
        if response.usage is not None:
            token_usage: CompletionUsage = response.usage
            input_tokens = token_usage.prompt_tokens
            output_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
            if token_usage.completion_tokens_details is not None:
                if token_usage.completion_tokens_details.reasoning_tokens is not None:
                    reasoning_tokens = token_usage.completion_tokens_details.reasoning_tokens

        response_data = AOAIChatCompletionResponse(
            raw_response=response,
            response_text=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens,
            total_tokens=total_tokens,
            execution_profile_name=profile.name,
            execution_start_time=start_time,
            execution_end_time=end_time,
            total_execution_time=total_execution_time
        )
        
        if omit_raw_response:
            return response_data
        else:
            return response, response_data
        
    
if __name__ == "__main__":
    executor = AOAIExecutor()
    raw_response, response_data = executor.execute_prompt_texts(
        instruction_prompt="You are a helpful assistant.",
        input_prompt="What is best strategy to solve time series forecasting problems?",
        response_format=None,
        profile_name='reasoning',
        omit_raw_response=False
    )
    print(response_data)
    print(response_data.response_text)
    print(response_data.total_execution_time)
    print(response_data.input_tokens, response_data.output_tokens, response_data.reasoning_tokens,response_data.total_tokens)
