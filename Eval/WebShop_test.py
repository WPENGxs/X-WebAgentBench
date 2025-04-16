from WebShopEnv import webshopEnv
from WebShop_prompt import *
from multilingual_text import *
import json
import re
from tqdm import tqdm
from deep_translator import GoogleTranslator
import time
from split_paragraph import split_paragraph

class WebShop_test():

    def __init__(self, model, saved_log_path):
        self.env = webshopEnv()
        self.model = model
        self.saved_log_path = f'{saved_log_path}'

    def trans_api(self, translator, text):
        if text != '':
            try:
                trans_text = translator.translate(text)
                time.sleep(0.5)
            except Exception as e:
                ##### text too long #####
                error = str(e)
                if 'Text length need to be between 0 and 5000 characters' in error:
                    parts = split_paragraph(text, max_length=3000)
                    trans_parts = []
                    for part in parts:
                        trans_part = translator.translate(part)
                        time.sleep(0.5)
                        trans_parts.append(trans_part)
                    af_text = ''
                    for trans_part in trans_parts:
                        af_text += trans_part
                    return af_text
                else:
                    trans_text = ''
                
                time.sleep(0.5)
            return trans_text
        else:
            return ''

    def get_clickable_actions(self, observation, language):
        available_actions = {}
        pattern = r'\[(.*?)\]'
        match = re.findall(pattern, observation)
        if webshop_search[language] in match:
            available_actions["has_search_bar"] = True
        else:
            available_actions["has_search_bar"] = False

        available_actions["clickables"] = str(match)
        output = f'Observation:\n{observation}\n\nAvailable Actions:\n' + str(available_actions)
        return output

    def get_clickable_actions_list(self, observation):
        pattern = r'\[(.*?)\]'
        match = re.findall(pattern, observation)
        return match

    def get_action(self, action):
        try:
            if '<think>' in action:
                action = action.split('</think>')[-1]
            action = action.split('Action: ')[1]
        except:
            action = 'Not find \"Action: \", can\'t split.'
        return action

    def search_find_buy_item(self, i, observation, history=[], language='en', need_re_search=False, loop=False, re_search_times=0, limit_re_search_times=3):
        if need_re_search:
            if re_search_times > limit_re_search_times:
                history.append({"role": "user", "content": f'limit re search times'})
                reward = 0
                return reward, history
            try:
                re_search_times += 1
                ########## re search: prompt -> llm ##########
                search_action, history = self.model(observation, history=history, language=language)
                search_action = self.get_action(search_action)
                if search_action == 'Not find \"Action: \", can\'t split.':
                    raise Exception
                ########## re search -> webshop ##########
                res = self.env.step(f'{language}/fixed_{i}', search_action, 'search')
                observation = res[0]
                observation = self.get_clickable_actions(observation, language)
                # print(f'Action: {search_action}\nObservation: {observation}\n')
            except:
                history.append({"role": "user", "content": f'action error: {search_action}'})
                if loop:
                    reward, history = self.search_find_buy_item(i, observation, history=history, language=language, need_re_search=False, loop=True, re_search_times=re_search_times)
                else:
                    reward = 0
                return reward, history

        ########## find: prompt -> llm ##########
        action, history = self.model(observation, history=history, language=language)
        action = self.get_action(action)

        ########## Error handling ##########
        if language != 'ur' or 'ar':
            if action.startswith('['):
                pattern = r'\[(.*?)\]'
                match = re.search(pattern, action)
                if match:
                    action = match.group(1)
        ########## judgment statement ##########
        if action.lower().startswith(f'{env_click[language]}[') or action.lower().endswith(f']{env_click[language]}'):
            action_attr = 'click'
            pattern = r'\[(.*?)\]'
            match = re.search(pattern, action)
            if match:
                button = match.group(1)
            else:
                button = action
            try:
                ##### still find -> webshop #####
                if button == webshop_prev[language] or button == webshop_next[language] or button == f'< {webshop_prev[language]}' or button == f'{webshop_next[language]} >':
                    action = action.replace('< ', '')
                    action = action.replace(' >', '')
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, history = self.search_find_buy_item(i, observation, history=history, language=language, need_re_search=False, re_search_times=re_search_times)
                ##### re search -> webshop #####
                elif button == webshop_back_btu[language]:
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, history = self.search_find_buy_item(i, observation, history=history, language=language, need_re_search=True, re_search_times=re_search_times+1)
                ##### click buy btu -> webshop #####
                elif button == webshop_buy[language]:
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward = res[1]
                    history.append({"role": "user", "content": observation})
                    return reward, history
                ##### click item/attr -> webshop #####
                else:
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, history = self.search_find_buy_item(i, observation, history=history, language=language, need_re_search=False, re_search_times=re_search_times)
            except:
                # print(f'click item/attr/other error: {action}')
                history.append({"role": "user", "content": f'click item/attr/other error: {action}'})
                if loop:
                    reward, history = self.search_find_buy_item(i, observation, history=history, language=language, need_re_search=False, loop=True, re_search_times=re_search_times)
                else:
                    reward = 0
            return reward, history
        else:
            # print(f'action error: {action}')
            history.append({"role": "user", "content": f'action error: {action}'})
            if loop:
                reward, history = self.search_find_buy_item(i, observation, history=history, language=language, need_re_search=False, loop=True, re_search_times=re_search_times)
            else:
                reward = 0
            return reward, history
        
    def search_find_buy_item_trans(self, i, observation, info={}, language='en', need_re_search=False, loop=False, re_search_times=0, limit_re_search_times=3, translator='', translator_='', observation_list_lan=[], observation_list_en=[], self_trans=False):
        ########## init translator ##########
        if translator == '':
            if language == 'zh':
                translator = GoogleTranslator(source='zh-CN', target='en')
            else:
                translator = GoogleTranslator(source=language, target='en')
        if translator_ == '':
            if language == 'zh':
                translator_ = GoogleTranslator(target='en', source='zh-CN')
            else:
                translator_ = GoogleTranslator(target='en', source=language)
        if need_re_search:
            if re_search_times > limit_re_search_times:
                info['history'].append({"role": "user", "content": f'limit re search times'})
                reward = 0
                return reward, info
            try:
                re_search_times += 1
                ########## re search: prompt -> llm ##########
                search_action, info['history'] = self.model(observation, history=info['history'], language='en')
                search_action = self.get_action(search_action)
                if search_action == 'Not find \"Action: \", can\'t split.':
                    raise Exception
                ########## translate action ##########
                if self_trans:
                    search_action, history = self.model(search_action, history=[], language=language, mode='translate')
                else:
                    search_action = self.trans_api(translator_, search_action)
                ########## re search -> webshop ##########
                res = self.env.step(f'{language}/fixed_{i}', search_action, 'search')
                observation = res[0]
                observation_list_lan = self.get_clickable_actions_list(observation)
                ########## translate page ##########
                info['page'][i].append(observation)
                if self_trans:
                    observation, history = self.model(observation, history=[], language=language, mode='translate_en')
                else:
                    observation = self.trans_api(translator, observation)
                info['trans_page'][i].append(observation)
                observation_list_en = self.get_clickable_actions_list(observation)
                observation = self.get_clickable_actions(observation, language)
                # print(f'Action: {search_action}\nObservation: {observation}\n')
            except:
                info['history'].append({"role": "user", "content": f'action error: {search_action}'})
                if loop:
                    reward, info = self.search_find_buy_item_trans(i, observation, info=info, language=language, need_re_search=False, loop=True, re_search_times=re_search_times, translator=translator, translator_=translator_, observation_list_lan=observation_list_lan, observation_list_en=observation_list_en, self_trans=self_trans)
                else:
                    reward = 0
                return reward, info

        ########## find: prompt -> llm ##########
        action, info['history'] = self.model(observation, history=info['history'], language='en')
        action = self.get_action(action)

        ########## Error handling ##########
        if language != 'ur' or 'ar':
            if action.startswith('['):
                pattern = r'\[(.*?)\]'
                match = re.search(pattern, action)
                if match:
                    action = match.group(1)
        ########## judgment statement ##########
        env_click_ = env_click['en']
        if action.lower().startswith(f'{env_click_}[') or action.lower().endswith(f']{env_click_}'):
            action_attr = 'click'
            pattern = r'\[(.*?)\]'
            match = re.search(pattern, action)
            if match:
                button = match.group(1)
            else:
                button = action
            ########## translation mapping ##########
            button = button.replace(' >', '')
            button = button.replace('< ', '')
            button = button.lower()
            observation_list_en = [item.replace(' >', '') for item in observation_list_en]
            observation_list_en = [item.replace('< ', '') for item in observation_list_en]
            observation_list_en = [item.lower() for item in observation_list_en]
            if button in observation_list_en:
                index = observation_list_en.index(button)
                button = observation_list_lan[index]
                action = f'click[{button}]'
            else:
                webshop_click_list_en = [webshop_back_btu['en'], webshop_prev['en'], webshop_next['en'], webshop_buy['en'], webshop_description['en'], webshop_features['en'], webshop_reviews['en']]
                webshop_click_list_en = [item.lower() for item in webshop_click_list_en]
                webshop_click_list_lan = [webshop_back_btu[language], webshop_prev[language], webshop_next[language], webshop_buy[language], webshop_description[language], webshop_features[language], webshop_reviews[language]]
                if button in webshop_click_list_en:
                    index = webshop_click_list_en.index(button)
                    button = webshop_click_list_lan[index]
                    action = f'click[{button}]'
            try:
                ##### still find -> webshop #####
                if button == webshop_prev[language] or button == webshop_next[language] or button == ('< '+webshop_prev[language]) or button == (webshop_next[language]+' >'):
                    action = action.replace('< ', '')
                    action = action.replace(' >', '')
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation_list_lan = self.get_clickable_actions_list(observation)
                    ########## translate page ##########
                    info['page'][i].append(observation)
                    if self_trans:
                        observation, history = self.model(observation, history=[], language=language, mode='translate_en')
                    else:
                        observation = self.trans_api(translator, observation)
                    info['trans_page'][i].append(observation)
                    observation_list_en = self.get_clickable_actions_list(observation)
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, info = self.search_find_buy_item_trans(i, observation, info=info, language=language, need_re_search=False, re_search_times=re_search_times, translator=translator, translator_=translator_, observation_list_lan=observation_list_lan, observation_list_en=observation_list_en, self_trans=self_trans)
                ##### re search -> webshop #####
                elif button == webshop_back_btu[language]:
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation_list_lan = self.get_clickable_actions_list(observation)
                    ########## translate page ##########
                    info['page'][i].append(observation)
                    if self_trans:
                        observation, history = self.model(observation, history=[], language=language, mode='translate_en')
                    else:
                        observation = self.trans_api(translator, observation)
                    info['trans_page'][i].append(observation)
                    observation_list_en = self.get_clickable_actions_list(observation)
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, info = self.search_find_buy_item_trans(i, observation, info=info, language=language, need_re_search=True, re_search_times=re_search_times+1, translator=translator, translator_=translator_, observation_list_lan=observation_list_lan, observation_list_en=observation_list_en, self_trans=self_trans)
                ##### click buy btu -> webshop #####
                elif button == webshop_buy[language]:
                    ########## translate action ##########
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation_list_lan = self.get_clickable_actions_list(observation)
                    ########## translate page ##########
                    info['page'][i].append(observation)
                    if self_trans:
                        observation, history = self.model(observation, history=[], language=language, mode='translate_en')
                    else:
                        observation = self.trans_api(translator, observation)
                    info['trans_page'][i].append(observation)
                    observation_list_en = self.get_clickable_actions_list(observation)
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward = res[1]
                    info['history'].append({"role": "user", "content": observation})
                    return reward, info
                ##### click item/attr -> webshop #####
                else:
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation_list_lan = self.get_clickable_actions_list(observation)
                    ########## translate page ##########
                    info['page'][i].append(observation)
                    if self_trans:
                        observation, history = self.model(observation, history=[], language=language, mode='translate_en')
                    else:
                        observation = self.trans_api(translator, observation)
                    info['trans_page'][i].append(observation)
                    observation_list_en = self.get_clickable_actions_list(observation)
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, info = self.search_find_buy_item_trans(i, observation, info=info, language=language, need_re_search=False, re_search_times=re_search_times, translator=translator, translator_=translator_, observation_list_lan=observation_list_lan, observation_list_en=observation_list_en, self_trans=self_trans)
            except:
                # print(f'click item/attr/other error: {action}')
                info['history'].append({"role": "user", "content": f'click item/attr/other error: {action}'})
                if loop:
                    reward, info = self.search_find_buy_item_trans(i, observation, info=info, language=language, need_re_search=False, loop=True, re_search_times=re_search_times, translator=translator, translator_=translator_, observation_list_lan=observation_list_lan, observation_list_en=observation_list_en, self_trans=self_trans)
                else:
                    reward = 0
            return reward, info
        else:
            # print(f'action error: {action}')
            info['history'].append({"role": "user", "content": f'action error: {action}'})
            if loop:
                reward, info = self.search_find_buy_item_trans(i, observation, info=info, language=language, need_re_search=False, loop=True, re_search_times=re_search_times, translator=translator, translator_=translator_, observation_list_lan=observation_list_lan, observation_list_en=observation_list_en, self_trans=self_trans)
            else:
                reward = 0
            return reward, info
        
    def search_find_buy_item_clp(self, i, observation, histories=[], language='en', need_re_search=False, loop=False, re_search_times=0, limit_re_search_times=3, prev_action=''):
        if need_re_search:
            if re_search_times > limit_re_search_times:
                history = []
                history.append({"role": "user", "content": f'limit re search times'})
                histories.append(history)
                reward = 0
                return reward, histories
            try:
                re_search_times += 1
                ########## re search: prompt -> llm ##########
                ##### clp step.1 #####
                alignment, history = self.model(observation, history=[], language=language, mode='clp')
                ##### clp step.2 #####
                search_action, history = self.model(get_clp_2_prompt(prev_action, language), history=history, language=language)
                search_action = self.get_action(search_action)
                histories.append(history)
                prev_action = search_action
                if search_action == 'Not find \"Action: \", can\'t split.':
                    raise Exception
                ########## re search -> webshop ##########
                res = self.env.step(f'{language}/fixed_{i}', search_action, 'search')
                observation = res[0]
                observation = self.get_clickable_actions(observation, language)
                # print(f'Action: {search_action}\nObservation: {observation}\n')
            except:
                history = []
                history.append({"role": "user", "content": f'action error: {search_action}'})
                histories.append(history)
                if loop:
                    reward, histories = self.search_find_buy_item_clp(i, observation, histories=histories, language=language, need_re_search=False, loop=True, re_search_times=re_search_times, prev_action=prev_action)
                else:
                    reward = 0
                return reward, histories

        ########## find: prompt -> llm ##########
        ##### clp step.1 #####
        alignment, history = self.model(observation, history=[], language=language, mode='clp')
        ##### clp step.2 #####
        action, history = self.model(get_clp_2_prompt(prev_action, language), history=history, language=language)
        action = self.get_action(action)
        histories.append(history)
        prev_action = action
        ########## Error handling ##########
        if language != 'ur' or 'ar':
            if action.startswith('['):
                pattern = r'\[(.*?)\]'
                match = re.search(pattern, action)
                if match:
                    action = match.group(1)
        ########## judgment statement ##########
        if action.lower().startswith(f'{env_click[language]}[') or action.lower().endswith(f']{env_click[language]}'):
            action_attr = 'click'
            pattern = r'\[(.*?)\]'
            match = re.search(pattern, action)
            if match:
                button = match.group(1)
            else:
                button = action
            try:
                ##### still find -> webshop #####
                if button == webshop_prev[language] or button == webshop_next[language] or button == f'< {webshop_prev[language]}' or button == f'{webshop_next[language]} >':
                    action = action.replace('< ', '')
                    action = action.replace(' >', '')
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, histories = self.search_find_buy_item_clp(i, observation, histories=histories, language=language, need_re_search=False, re_search_times=re_search_times, prev_action=prev_action)
                ##### re search -> webshop #####
                elif button == webshop_back_btu[language]:
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, histories = self.search_find_buy_item_clp(i, observation, histories=histories, language=language, need_re_search=True, re_search_times=re_search_times+1, prev_action=prev_action)
                ##### click buy btu -> webshop #####
                elif button == webshop_buy[language]:
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward = res[1]
                    history = []
                    history.append({"role": "user", "content": observation})
                    histories.append(history)
                    return reward, histories
                ##### click item/attr -> webshop #####
                else:
                    res = self.env.step(f'{language}/fixed_{i}', action, action_attr)
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    reward, histories = self.search_find_buy_item_clp(i, observation, histories=histories, language=language, need_re_search=False, re_search_times=re_search_times, prev_action=prev_action)
            except:
                # print(f'click item/attr/other error: {action}')
                history = []
                history.append({"role": "user", "content": f'click item/attr/other error: {action}'})
                histories.append(history)
                if loop:
                    reward, histories = self.search_find_buy_item_clp(i, observation, histories=histories, language=language, need_re_search=False, loop=True, re_search_times=re_search_times, prev_action=prev_action)
                else:
                    reward = 0
            return reward, histories
        else:
            # print(f'action error: {action}')
            history = []
            history.append({"role": "user", "content": f'action error: {action}'})
            histories.append(history)
            if loop:
                reward, histories = self.search_find_buy_item_clp(i, observation, histories=histories, language=language, need_re_search=False, loop=True, re_search_times=re_search_times)
            else:
                reward = 0
            return reward, histories

    def test_direct(self, language, n=50):
        log_path = f'{self.saved_log_path}_{language}.json'
        logs = {}
        total_score = 0
        with tqdm(total=n) as pbar:
            for i in range(n):
                try:
                    # print('-'*10)
                    # print(f'No.{i + 1}')
                    ########## reset new page ##########
                    res = self.env.step(f'{language}/fixed_{i}', '', 'reset')
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {action}\nObservation: {observation}\n')
                    ########## search: prompt -> llm ##########
                    search_action, history = self.model(observation, history=[], language=language)
                    search_action = self.get_action(search_action)
                    ########## search -> webshop ##########
                    res = self.env.step(f'{language}/fixed_{i}', search_action, 'search')
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    # print(f'Action: {search_action}\nObservation: {observation}\n')
                    ########## find, re search, and get the item ##########
                    reward, history = self.search_find_buy_item(i, observation, history=history, language=language, need_re_search=False, loop=False)
                    total_score += reward
                    ########## end ##########
                    # print('score:', reward)
                    ########## end ##########
                    # print('-'*10)
                # if assert False
                except Exception as e:
                    # print(e)
                    history = history
                    reward = 0
                log = {
                        'history': history,
                        'reward': reward
                    }
                logs[i] = log
                pbar.update(1)
        logs = json.dumps(logs, ensure_ascii=False)
        output_file = open(log_path, 'w', encoding='utf-8')
        output_file.write(logs)
        output_file.close()
        total_score = total_score / n
        return total_score
    
    def test_translate_en(self, language, n=50):
        log_path = f'{self.saved_log_path}_{language}.json'
        logs = {}
        total_score = 0
        if language == 'zh':
            translator = GoogleTranslator(source='zh-CN', target='en')
            translator_ = GoogleTranslator(source='en', target='zh-CN')
        else:
            translator = GoogleTranslator(source=language, target='en')
            translator_ = GoogleTranslator(source='en', target=language)
        with tqdm(total=n) as pbar:
            for i in range(n):
                try:
                    ########## history, trans prepare ##########
                    info = {
                        'history': [],
                        'page':{},
                        'trans_page': {}
                    }
                    ########## reset new page ##########
                    res = self.env.step(f'{language}/fixed_{i}', '', 'reset')
                    observation = res[0]
                    ########## translate page ##########
                    info['page'][i] = []
                    info['page'][i].append(observation)
                    observation = self.trans_api(translator, observation)
                    info['trans_page'][i] = []
                    info['trans_page'][i].append(observation)
                    observation = self.get_clickable_actions(observation, 'en')
                    ########## search: prompt -> llm ##########
                    search_action, info['history'] = self.model(observation, history=[], language='en')
                    search_action = self.get_action(search_action)
                    ########## translate action ##########
                    search_action = self.trans_api(translator_, search_action)
                    ########## search -> webshop ##########
                    res = self.env.step(f'{language}/fixed_{i}', search_action, 'search')
                    observation = res[0]
                    observation_list_lan = self.get_clickable_actions_list(observation)
                    ########## translate page ##########
                    info['page'][i].append(observation)
                    observation = self.trans_api(translator, observation)
                    info['trans_page'][i].append(observation)
                    observation_list_en = self.get_clickable_actions_list(observation)
                    observation = self.get_clickable_actions(observation, language)
                    ########## find, re search, and get the item ##########
                    reward, info = self.search_find_buy_item_trans(i, observation, info=info, language=language, need_re_search=False, loop=False, translator=translator, translator_=translator_, observation_list_lan=observation_list_lan, observation_list_en=observation_list_en)
                    total_score += reward
                    ########## end ##########
                except Exception as e:
                    # print(e)
                    info = info
                    reward = 0
                log = {
                        'info': info,
                        'reward': reward
                    }
                logs[i] = log
                pbar.update(1)
        logs = json.dumps(logs, ensure_ascii=False)
        output_file = open(log_path, 'w', encoding='utf-8')
        output_file.write(logs)
        output_file.close()
        total_score = total_score / n
        return total_score

    def test_self_translate_en(self, language, n=50):
        log_path = f'{self.saved_log_path}_{language}.json'
        logs = {}
        total_score = 0
        if language == 'zh':
            translator = GoogleTranslator(source='zh-CN', target='en')
            translator_ = GoogleTranslator(source='en', target='zh-CN')
        else:
            translator = GoogleTranslator(source=language, target='en')
            translator_ = GoogleTranslator(source='en', target=language)
        with tqdm(total=n) as pbar:
            for i in range(n):
                try:
                    ########## history, trans prepare ##########
                    info = {
                        'history': [],
                        'page':{},
                        'trans_page': {}
                    }
                    ########## reset new page ##########
                    res = self.env.step(f'{language}/fixed_{i}', '', 'reset')
                    observation = res[0]
                    ########## translate page ##########
                    info['page'][i] = []
                    info['page'][i].append(observation)
                    observation, history = self.model(observation, history=[], language=language, mode='translate_en')
                    info['trans_page'][i] = []
                    info['trans_page'][i].append(observation)
                    observation = self.get_clickable_actions(observation, 'en')
                    ########## search: prompt -> llm ##########
                    search_action, info['history'] = self.model(observation, history=[], language='en')
                    search_action = self.get_action(search_action)
                    ########## translate action ##########
                    search_action, history = self.model(search_action, history=[], language=language, mode='translate')
                    ########## search -> webshop ##########
                    res = self.env.step(f'{language}/fixed_{i}', search_action, 'search')
                    observation = res[0]
                    observation_list_lan = self.get_clickable_actions_list(observation)
                    ########## translate page ##########
                    info['page'][i].append(observation)
                    observation, history = self.model(observation, history=[], language=language, mode='translate_en')
                    info['trans_page'][i].append(observation)
                    observation_list_en = self.get_clickable_actions_list(observation)
                    observation = self.get_clickable_actions(observation, language)
                    ########## find, re search, and get the item ##########
                    reward, info = self.search_find_buy_item_trans(i, observation, info=info, language=language, need_re_search=False, loop=False, translator=translator, translator_=translator_, observation_list_lan=observation_list_lan, observation_list_en=observation_list_en, self_trans=True)
                    total_score += reward
                    ########## end ##########
                except Exception as e:
                    # print(e)
                    info = info
                    reward = 0
                log = {
                        'info': info,
                        'reward': reward
                    }
                logs[i] = log
                pbar.update(1)
        logs = json.dumps(logs, ensure_ascii=False)
        output_file = open(log_path, 'w', encoding='utf-8')
        output_file.write(logs)
        output_file.close()
        total_score = total_score / n
        return total_score

    def test_clp_en(self, language, n=50):
        log_path = f'{self.saved_log_path}_{language}.json'
        logs = {}
        total_score = 0
        with tqdm(total=n) as pbar:
            for i in range(n):
                try:
                    histories = []
                    ########## reset new page ##########
                    res = self.env.step(f'{language}/fixed_{i}', '', 'reset')
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    ########## search: prompt -> llm ##########
                    ##### clp step.1 #####
                    alignment, history = self.model(observation, history=[], language=language, mode='clp')
                    ##### clp step.2 #####
                    search_action, history = self.model(get_clp_2_prompt('', language), history=history, language=language)
                    search_action = self.get_action(search_action)
                    histories.append(history)
                    prev_action = search_action
                    ########## search -> webshop ##########
                    res = self.env.step(f'{language}/fixed_{i}', search_action, 'search')
                    observation = res[0]
                    observation = self.get_clickable_actions(observation, language)
                    ########## find, re search, and get the item ##########
                    reward, histories = self.search_find_buy_item_clp(i, observation, histories=histories, language=language, need_re_search=False, loop=False, prev_action=prev_action)
                    total_score += reward
                    ########## end ##########
                except Exception as e:
                    # print(e)
                    histories = histories
                    reward = 0
                log = {
                        'histories': histories,
                        'reward': reward
                    }
                logs[i] = log
                pbar.update(1)
        logs = json.dumps(logs, ensure_ascii=False)
        output_file = open(log_path, 'w', encoding='utf-8')
        output_file.write(logs)
        output_file.close()
        total_score = total_score / n
        return total_score