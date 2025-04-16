
import json
import argparse
import os

parser = argparse.ArgumentParser()

parser.add_argument('--model', type=str, default='gpt-3.5-turbo')
parser.add_argument('--method', type=str, default='direct')
parser.add_argument('--language', type=str, default='all')
parser.add_argument('--root_log_path', type=str, default='./saved_log')

def re_eval(model, method, language, root_log_path):
    if language != 'all':
        total_score = 0
        log_path = f'{root_log_path}/{model}/{method}/{method}_{language}.json'
        with open(log_path, 'r') as json_file:
            logs = json.load(json_file)
        for i in range(len(logs)):
            total_score += logs[f'{i}']['reward']
        total_score = total_score / len(logs)
        return total_score
    else:
        total_score = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        language = ['zh', 'fr', 'es', 'de', 'el', 'bg', 'ru', 'tr', 'ar', 'vi', 'th', 'hi', 'sw', 'ur']
        for i in range(len(language)):
            log_path = f'{root_log_path}/{model}/{method}/{method}_{language[i]}.json'
            if os.path.isfile(log_path):
                with open(log_path, 'r') as json_file:
                    logs = json.load(json_file)
                for j in range(len(logs)):
                    total_score[i] += logs[f'{j}']['reward']
                total_score[i] = total_score[i] / len(logs)
            else:
                total_score[i] = -1
        return total_score

if __name__ == '__main__':
    language = ['zh', 'fr', 'es', 'de', 'el', 'bg', 'ru', 'tr', 'ar', 'vi', 'th', 'hi', 'sw', 'ur']
    args = parser.parse_args()
    total_score = re_eval(args.model, args.method, args.language, args.root_log_path)
    if isinstance(total_score, list):
        for i in range(len(language)):
            print('#'*40)
            print(f'model: {args.model}\nmethod: {args.method}\nlanguage: {language[i]}\ntotal_score: {total_score[i]}')
            print('#'*40)
    else:
        print('#'*40)
        print(f'model: {args.model}\nmethod: {args.method}\nlanguage: {args.language}\ntotal_score: {total_score}')
        print('#'*40)