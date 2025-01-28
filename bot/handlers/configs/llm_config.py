from services.llm.deepseek_llm import DeepseekLlm
from services.llm.llm_model import LlmModel
from services.llm.openai_llm import OpenAiLlm, OpenAiO1Llm
from services.llm.anthropic_llm import AnthropicLlm

default_model_mapping: dict[str, LlmModel] = {}

# openai
default_model_mapping["gpt"] = OpenAiLlm(model_name="gpt-4o-mini") 
default_model_mapping["гпт"] = OpenAiLlm(model_name="gpt-4o-mini") 
default_model_mapping["gpt4"] = OpenAiLlm(model_name="gpt-4o") 
default_model_mapping["гпт4"] = OpenAiLlm(model_name="gpt-4o") 
default_model_mapping["o1"] = OpenAiO1Llm(model_name="o1-mini") 
default_model_mapping["o1p"] = OpenAiO1Llm(model_name="o1-preview")

# anthropic
default_model_mapping["anth"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["claude"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["haiku"] = AnthropicLlm(model_name="claude-3-5-haiku-latest") 
default_model_mapping["sonnet"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["opus"] = AnthropicLlm(model_name="claude-3-opus-latest", is_vision_model=False)

# deepseek
default_model_mapping["ds"] = DeepseekLlm(model_name="deepseek-chat", is_vision_model=False) 
default_model_mapping["dsr"] = DeepseekLlm(model_name="deepseek-reasoner", is_vision_model=False) 
default_model_mapping["deepseek"] = DeepseekLlm(model_name="deepseek-reasoner", is_vision_model=False)