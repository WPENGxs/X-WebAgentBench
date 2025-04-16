import argparse, json, logging, random
from pathlib import Path
from ast import literal_eval

from flask import (
    Flask,
    request,
    redirect,
    url_for
)

from rich import print

from web_agent_site.engine.engine import (
    load_products,
    init_search_engine,
    convert_web_app_string_to_var,
    get_top_n_product_from_keywords,
    get_product_per_page,
    map_action_to_html,
    END_BUTTON
)
from web_agent_site.engine.goal import get_reward, get_goals
from web_agent_site.utils import (
    generate_mturk_code,
    setup_logger,
    DEFAULT_FILE_PATH,
    DEBUG_PROD_SIZE,
)

from web_agent_site.multilingual_text import (
    webshop_title,
    webshop_instruction,
    webshop_search_hint,
    webshop_search,
    webshop_back_btu,
    webshop_page,
    webshop_total_results,
    webshop_prev,
    webshop_next,
    webshop_buy,
    webshop_price,
    webshop_rating,
    webshop_description,
    webshop_features,
    webshop_reviews,
    webshop_attributes,
    webshop_end,
    webshop_code,
    webshop_mturk,
    webshop_score,
)

app = Flask(__name__)

search_engine = {
    'en': None,
    'zh': None,
    'fr': None,
    'es': None, 
    'de': None, 
    'el': None, 
    'bg': None, 
    'ru': None, 
    'tr': None, 
    'ar': None, 
    'vi': None, 
    'th': None, 
    'hi': None, 
    'sw': None, 
    'ur': None
}
all_products = {
    'en': None,
    'zh': None,
    'fr': None,
    'es': None, 
    'de': None, 
    'el': None, 
    'bg': None, 
    'ru': None, 
    'tr': None, 
    'ar': None, 
    'vi': None, 
    'th': None, 
    'hi': None, 
    'sw': None, 
    'ur': None
}
product_item_dict = {
    'en': None,
    'zh': None,
    'fr': None,
    'es': None, 
    'de': None, 
    'el': None, 
    'bg': None, 
    'ru': None, 
    'tr': None, 
    'ar': None, 
    'vi': None, 
    'th': None, 
    'hi': None, 
    'sw': None, 
    'ur': None
}
product_prices = {
    'en': None,
    'zh': None,
    'fr': None,
    'es': None, 
    'de': None, 
    'el': None, 
    'bg': None, 
    'ru': None, 
    'tr': None, 
    'ar': None, 
    'vi': None, 
    'th': None, 
    'hi': None, 
    'sw': None, 
    'ur': None
}
attribute_to_asins = {
    'en': None,
    'zh': None,
    'fr': None,
    'es': None, 
    'de': None, 
    'el': None, 
    'bg': None, 
    'ru': None, 
    'tr': None, 
    'ar': None, 
    'vi': None, 
    'th': None, 
    'hi': None, 
    'sw': None, 
    'ur': None
}
goals = {
    'en': None,
    'zh': None,
    'fr': None,
    'es': None, 
    'de': None, 
    'el': None, 
    'bg': None, 
    'ru': None, 
    'tr': None, 
    'ar': None, 
    'vi': None, 
    'th': None, 
    'hi': None, 
    'sw': None, 
    'ur': None
}
weights = {
    'en': None,
    'zh': None,
    'fr': None,
    'es': None, 
    'de': None, 
    'el': None, 
    'bg': None, 
    'ru': None, 
    'tr': None, 
    'ar': None, 
    'vi': None, 
    'th': None, 
    'hi': None, 
    'sw': None, 
    'ur': None
}

user_sessions = {
    'en': dict(),
    'zh': dict(),
    'fr': dict(),
    'es': dict(), 
    'de': dict(), 
    'el': dict(), 
    'bg': dict(), 
    'ru': dict(), 
    'tr': dict(), 
    'ar': dict(), 
    'vi': dict(), 
    'th': dict(), 
    'hi': dict(), 
    'sw': dict(), 
    'ur': dict()
}
user_log_dir = None
SHOW_ATTRS_TAB = False

goal_en = None

@app.route('/')
def home():
    return redirect(url_for('index', language="en", session_id="abc"))

@app.route('/<language>/<session_id>', methods=['GET', 'POST'])
def index(language, session_id):
    
    global user_log_dir
    global all_products, product_item_dict, \
           product_prices, attribute_to_asins, \
           search_engine, \
           goals, weights, user_sessions
    global goal_en

    if search_engine[language] is None:
        print('Error, shuffle file not load!')

    if session_id not in user_sessions[language] and 'fixed' in session_id:
        goal_dix = int(session_id.split('_')[-1])
        goal = goals[language][goal_dix]
        instruction_text = goal['instruction_text']
        user_sessions[language][session_id] = {'goal': goal, 'done': False}
        if user_log_dir is not None:
            setup_logger(session_id, user_log_dir)
    elif session_id not in user_sessions[language]:
        goal = random.choices(goals[language], weights[language])[0]
        instruction_text = goal['instruction_text']
        user_sessions[language][session_id] = {'goal': goal, 'done': False}
        if user_log_dir is not None:
            setup_logger(session_id, user_log_dir)
    else:
        instruction_text = user_sessions[language][session_id]['goal']['instruction_text']

    if request.method == 'POST' and 'search_query' in request.form:
        keywords = request.form['search_query'].lower().split(' ')
        return redirect(url_for(
            'search_results',
            language=language,
            session_id=session_id,
            keywords=keywords,
            page=1,
        ))
    if user_log_dir is not None:
        logger = logging.getLogger(session_id)
        logger.info(json.dumps(dict(
            page='index',
            language=language,
            url=request.url,
            goal=user_sessions[language][session_id]['goal'],
        )))
    return map_action_to_html(
        'start',
        language=language,
        session_id=session_id,
        instruction_text=instruction_text,
        webshop_title=webshop_title[language],
        webshop_instruction=webshop_instruction[language],
        webshop_search_hint=webshop_search_hint[language],
        webshop_search=webshop_search[language],
    )


@app.route(
    '/search_results/<language>/<session_id>/<keywords>/<page>',
    methods=['GET', 'POST']
)
def search_results(language, session_id, keywords, page):
    instruction_text = user_sessions[language][session_id]['goal']['instruction_text']
    page = convert_web_app_string_to_var('page', page)
    keywords = convert_web_app_string_to_var('keywords', keywords)
    top_n_products = get_top_n_product_from_keywords(
        keywords,
        search_engine[language],
        all_products[language],
        product_item_dict[language],
        attribute_to_asins[language],
    )

    products = get_product_per_page(top_n_products, page)
    html = map_action_to_html(
        'search',
        language=language,
        session_id=session_id,
        products=products,
        keywords=keywords,
        page=page,
        total=len(top_n_products),
        instruction_text=instruction_text,
        webshop_instruction=webshop_instruction[language],
        webshop_back_btu=webshop_back_btu[language],
        webshop_page=webshop_page[language],
        webshop_total_results=webshop_total_results[language],
        webshop_prev=webshop_prev[language],
        webshop_next=webshop_next[language],
    )
    logger = logging.getLogger(session_id)
    logger.info(json.dumps(dict(
        page='search_results',
        language=language,
        url=request.url,
        goal=user_sessions[language][session_id]['goal'],
        content=dict(
            keywords=keywords,
            search_result_asins=[p['asin'] for p in products],
            page=page,
            webshop_instruction=webshop_instruction[language],
            webshop_back_btu=webshop_back_btu[language],
            webshop_page=webshop_page[language],
            webshop_total_results=webshop_total_results[language],
            webshop_prev=webshop_prev[language],
            webshop_next=webshop_next[language],
        )
    )))
    return html


@app.route(
    '/item_page/<language>/<session_id>/<asin>/<keywords>/<page>/<options>',
    methods=['GET', 'POST']
)
def item_page(language, session_id, asin, keywords, page, options):
    options = literal_eval(options)
    product_info = product_item_dict[language][asin]

    goal_instruction = user_sessions[language][session_id]['goal']['instruction_text']
    product_info['goal_instruction'] = goal_instruction

    html = map_action_to_html(
        'click',
        language=language,
        session_id=session_id,
        product_info=product_info,
        keywords=keywords,
        page=page,
        asin=asin,
        options=options,
        instruction_text=goal_instruction,
        show_attrs=SHOW_ATTRS_TAB,
        webshop_instruction=webshop_instruction[language],
        webshop_back_btu=webshop_back_btu[language],
        webshop_prev=webshop_prev[language],
        webshop_buy=webshop_buy[language],
        webshop_price=webshop_price[language],
        webshop_rating=webshop_rating[language],
        webshop_description=webshop_description[language],
        webshop_features=webshop_features[language],
        webshop_reviews=webshop_reviews[language],
        webshop_attributes=webshop_attributes[language],
    )
    logger = logging.getLogger(session_id)
    logger.info(json.dumps(dict(
        page='item_page',
        language=language,
        url=request.url,
        goal=user_sessions[language][session_id]['goal'],
        content=dict(
            keywords=keywords,
            page=page,
            asin=asin,
            options=options,
        )
    )))
    return html


@app.route(
    '/item_sub_page/<language>/<session_id>/<asin>/<keywords>/<page>/<sub_page>/<options>',
    methods=['GET', 'POST']
)
def item_sub_page(language, session_id, asin, keywords, page, sub_page, options):
    options = literal_eval(options)
    product_info = product_item_dict[language][asin]

    goal_instruction = user_sessions[language][session_id]['goal']['instruction_text']
    product_info['goal_instruction'] = goal_instruction

    html = map_action_to_html(
        f'click[{sub_page}]',
        language=language,
        session_id=session_id,
        product_info=product_info,
        keywords=keywords,
        page=page,
        asin=asin,
        options=options,
        instruction_text=goal_instruction,
        webshop_instruction=webshop_instruction[language],
        webshop_back_btu=webshop_back_btu[language],
        webshop_prev=webshop_prev[language],
    )
    logger = logging.getLogger(session_id)
    logger.info(json.dumps(dict(
        page='item_sub_page',
        language=language,
        url=request.url,
        goal=user_sessions[language][session_id]['goal'],
        content=dict(
            keywords=keywords,
            page=page,
            asin=asin,
            options=options,
        )
    )))
    return html


@app.route('/done/<language>/<session_id>/<asin>/<options>', methods=['GET', 'POST'])
def done(language, session_id, asin, options):
    goal_dix = int(session_id.split('_')[-1])

    options = literal_eval(options)
    goal = goals[language][goal_dix]
    purchased_product = product_item_dict[language][asin]
    purchased_product_en = product_item_dict['en'][asin]
    goal_en = None
    for g in goals['en']:
        if goal['asin'] == g['asin']:
            goal_en = g
            break
    price = product_prices[language][asin]

    reward, reward_info = get_reward(
        purchased_product,
        goal,
        purchased_product_en,
        goal_en,
        price=price,
        options=options,
        verbose=True
    )
    user_sessions[language][session_id]['done'] = True
    user_sessions[language][session_id]['reward'] = reward
    # print(user_sessions)

    logger = logging.getLogger(session_id)
    logger.info(json.dumps(dict(
        page='done',
        language=language,
        url=request.url,
        goal=goal,
        content=dict(
            asin=asin,
            options=options,
            price=price,
        ),
        reward=reward,
        reward_info=reward_info,
    )))
    del logging.root.manager.loggerDict[session_id]
    
    return map_action_to_html(
        f'click[{END_BUTTON}]',
        language=language,
        session_id=session_id,
        reward=reward,
        asin=asin,
        options=options,
        reward_info=reward_info,
        query=purchased_product['query'],
        category=purchased_product['category'],
        product_category=purchased_product['product_category'],
        goal_attrs=user_sessions[language][session_id]['goal']['attributes'],
        purchased_attrs=purchased_product['Attributes'],
        goal=goal,
        mturk_code=generate_mturk_code(session_id),
        webshop_end=webshop_end[language],
        webshop_code=webshop_code[language],
        webshop_mturk=webshop_mturk[language],
        webshop_score=webshop_score[language],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebShop flask app backend configuration")
    parser.add_argument("--log", action='store_true', help="Log actions on WebShop in trajectory file")
    parser.add_argument("--attrs", action='store_true', help="Show attributes tab in item page")

    languages = ['en', 'zh', 'fr', 'es', 'de', 'el', 'bg', 'ru', 'tr', 'ar', 'vi', 'th', 'hi', 'sw', 'ur']

    for lan in languages:
        shuffle_file_path = DEFAULT_FILE_PATH + f'items_shuffle_40k_{lan}.json'
        attr_path = f'items_ins_v2_40k_{lan}.json'
        human_path = f'items_human_ins_{lan}.json'
        print('-'*40)
        print(f'load {lan} data...')
        all_products[lan], product_item_dict[lan], product_prices[lan], attribute_to_asins[lan] = \
            load_products(
                filepath=shuffle_file_path,
                attr_path=attr_path,
                human_attr_path=human_path,
                num_products=DEBUG_PROD_SIZE
            )
        search_engine[lan] = init_search_engine(lan, num_products=DEBUG_PROD_SIZE)

        goals[lan] = get_goals(all_products[lan], product_prices[lan], language=lan)
        # random.seed(233)
        # random.shuffle(goals)
        weights[lan] = [goal['weight'] for goal in goals[lan]]
    print('All files load done.')

    args = parser.parse_args()
    if args.log:
        user_log_dir = Path('user_session_logs/mturk')
        user_log_dir.mkdir(parents=True, exist_ok=True)
    SHOW_ATTRS_TAB = args.attrs

    app.run(host='0.0.0.0', port=3000)
