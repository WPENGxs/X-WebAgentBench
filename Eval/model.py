from openai import OpenAI
from WebShop_prompt import *

# gpt-3.5-turbo/gpt-4o
client_gpt = OpenAI(api_key="api key", base_url="base url")

# deepseek
client_deepseek = OpenAI(api_key="api key", base_url="https://api.deepseek.com/v1")

# deepinfra
client_deepinfra = OpenAI(api_key="api key", base_url="https://api.deepinfra.com/v1/openai")

BREAK_TIMES_LIMIT = 5

class model():

    def gpt_generator(text, history=[], language='en', mode='direct'):
        if history == [] and mode == 'direct':
            history=[
                {"role": "system", "content": get_base_prompt(language)},
                {"role": "user", "content": text},
            ]
        elif history == [] and mode == 'translate':
            history=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": get_trans_prompt(text, language)},
            ]
        elif history == [] and mode == 'translate_en':
            history=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": get_trans_prompt_en(text, language)},
            ]
        elif history == [] and mode == 'clp':
            history=[
                {"role": "system", "content": get_clp_base_prompt(language)},
                {"role": "user", "content": get_clp_1_prompt(text, language)},
            ]
        else:
            history.append({"role": "user", "content": text})
        loop_times = 0
        while True:
            if loop_times > BREAK_TIMES_LIMIT:
                message = 'BREAK_TIMES_LIMIT'
                break
            try:
                response = client_gpt.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=history,
                stream=False)
                message = response.choices[0].message.content
            except Exception:
                message = 'Error'
            if message != 'Error':
                break
            loop_times += 1
        history.append({"role": "system", "content": message})
        return message, history

    def gpt4_generator(text, history=[], language='en', mode='direct'):
        if history == [] and mode == 'direct':
            history=[
                {"role": "system", "content": get_base_prompt(language)},
                {"role": "user", "content": text},
            ]
        elif history == [] and mode == 'translate':
            history=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": get_trans_prompt(text, language)},
            ]
        elif history == [] and mode == 'translate_en':
            history=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": get_trans_prompt_en(text, language)},
            ]
        elif history == [] and mode == 'clp':
            history=[
                {"role": "system", "content": get_clp_base_prompt(language)},
                {"role": "user", "content": get_clp_1_prompt(text, language)},
            ]
        else:
            history.append({"role": "user", "content": text})
        loop_times = 0
        while True:
            if loop_times > BREAK_TIMES_LIMIT:
                message = 'BREAK_TIMES_LIMIT'
                break
            try:
                response = client_gpt.chat.completions.create(
                model="gpt-4o",
                messages=history,
                stream=False)
                message = response.choices[0].message.content
            except Exception:
                message = 'Error'
            if message != 'Error':
                break
            loop_times += 1
        history.append({"role": "system", "content": message})
        return message, history


    def deepseekreasoner_generator(text, history=[], language='en', mode='direct'):
        if history == [] and mode == 'direct':
            history=[
                {"role": "system", "content": get_base_prompt(language)},
                {"role": "user", "content": text},
            ]
        elif history == [] and mode == 'translate':
            history=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": get_trans_prompt(text, language)},
            ]
        elif history == [] and mode == 'translate_en':
            history=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": get_trans_prompt_en(text, language)},
            ]
        elif history == [] and mode == 'clp':
            history=[
                {"role": "system", "content": get_clp_base_prompt(language)},
                {"role": "user", "content": get_clp_1_prompt(text, language)},
            ]
        else:
            history.append({"role": "user", "content": text})
        loop_times = 0
        while True:
            if loop_times > BREAK_TIMES_LIMIT:
                message = 'BREAK_TIMES_LIMIT'
                break
            try:
                response = client_deepseek.chat.completions.create(
                model="deepseek-reasoner",
                messages=history,
                stream=False)
                message = response.choices[0].message.content
            except Exception:
                message = 'Error'
            if message != 'Error':
                break
            loop_times += 1
        history.append({"role": "assistant", "content": message})
        return message, history

    def qwq_generator(text, history=[], language='en', mode='direct'):
        if history == [] and mode == 'direct':
            history=[
                {"role": "system", "content": get_base_prompt(language)},
                {"role": "user", "content": text},
            ]
        elif history == [] and mode == 'translate':
            history=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": get_trans_prompt(text, language)},
            ]
        elif history == [] and mode == 'translate_en':
            history=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": get_trans_prompt_en(text, language)},
            ]
        elif history == [] and mode == 'clp':
            history=[
                {"role": "system", "content": get_clp_base_prompt(language)},
                {"role": "user", "content": get_clp_1_prompt(text, language)},
            ]
        else:
            history.append({"role": "user", "content": text})
        loop_times = 0
        while True:
            if loop_times > BREAK_TIMES_LIMIT:
                message = 'BREAK_TIMES_LIMIT'
                break
            try:
                response = client_deepinfra.chat.completions.create(
                model="Qwen/QwQ-32B-Preview",
                messages=history,
                stream=False)
                message = response.choices[0].message.content
            except Exception:
                message = 'Error'
            if message != 'Error':
                break
            loop_times += 1
        history.append({"role": "system", "content": message})
        return message, history
