import sys
import json
from tqdm import tqdm
import argparse
sys.path.insert(0, '../')

from web_agent_site.utils import DEFAULT_FILE_PATH
from web_agent_site.engine.engine import load_products

parser = argparse.ArgumentParser()
parser.add_argument('--language', type=str, default='en')

args = parser.parse_args()
language = args.language
print(f'python convert_product_file_format.py language: {language}')

shuffle_file_path = DEFAULT_FILE_PATH + f'items_shuffle_40k_{language}.json'
attr_path = f'items_ins_v2_40k_{language}.json'
huamn_path = f'items_human_ins_{language}.json'
all_products, *_ = load_products(filepath=shuffle_file_path, attr_path=attr_path, human_attr_path=huamn_path)

docs = []
for p in tqdm(all_products, total=len(all_products)):
    option_texts = []
    options = p.get('options', {})
    for option_name, option_contents in options.items():
        option_contents_text = ', '.join(option_contents)
        option_texts.append(f'{option_name}: {option_contents_text}')
    option_text = ', and '.join(option_texts)

    doc = dict()
    doc['id'] = p['asin']
    doc['contents'] = ' '.join([
        p['Title'],
        p['Description'],
        p['BulletPoints'][0] if p['BulletPoints'][0]!=None else "",
        option_text,
    ]).lower()
    doc['product'] = p
    docs.append(doc)


with open(f'./{language}/resources_100/documents.jsonl', 'w+') as f:
    for doc in docs[:100]:
        f.write(json.dumps(doc) + '\n')

with open(f'./{language}/resources/documents.jsonl', 'w+') as f:
    for doc in docs:
        f.write(json.dumps(doc) + '\n')

with open(f'./{language}/resources_1k/documents.jsonl', 'w+') as f:
    for doc in docs[:1000]:
        f.write(json.dumps(doc) + '\n')

with open(f'./{language}/resources_100k/documents.jsonl', 'w+') as f:
    for doc in docs[:100000]:
        f.write(json.dumps(doc) + '\n')
