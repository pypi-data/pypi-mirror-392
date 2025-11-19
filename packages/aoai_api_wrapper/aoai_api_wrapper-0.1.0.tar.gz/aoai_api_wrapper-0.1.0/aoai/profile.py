from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Optional
from openai.types import ReasoningEffort


class AOAIProfile(BaseModel):
    name: str
    model: str
    temperature: Optional[float] = Field(default=None)
    top_p: Optional[float] = Field(default=None)
    frequency_penalty: Optional[float] = Field(default=None)
    max_tokens: Optional[int] = Field(default=None)
    reasoning_effort: Optional[ReasoningEffort] = Field(default=None)

    # validations:
    # - reasoning_effort and model compatibility
    #     - non gpt-5* models: reasoning_effort must be Omit
    #     - gpt-5: reasoning_effort must be one of ["low", "medium", "high"]
    #     - gpt-5-mini, gpt-5-nano: reasoning_effort must be one of ["minimal", "low", "medium", "high"]
    #     - gpt-5.1: reasoning_effort must be one of ["minimal", "low", "medium", "high", None]
    # - temperature between 0.0 and 2.0
    # - temperature and reasoning_effort compatibility
    #     - non gpt-5* models(means reasoning_effort is Omit): temperature can be any value between 0.0 and 2.0
    #     - gpt-5.1: if reasoning_effort is None, temperature can be any value between 0.0 and 2.0
    #     - gpt-5* with reasoning_effort set: temperature must be 1.0
    # - top_p between 0.0 and 1.0
    # - top_p and reasoning_effort compatibility
    #     - non gpt-5* models(means reasoning_effort is Omit): top_p can be any value between 0.0 and 1.0
    #     - gpt-5* with reasoning_effort set: top_p must be 1.0
    # - max_tokens between 1 and model's maximum context length
    # - frequency_penalty between -2.0 and 2.0
    @field_validator("temperature", mode="before")
    @classmethod
    def validate_temperature(cls, v) -> float:
        if not (0.0 <= v <= 2.0):
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

    @field_validator("top_p", mode="before")
    @classmethod
    def validate_top_p(cls, v) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("top_p must be between 0.0 and 1.0")
        return v

    @field_validator("frequency_penalty", mode="before")
    @classmethod
    def validate_frequency_penalty(cls, v) -> float:
        if not (-2.0 <= v <= 2.0):
            raise ValueError("frequency_penalty must be between -2.0 and 2.0")
        return v
    
    def is_unset(self, field_name: str) -> bool:
        return field_name not in self.model_fields_set
    
    @model_validator(mode="after")
    @classmethod
    def validate_reasoning_effort_and_model(cls, model_instance: "AOAIProfile") -> "AOAIProfile":
        model_name = model_instance.model.lower()
        reasoning_effort = model_instance.reasoning_effort

        if model_instance.is_unset("reasoning_effort"):
            return model_instance

        if model_name.startswith("gpt-5.1"):
            valid_efforts = ["minimal", "low", "medium", "high", None]
        elif model_name.startswith("gpt-5-mini") or model_name.startswith("gpt-5-nano"):
            valid_efforts = ["minimal", "low", "medium", "high"]
        elif model_name.startswith("gpt-5"):
            valid_efforts = ["low", "medium", "high"]
        else:
            valid_efforts = []
        if reasoning_effort not in valid_efforts:
            raise ValueError(f"For model {model_instance.model}, reasoning_effort must be one of {valid_efforts}")

        return model_instance
    
    @model_validator(mode="after")
    @classmethod
    def validate_temperature_and_reasoning_effort(cls, model_instance: "AOAIProfile") -> "AOAIProfile":
        model_name = model_instance.model.lower()
        reasoning_effort = model_instance.reasoning_effort
        temperature = model_instance.temperature
        
        if model_instance.is_unset("temperature"):
            return model_instance

        if model_name.startswith("gpt-5.1"):
            if (not model_instance.is_unset("reasoning_effort")) and (reasoning_effort is not None):
                if temperature != 1.0:
                    raise ValueError("When reasoning_effort is set, temperature must be 1.0")
        if model_name.startswith("gpt-5"):
            if temperature != 1.0:
                raise ValueError("For gpt-5* models, when reasoning_effort is set, temperature must be 1.0")
        
        return model_instance
    
    @model_validator(mode="after")
    @classmethod
    def validate_top_p_and_reasoning_effort(cls, model_instance: "AOAIProfile") -> "AOAIProfile":
        model_name = model_instance.model.lower()
        reasoning_effort = model_instance.reasoning_effort
        top_p = model_instance.top_p

        if model_instance.is_unset("top_p"):
            return model_instance
        
        if model_name.startswith("gpt-5.1"):
            if (not model_instance.is_unset("reasoning_effort")) and (reasoning_effort is not None):
                if top_p != 1.0:
                    raise ValueError("When reasoning_effort is set, top_p must be 1.0")
        if model_name.startswith("gpt-5"):
            if top_p != 1.0:
                raise ValueError("For gpt-5* models, when reasoning_effort is set, top_p must be 1.0")

        return model_instance


default_profile = AOAIProfile(
    name="default",
    model="gpt-4.1",
    temperature=1.0,
    top_p=1.0,
    frequency_penalty=0.0
)

reasoning_profile = AOAIProfile(
    name="reasoning",
    model="gpt-5",
    temperature=1.0,
    top_p=1.0,
    frequency_penalty=0.0,
    reasoning_effort="medium"
)
