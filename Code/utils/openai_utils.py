import sys
sys.path.append("./utils")

from openai import OpenAI
import json
import base64
import requests
import tiktoken

def login_openai():
    key = json.load(open(sys.path[0] + "/data/openai_api_key.json"))

    organization = key["organization"]
    api_key = key["api_key"]
    client = OpenAI(api_key=api_key, organization=organization)
    return client

def generate_completion_multiple(prompts, client, model='gpt-4o', temp=0.75, n=1, max_tokens=15500, logprobs=True, top_logprobs=5, return_obj=True):
    messages = []
    for prompt in prompts:
        messages.append({"role": prompt[0], "content": prompt[1]})
    if logprobs:
        chat_completion = client.chat.completions.create(
              model=model,
              messages=messages,
              temperature=temp,
              n=n,
              logprobs=logprobs,
              top_logprobs=top_logprobs
        )
    else:
        chat_completion = client.chat.completions.create(
              model=model,
              messages=messages,
              temperature=temp,
              n=n,
        )
    return chat_completion if return_obj else [choice.message.content for choice in chat_completion.choices]

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def respond_to_image_multiple(prompts_and_images, api_key, model="gpt-4o", temp=0.75, n=1, max_tokens=4096, return_obj=True, timeout=300):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    messages = []
    for role, prompt, image in prompts_and_images:
        if image is not None:
            message = {"role": role, "content":
                [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}",
                        },
                    }
                ]
                       }
        else:
            message = {"role": role, "content":
                [{"type": "text", "text": prompt}]
                       }
        messages.append(message)
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temp,
        "n": n,
        "max_tokens": max_tokens
    }
    chat_completion = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=timeout).json()

    return chat_completion

def estimate_cost(prompts, model="gpt-4o"):
    tokens = 0
    for role, prompt, image in prompts:
        enc = tiktoken.encoding_for_model(model)
        tokens += len(enc.encode(prompt))
        if image is not None:
            tokens += 425
    input_cost_ratio = 5/1000000
    input_cost = tokens*input_cost_ratio

    max_output_cost = 4096*(15/1000000)

    max_cost = input_cost + max_output_cost

    return {"input_tokens": tokens, "input_cost": input_cost, "max_output_cost": max_output_cost, "max_cost": max_cost}