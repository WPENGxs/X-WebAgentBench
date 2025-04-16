from WebShop_test import WebShop_test
from model import model
import argparse
import os
from os_model import os_model

parser = argparse.ArgumentParser()

# model = ['gpt-3.5-turbo', 'gpt-4o', 'qwen2', 'mistral', 'llama3']
# method = ['direct', 'translate_en', 'self-translate_en', 'clp_en']
# language = ['zh', 'fr', 'es', 'de', 'el', 'bg', 'ru', 'tr', 'ar', 'vi', 'th', 'hi', 'sw', 'ur']
parser.add_argument('--model', type=str, default='gpt-3.5-turbo')
parser.add_argument('--method', type=str, default='direct')
parser.add_argument('--language', type=str, default='zh')
parser.add_argument('--root_log_path', type=str, default='./saved_log')
parser.add_argument('--test_n', type=int, default=200)
parser.add_argument('--device', type=str, default='cuda:0')

def check_dir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            print(f"An error occurred while creating path '{path}': {e.strerror}")

def main():
    args = parser.parse_args()
    saved_log_dir = f'{args.root_log_path}/{args.model}/{args.method}'
    check_dir(saved_log_dir)
    saved_log_path = f'{args.root_log_path}/{args.model}/{args.method}/{args.method}'

    print(f'start test, now test {args.language}')

    if args.model == 'gpt-3.5-turbo':
        test_model = WebShop_test(model.gpt_generator, saved_log_path)
    elif args.model == 'gpt-4o':
        test_model = WebShop_test(model.gpt4_generator, saved_log_path)
    elif args.model == 'deepseek_v2':
        test_model = WebShop_test(model.deepseek_v2_generator, saved_log_path)
    elif args.model == 'qwen2':
        os_model_ = os_model(args.model, args.device)
        test_model = WebShop_test(os_model_.qwen2_generator, saved_log_path)
    elif args.model == 'mistral':
        os_model_ = os_model(args.model, args.device)
        test_model = WebShop_test(os_model_.mistral_generator, saved_log_path)
    elif args.model == 'deepseek-reasoner':
        test_model = WebShop_test(model.deepseekreasoner_generator, saved_log_path)
    elif args.model == 'qwq':
        test_model = WebShop_test(model.qwq_generator, saved_log_path)
    elif args.model == 'llama3':
        print('Please follow the official tutorial and modify our code in os_model.py, or you can use API to call the llama series model (we use deepinfra).')
    else:
        print('error model name.')

    if args.method == 'direct':
        total_score = test_model.test_direct(args.language, n=args.test_n)
    elif args.method == 'translate_en':
        total_score = test_model.test_translate_en(args.language, n=args.test_n)
    elif args.method == 'self-translate_en':
        total_score = test_model.test_self_translate_en(args.language, n=args.test_n)
    elif args.method == 'clp_en':
        total_score = test_model.test_clp_en(args.language, n=args.test_n)
    else:
        print('error method name.')

    print('#'*40)
    print(f'model: {args.model}\nmethod: {args.method}\nlanguage: {args.language}\ntotal_score: {total_score*100}')
    print('#'*40)

if __name__ == '__main__':
    main()