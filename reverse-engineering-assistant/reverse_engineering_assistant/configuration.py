#!/usr/bin/env python3
from __future__ import annotations

import yaml
from typing import Literal, TypedDict, Optional, NotRequired

from .model import ModelType

from pathlib import Path

from enum import Enum

configuration_directory = Path.home() / ".config" / "reverse-engineering-assistant"
if not configuration_directory.exists():
    configuration_directory.mkdir(exist_ok=True, parents=True)
configuration_file = configuration_directory / "config.yaml"

llama_2_prompt = """<<SYS>>
You are to help with reverse engineering related tasks.
<</SYS>>
[INST] We have provided context information below.
---------------------
{context_str}
---------------------
Given this information, perform the following instructions.
{query_str}
[/INST]"""

codellama_2_prompt = """<<SYS>>
You are a helpful coding AI assistant, specialising in reverse engineering tasks.
We have provided context information below.
---------------------
{context_str}
---------------------
Given this information, perform the following instructions.
<</SYS>>
[INST] {query_str}
[/INST]"""


step_decompose_query_prompt = """The original question is as follows: {query_str}
   We have an opportunity to answer some, or all of the question from a 
   knowledge source. 

   We are analysing a program, and we have the following information:
   {program_context}

   Context information for the knowledge source is provided below.
   Given the context, return a new question that can be answered from 
   the context. The question can be the same as the original question, 
   or a new question that represents a subcomponent of the overall question.
   As an example: 

   Question: How many Grand Slam titles does the winner of the 2020 Australian 
   Open have?
   Knowledge source context: Provides information about the winners of the 2020 
   Australian Open
   New question: Who was the winner of the 2020 Australian Open? 

   Question: What is the current population of the city in which Paul Graham found 
   his first company, Viaweb?
   Knowledge source context: Provides information about Paul Graham's 
   professional career, including the startups he's founded. 
   New question: In which city did Paul Graham found his first company, Viaweb? 


   Question: {query_str}
   Knowledge source context: {context_str}
   New question: 
"""

class QueryEngineType(Enum):
    simple_query_engine = "simple_query_engine"
    multi_step_query_engine = "multi_step_query_engine"

class LlamaCPPConfiguration(TypedDict):
    # URL to download the model from.
    # Not required if the path is set
    model_url: Optional[str]
    # Path to the model file.
    # Not required if the URL is set
    model_path: Optional[str]
    # Number of layers to offload to the GPU
    # during inference
    number_gpu_layers: Optional[int]
    model_type: Optional[Literal["llama", "codellama"]]

class TextGenWebUIConfiguration(TypedDict):
    # Base URL of your text_gen_web_ui instance
    # e.g. http://localhost:5000
    text_gen_web_ui_url: str

class OpenAIConfiguration(TypedDict):
    # If None, we'll pull from the environment
    # variable OPENAI_API_TOKEN
    openai_api_token: Optional[str]

class AssistantConfiguration(TypedDict):
    type: ModelType
    openai: Optional[OpenAIConfiguration]
    local_llama_cpp: Optional[LlamaCPPConfiguration]
    text_gen_web_ui: Optional[TextGenWebUIConfiguration]
    prompt: Optional[str]
    step_decompose_query_prompt: Optional[str]
    query_engine: Optional[QueryEngineType]

def save_configuration(configuration: AssistantConfiguration):
    with open(configuration_file, "w") as f:
        config = configuration.copy()
        config["type"] = config["type"].value
        config["query_engine"] = config["query_engine"].value
        yaml.safe_dump(config, f)

def load_configuration() -> AssistantConfiguration:
    if not configuration_file.exists():
        create_default_configuration()
    with open(configuration_file, "r") as f:
        config = yaml.safe_load(f)
        config["type"] = ModelType(config["type"])
        config["query_engine"] = QueryEngineType(config.get("query_engine", "multi_step_query_engine"))
        return config

def create_default_configuration():
    assistant_config: AssistantConfiguration = {
            "type": ModelType.OpenAI,
            "openai": {
                "openai_api_token": None,
            },
            "local_llama_cpp": {
                #"model_url": "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGML/resolve/main/llama-2-13b-chat.ggmlv3.q6_K.bin",
                "model_url": "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q6_K.gguf.bin",
                "model_path": None,
                "number_gpu_layers": 1,
                "model_type": "codellama",
            },
            "text_gen_web_ui": {
                "text_gen_web_ui_url": "http://localhost:5000",
            },
            "prompt": codellama_2_prompt,
            "step_decompose_query_prompt": step_decompose_query_prompt,
            "query_engine": QueryEngineType.multi_step_query_engine,
    }
    save_configuration(assistant_config)