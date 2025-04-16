from WebShop_prompt import *

class os_model():
    def __init__(self, model, device):
        if model == 'qwen2':
            # transformers>=4.40.0
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model_name = "Qwen/Qwen2-7B-Instruct"
            self.device = device # the device to load the model onto

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map=device
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        elif model == 'mistral':
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.device = device
            # pip install transformers torch torchvision accelerate sentencepiece protobuf
            # from transformers import pipeline
            # self.mistral_pipeline = pipeline("text-generation", model="./Mistral-7B-Instruct-v0.3", max_new_tokens=512, device=device)
            self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3", device_map=device)
            self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")
        else:
            print('unknown model')

    def qwen2_generator(self, text, history=[], language='en', mode='direct'):
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
        text = self.tokenizer.apply_chat_template(
            history,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        message = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        history.append({"role": "system", "content": message})
        return message, history
    
    def mistral_generator(self, text, history=[], language='en', mode='direct'):
        if history == [] and mode == 'direct':
            history=[
                {"role": "user", "content": get_base_prompt(language)},
                {"role": "assistant", "content": "OK"},
                {"role": "user", "content": text},
            ]
        elif history == [] and mode == 'translate':
            history=[
                {"role": "user", "content": get_trans_prompt(text, language)},
            ]
        elif history == [] and mode == 'translate_en':
            history=[
                {"role": "user", "content": get_trans_prompt_en(text, language)},
            ]
        elif history == [] and mode == 'clp':
            history=[
                {"role": "user", "content": get_clp_base_prompt(language)},
                {"role": "assistant", "content": "OK"},
                {"role": "user", "content": get_clp_1_prompt(text, language)},
            ]
        else:
            history.append({"role": "user", "content": text})
        model_inputs = self.tokenizer.apply_chat_template(history, return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(model_inputs, max_new_tokens=512, do_sample=True, pad_token_id=self.tokenizer.eos_token_id)
        message = self.tokenizer.batch_decode(generated_ids)[0]
        message = message.split('[/INST]')[-1].replace('</s>', '').strip()

        history.append({"role": "assistant", "content": message})
        return message, history