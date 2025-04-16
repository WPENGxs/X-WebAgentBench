from multilingual_text import *

item = {
    'en': 'earphone',
    'zh': '耳机',
    'fr': 'écouteur',
    'es': 'auricular', 
    'de': 'Kopfhörer', 
    'el': 'ακουστικό', 
    'bg': 'слушалка', 
    'ru': 'наушник', 
    'tr': 'kulaklık', 
    'ar': 'سماعة الأذن', 
    'vi': 'tai nghe', 
    'th': 'หูฟัง', 
    'hi': 'ईरफ़ोन', 
    'sw': 'earphone', 
    'ur': 'ائرفون'
}
attr = {
    'en': 'black',
    'zh': '黑色',
    'fr': 'noir', 
    'es': 'negro', 
    'de': 'Schwarz', 
    'el': 'μαύρος', 
    'bg': 'черен', 
    'ru': 'черный', 
    'tr': 'siyah', 
    'ar': 'أسود', 
    'vi': 'đen', 
    'th': 'สีดำ', 
    'hi': 'काला', 
    'sw': 'nyeusi', 
    'ur': 'سیاہ'
}
trans_lan = {
    'en': 'English',
    'zh': 'Chinese',
    'fr': 'French',
    'es': 'Spanish', 
    'de': 'German', 
    'el': 'Greek', 
    'bg': 'Bulgarian', 
    'ru': 'Russian', 
    'tr': 'Turkish', 
    'ar': 'Arabic', 
    'vi': 'Vietnamese', 
    'th': 'Thai', 
    'hi': 'Hindi', 
    'sw': 'Swahili', 
    'ur': 'Urdu'
}

base_prompt = {
    'en': f'''You are an interactive assistant on a shopping website. Given a shopping instruction, you need to follow the instruction requirements and accurately determine the products you need to buy at the moment. And extract the search keywords, search and filter the products on the shopping website, find the products you need and buy them.
    Below are some instructions and their corresponding functions:
    {env_search['en']}[<keyword>]: Search keywords on the search page. If you are not on the search page, please return to the search page. Such as"{env_search['en']}[earphone]".
    {env_click['en']}[{webshop_prev['en']}]/{env_click['en']}[{webshop_next['en']}]: Jump to the previous/next page. Such as "{env_click['en']}[{webshop_prev['en']}]".
    {env_click['en']}[{webshop_back_btu['en']}]: Back to search page. Such as "{env_click['en']}[{webshop_back_btu['en']}]".
    {env_click['en']}[<item id>]: Click on a item to go to its details page. Such as "{env_click['en']}[ABCDE12345]".
    {env_click['en']}[<attribute>]: Select item attribute on the details page. Such as "{env_click['en']}[black]".
    {env_click['en']}[{webshop_buy['en']}]: Buy this item. Such as "{env_click['en']}[{webshop_buy['en']}]".
    Note: Please only reply with the listed instructions. The instructions must be complete in the format of "{env_search['en']}/{env_click['en']}[<filler word>]". No missing or additional symbols are allowed!
    ''',

    'zh': f'''你是一名购物网站互动助理。给定购物的一条指令，你需要遵循指令要求，准确判断当前需要购买的商品。并提取出搜索关键词，通过搜索和筛选购物网站上的商品，找到你所需要的商品并购买。
    下面是一些指令和其对应的作用：
    {env_search['zh']}[<关键词>]：在搜索页面搜索关键词，不在搜索页面时，请返回搜索页面。例如"{env_search['zh']}[耳机]"。
    {env_click['zh']}[{webshop_prev['zh']}]/{env_click['zh']}[{webshop_next['zh']}]：跳转到到上一页/下一页。例如"{env_click['zh']}[{webshop_prev['zh']}]"。
    {env_click['zh']}[{webshop_back_btu['zh']}]：返回搜索页面。例如"{env_click['zh']}[{webshop_back_btu['zh']}]"。
    {env_click['zh']}[<商品id>]：点击商品并进入详情页面。例如"{env_click['zh']}[ABCDE12345]"。
    {env_click['zh']}[<商品属性>]：在商品详情页面选择商品属性。例如"{env_click['zh']}[黑色]"。
    {env_click['zh']}[{webshop_buy['zh']}]：购买商品。例如"{env_click['zh']}[{webshop_buy['zh']}]"。
    注意：请只回复列出的指令，指令必须完整的为"{env_search['zh']}/{env_click['zh']}[<填充词>]"格式，不能缺少或者添加额外符号！
    '''
}

# agentbench: https://arxiv.org/pdf/2308.03688
def get_base_prompt(language):
    prompt = f'''You are web shopping. I will give you instructions about what to do.
    You have to follow the instructions.
    Every round I will give you an observation and a list of available actions, you have to respond an action based on the state and instruction. You can use search action if search is available.
    You can click one of the buttons in clickables. An action should be of the following structure:
    {env_search[language]}[<keyword>]: Search keywords on the search page. If you are not on the search page, please return to the search page. Such as"{env_search[language]}[{item[language]}]".
    {env_click[language]}[{webshop_prev[language]}]/{env_click[language]}[{webshop_next[language]}]: Jump to the previous/next page. Such as "{env_click[language]}[{webshop_prev[language]}]".
    {env_click[language]}[{webshop_back_btu[language]}]: Back to search page. Such as "{env_click[language]}[{webshop_back_btu[language]}]".
    {env_click[language]}[<item id>]: Click on a item to go to its details page. Such as "{env_click[language]}[ABCDE12345]".
    {env_click[language]}[<attribute>]: Select item attribute on the details page. Such as "{env_click[language]}[{attr[language]}]".
    {env_click[language]}[{webshop_buy[language]}]: Buy this item. Such as "{env_click[language]}[{webshop_buy[language]}]".
    If the action is not valid, perform nothing. 
    Keywords in search are up to you, but the value in click must be a value in the list of available actions. 
    Remember that your keywords in search should be carefully designed. 
    Your response should use the following format:
    Thought: I think ...
    Action: {env_click[language]}[<something>]
    '''
    return prompt

def get_trans_prompt_en(text, language):
    prompt = f'''You are an expert translator with fluency in English and {trans_lan[language]} languages. Translate the given text from {trans_lan[language]} to English. 
    Text: {text}
    '''
    return prompt

def get_trans_prompt(text, language):
    prompt = f'''You are an expert translator with fluency in {trans_lan[language]} and English languages. Translate the given text from English to {trans_lan[language]}. 
    Text: {text}
    '''
    return prompt

def get_clp_base_prompt(language):
    prompt = f'''You are an expert in multi-lingual understanding. Please fully understand given observation and give the correct Action. 
    You should help users buy what they need and help them perform the corresponding actions.
    '''
    return prompt

def get_clp_1_prompt(observation, language):
    prompt = f'''Please act as an expert in multi-lingual understanding in {trans_lan[language]}.
    You need fully understand every words, and explain its effection.
    Don't response the Action, it is next step task.
    Let's understand the observation in English step-by-step!
    {observation}
    '''
    return prompt

def get_clp_2_prompt(prev_action, language):
    prompt = f'''After understanding, you should act as an expert in reasoning in English. In the end, you should response Action in {trans_lan[language]} according previously understood observation.
    Previous Action: {prev_action}
    {get_base_prompt(language)}
    '''
    return prompt