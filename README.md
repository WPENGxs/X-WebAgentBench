<h2 align="center">X-WebAgentBench: A Multilingual Interactive Web Benchmark for Evaluating Global Agentic System</h2>

<p align="center">
  <b>
  [<a href="paper_url">Arxiv</a>]
  </b>
  <br/>
</p>

### Table of Contents
- [X-WebAgentBench](#x-webagentbench)
  - [Data Prepare](#data-prepare)
  - [Setup](#setup)
  - [Usage](#usage)
- [Evaluation](#evaluation)
  - [Setup](#setup-1)
  - [Final Result](#final-result)
- [Reference](#reference)
- [Contact](#contact)

## X-WebAgentBench

### Data Prepare
1. Download product data and instruction data, which is about 5G after unzip. Download link: [Google Drive](https://drive.google.com/file/d/1BwUHkTFuQVmhy7-HLbK4JjqJbups7OgP/view?usp=drive_link).

2. Unzip the files to `X-WebAgentBench/data/`.
### Setup
1. Create conda environment:
```
conda create -n xwebagentbench python=3.8.13
conda activate xwebagentbench
```
2. Install environment and jdk:
```
conda install -c pytorch faiss-cpu
conda install -c conda-forge openjdk=11
pip install -r requirements.txt
```
**Note:** If you get the output `error: command 'g++' failed: No such file or directory`, please install g++ by `sudo apt-get install g++` to solve it.

3. Download `en_core_web_lg` model:
```
python -m spacy download en_core_web_lg
```
4. Create index files (including 15 languages, about 30G). It takes about 30 minutes on our device:
```
(xwebagentbench) root@server:~/X-WebAgentBench$ ./reset_index.sh
```
5. Set host in `web_agent_site/app_multi.py` (default port is 3000):
```
--> app.run(host='your ip address', port=3000)
```

6. Launch X-WebAgentBench (need 16G RAM):
```
(xwebagentbench) root@server:~/X-WebAgentBench$ python -m web_agent_site.app_multi --log
```
**Note:** We recommend that the server needs at least 16G memory, or using higher memory.

<!-- The server configuration we use is as follows:
```
CPU: 8*Intel(R) Xeon(R) CPU E5-2680 v4 @ 2.40GHz
RAM: 16G
ROM: 120G
System: Ubuntu Server 20.04
``` -->
**Start in Specific Languages:** If you want start X-WebAgentBench in specific languages, please modify `X-WebAgentBench/web_agent_site/app_multi.py`:
```
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebShop flask app backend configuration")
    parser.add_argument("--log", action='store_true', help="Log actions on WebShop in trajectory file")
    parser.add_argument("--attrs", action='store_true', help="Show attributes tab in item page")

--> languages = ['en', 'zh', 'fr', 'es', 'de', 'el', 'bg', 'ru', 'tr', 'ar', 'vi', 'th', 'hi', 'sw', 'ur']
```
Adjust the `languages` list to the languages you want to start. And `'en'` MUST in list.

### Usage
**Webpage:** You can use a browser to access X-WebAgentBench directly by below url:
```
http://webshop_url:<port>/<language>/fixed_<num>

<port> is the port that was set when the X-WebAgentBench was launched, and it defaults to 3000.
<language> is an abbreviation for each language.
<num> is human_ins number id, between 0 and 199, inclusive.
```

**Text:** Also, you can parse html to text using the code `Eval/WebShopEnv.py`, you can use code to interact with the X-WebAgentBench and fetch text content:
```
from WebShopEnv import webshopEnv
env = webshopEnv()
res = env.step(f'{<language>}/fixed_{<num_id>}', <action>, <action_attr>)
observation = res[0]

<action>: Action input
<action_attr>: ['reset', 'think', 'search', 'click']
```
* observation example print (init page):
```
WebShop 
Instruction:  
im looking for a earbud headphones for stereo sound quality of style je-04b which will be more comfortable for me to use without disturbing others , and price lower than 60.00 dollars 
[Search]
```

* observation example print (search page):
```
Instruction: 
im looking for a earbud headphones for stereo sound quality of style je-04b which will be more comfortable for me to use without disturbing others , and price lower than 60.00 dollars 
[Back to Search] 
Page 1 (Total results: 50) 
[Next >] 
[B09743DFJC] 
Jinpei Cute Panda Wireless Earphones, Waterproof, Noise Cancelling in-Ear erbuds, TWS Stereo Headphones, Built in mic Headset Premium Sound with deep Bass 
$39.9 
[B097445J5R] 
Jinpei Cute Pink cat Wireless Earphones, Waterproof, Noise Cancelling in-Ear erbuds, TWS Stereo Headphones, Built in mic Headset Premium Sound with deep bass 
$39.9 
[B084TSH1YW] 
TWS Headphones Wireless Earbuds Earphones for Moto Z4, True Wireless Stereo Headset Hands-Free Mic Charging Case Compatible with Motorola Moto Z4 
$59.99 
[B09QVFV6GG] 
TWS Headphones Wireless Earbuds Earphones for Galaxy A03s - True Wireless Stereo Headset Hands-Free Mic Charging Case Compatible with Samsung Galaxy A03s 
$54.99 
[B084Z3GPP7] 
TWS Headphones Wireless Earbuds Earphones for Moto G Stylus, True Wireless Stereo Headset Hands-Free Mic Charging Case Compatible with Motorola Moto G Stylus 
$59.99
```

* observation example print (item page):
```
Instruction: 
im looking for a earbud headphones for stereo sound quality of style je-04b which will be more comfortable for me to use without disturbing others , and price lower than 60.00 dollars 
[Back to Search] 
[< Prev] 
style [je-01b][je-02b][je-03b][je-04b][je-05b]
Jinpei Cute Panda Wireless Earphones, Waterproof, Noise Cancelling in-Ear erbuds, TWS Stereo Headphones, Built in mic Headset Premium Sound with deep Bass 
Price: $39.9 
Rating: N.A. 
[Description] 
[Features] 
[Reviews] 
[Buy Now]
```

* observation example print (buy page):
```
Your score (min 0.0, max 1.0): 0.6666666666666666
```

## Evaluation

### Setup
1. Create conda environment:
```
conda create -n eval python=3.10.0
conda activate eval
```
2. Install base environment:
```
pip install tqdm requests bs4 deep_translator
```
3. (Optional) If you want to run GPT-3.5-turbo/GPT-4o, please install `openai` and set openai API key in `X-WebAgentBench/Eval/model.py`:
```
--> client_gpt = OpenAI(api_key="api key", base_url="base url")
```
4. (Optional) For `Llama`, we use the API to call the llama series model (Llama3-8B/70B, Llama3.1-8B/70B/405B). If you want to run it locally, please follow the [official tutorial](https://github.com/meta-llama/llama3) and modify our code. You can follow our step to install open-source LLM dependencies for `Qwen2` and `Mistral`:
```
Qwen2: transformers>=4.40.0
Mistral: pip install transformers torch torchvision accelerate sentencepiece protobuf
```
5. Fill in the url in `X-WebAgentBench/Eval/WebShopEnv.py` (like `http://webshop_url:<port>`):
```
--> WEBSHOP_URL = "webshop_url"
```
6. Run our code:
```
(eval) root@server:~/X-WebAgentBench/Eval$ python main.py --model MODEL --method METHOD --language LANGUAGE [--test_n NUM --device DEVICE]

MODEL = ['gpt-3.5-turbo', 'gpt-4o', 'qwen2', 'mistral', 'llama3']
METHOD = ['direct', 'translate_en', 'self-translate_en', 'clp_en']
LANGUAGE = ['zh', 'fr', 'es', 'de', 'el', 'bg', 'ru', 'tr', 'ar', 'vi', 'th', 'hi', 'sw', 'ur']
NUM = 200 (default)
DEVICE = 'cuda:0' (default)
```

### Final Result
After the evaluation code is run, the final result (Task Score=100*avg.reward) will be output:
```
########################################
model: MODEL
method: METHOD
language: LANGUAGE
total_score: SCORE
########################################
```

In addition, you can get output log in `X-WebAgentBench/Eval/saved_log/MODEL/METHOD/METHOD_LANGUAGE.json`.

## Reference
If you find this project useful for your research, please consider citing the following paper:
```
@article
```

## Contact
If you have any questions or suggestions, please create Github issues here or email [Peng Wang](mailto:wpengxss@gmail.com), [Ruihan Tao](mailto:aarontao757@gmail.com), and [Libo Qin](mailto:lbqin@csu.edu.cn).