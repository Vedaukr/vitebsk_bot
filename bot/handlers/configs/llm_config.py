from services.llm.deepseek_llm import DeepseekLlm
from services.llm.llm_model import LlmModel
from services.llm.openai_llm import GrokLlm, OpenAiLlm, OpenAiOSeriesLlm
from services.llm.anthropic_llm import AnthropicLlm, AnthropicThinkingLlm
from settings import settings

default_model_mapping: dict[str, LlmModel] = {}

# openai
default_model_mapping["gpt4m"] = OpenAiLlm(model_name="gpt-4o-mini")
default_model_mapping["gpt"] = OpenAiLlm(model_name="gpt-4o") 
default_model_mapping["гпт"] = OpenAiLlm(model_name="gpt-4o") 
default_model_mapping["gpt4"] = OpenAiLlm(model_name="gpt-4o") 
default_model_mapping["гпт4"] = OpenAiLlm(model_name="gpt-4o") 

# Cyrillic dups for o
default_model_mapping["o1"] = OpenAiOSeriesLlm(model_name="o1-mini") 
default_model_mapping["о1"] = OpenAiOSeriesLlm(model_name="o1-mini") 
default_model_mapping["o1p"] = OpenAiOSeriesLlm(model_name="o1-preview")
default_model_mapping["о1п"] = OpenAiOSeriesLlm(model_name="o1-preview")
default_model_mapping["o3"] = OpenAiOSeriesLlm(model_name="o3-mini", reasoning_effort="high")
default_model_mapping["о3"] = OpenAiOSeriesLlm(model_name="o3-mini", reasoning_effort="high")

# anthropic
default_model_mapping["anth"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["claude"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["haiku"] = AnthropicLlm(model_name="claude-3-5-haiku-latest") 
default_model_mapping["sonnet"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["opus"] = AnthropicLlm(model_name="claude-3-opus-latest", is_vision_model=False)

default_model_mapping["anth37"] = AnthropicThinkingLlm(model_name="claude-3-7-sonnet-latest", thinking_budget=3000) 
default_model_mapping["claude37"] = AnthropicThinkingLlm(model_name="claude-3-7-sonnet-latest", thinking_budget=3000) 
default_model_mapping["sonnet37"] = AnthropicThinkingLlm(model_name="claude-3-7-sonnet-latest", thinking_budget=3000) 

# deepseek
default_model_mapping["ds"] = DeepseekLlm(model_name="deepseek-chat", is_vision_model=False) 
default_model_mapping["dsr"] = DeepseekLlm(model_name="deepseek-reasoner", is_vision_model=False) 
default_model_mapping["deepseek"] = DeepseekLlm(model_name="deepseek-reasoner", is_vision_model=False)

# grok
default_model_mapping["grok"] = GrokLlm(model_name="grok-3-mini", is_vision_model=False, api_key=settings['GROK_API_KEY'], organization=None, base_url="https://api.x.ai/v1") 
default_model_mapping["grok3"] = GrokLlm(model_name="grok-3", is_vision_model=False, api_key=settings['GROK_API_KEY'], organization=None, base_url="https://api.x.ai/v1")