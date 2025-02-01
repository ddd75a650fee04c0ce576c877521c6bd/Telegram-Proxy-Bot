import os
import logging
from datetime import datetime, timedelta
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Configuração do token
if 'TOKEN' in os.environ:
    TOKEN = os.environ['TOKEN']  # Para ambientes como Replit
else:
    load_dotenv()  # Carrega variáveis do arquivo .env
    TOKEN = os.getenv('TOKEN')  # Para execução local com .env

# Permite que o usuário defina o token diretamente no main.py
if not TOKEN:
    TOKEN = "SEU_TOKEN_AQUI"  # Substitua por seu token diretamente no código

if not TOKEN or TOKEN == "SEU_TOKEN_AQUI":
    raise ValueError("Token não encontrado! Configure a variável 'TOKEN' no ambiente, .env ou diretamente no main.py.")

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Traduções para múltiplos idiomas
LANGUAGES = {
    'en': {
        'greeting': "Hi! Choose an option:",
        'mtproto_button': "MTProto Proxies",
        'socks_button': "SOCKS Proxies",
        'refresh_button': "Refresh",
        'connect': "Connect to",
        'switch_to_mtproto': "Switch to MTProto",
        'switch_to_socks': "Switch to SOCKS",
        'language_changed': "Language changed to English.",
        'mtproto_msg': "Here are your MTProto proxies:",
        'socks_msg': "Here are your SOCKS proxies:",
        'no_proxies': "No proxies are currently available.",
        'country': "Country",
        'host': "Host",
        'port': "Port",
        'secret': "Secret",
        'uptime': "Uptime",
        'ping': "Ping",
        'upload': "Upload",
        'download': "Download",
        'added_on': "Added on",
        'choose_language': "Please choose your language:"
    },
    'pt': {
        'greeting': "Olá! Escolha uma opção:",
        'mtproto_button': "Proxies MTProto",
        'socks_button': "Proxies SOCKS",
        'refresh_button': "Atualizar",
        'connect': "Conectar a",
        'switch_to_mtproto': "Trocar para MTProto",
        'switch_to_socks': "Trocar para SOCKS",
        'language_changed': "Idioma alterado para português.",
        'mtproto_msg': "Aqui estão seus proxies MTProto:",
        'socks_msg': "Aqui estão seus proxies SOCKS:",
        'no_proxies': "Nenhum proxy está disponível no momento.",
        'country': "País",
        'host': "Host",
        'port': "Porta",
        'secret': "Segredo",
        'uptime': "Tempo ativo",
        'ping': "Ping",
        'upload': "Upload",
        'download': "Download",
        'added_on': "Adicionado em",
        'choose_language': "Por favor, escolha seu idioma:"
    },
    'es': {
        'greeting': "¡Hola! Elige una opción:",
        'mtproto_button': "Proxies MTProto",
        'socks_button': "Proxies SOCKS",
        'refresh_button': "Actualizar",
        'connect': "Conectar a",
        'switch_to_mtproto': "Cambiar a MTProto",
        'switch_to_socks': "Cambiar a SOCKS",
        'language_changed': "Idioma cambiado a español.",
        'mtproto_msg': "Aquí están tus MTProto proxies:",
        'socks_msg': "Aquí están tus SOCKS proxies:",
        'no_proxies': "No hay proxies disponibles en este momento.",
        'country': "País",
        'host': "Host",
        'port': "Puerto",
        'secret': "Secreto",
        'uptime': "Tiempo activo",
        'ping': "Ping",
        'upload': "Subida",
        'download': "Descarga",
        'added_on': "Añadido en",
        'choose_language': "Por favor, elige tu idioma:"
    },
    'ru': {
        'greeting': "Привет! Выберите опцию:",
        'mtproto_button': "MTProto прокси",
        'socks_button': "SOCKS прокси",
        'refresh_button': "Обновить",
        'connect': "Подключиться к",
        'switch_to_mtproto': "Переключиться на MTProto",
        'switch_to_socks': "Переключиться на SOCKS",
        'language_changed': "Язык изменён на русский.",
        'mtproto_msg': "Вот ваши MTProto прокси:",
        'socks_msg': "Вот ваши SOCKS прокси:",
        'no_proxies': "В настоящее время нет доступных прокси.",
        'country': "Страна",
        'host': "Хост",
        'port': "Порт",
        'secret': "Секрет",
        'uptime': "Время работы",
        'ping': "Пинг",
        'upload': "Загрузка",
        'download': "Скачивание",
        'added_on': "Добавлено",
        'choose_language': "Пожалуйста, выберите язык:"
    },
    'ar': {
        'greeting': "مرحبًا! اختر خيارًا:",
        'mtproto_button': "بروكسي MTProto",
        'socks_button': "بروكسي SOCKS",
        'refresh_button': "تحديث",
        'connect': "اتصل بـ",
        'switch_to_mtproto': "التبديل إلى MTProto",
        'switch_to_socks': "التبديل إلى SOCKS",
        'language_changed': "تم تغيير اللغة إلى العربية.",
        'mtproto_msg': "ها هي بروكسيات MTProto الخاصة بك:",
        'socks_msg': "ها هي بروكسيات SOCKS الخاصة بك:",
        'no_proxies': "لا توجد بروكسيات متاحة حاليًا.",
        'country': "الدولة",
        'host': "المضيف",
        'port': "المنفذ",
        'secret': "السر",
        'uptime': "وقت التشغيل",
        'ping': "وقت الاستجابة",
        'upload': "الرفع",
        'download': "التنزيل",
        'added_on': "تمت الإضافة في",
        'choose_language': "يرجى اختيار لغتك:"
    },
    'zh': {
        'greeting': "你好！选择一个选项：",
        'mtproto_button': "MTProto代理",
        'socks_button': "SOCKS代理",
        'refresh_button': "刷新",
        'connect': "连接到",
        'switch_to_mtproto': "切换到MTProto",
        'switch_to_socks': "切换到SOCKS",
        'language_changed': "语言已更改为中文。",
        'mtproto_msg': "这是您的MTProto代理：",
        'socks_msg': "这是您的SOCKS代理：",
        'no_proxies': "目前没有可用的代理。",
        'country': "国家",
        'host': "主机",
        'port': "端口",
        'secret': "密钥",
        'uptime': "在线时间",
        'ping': "延迟",
        'upload': "上传",
        'download': "下载",
        'added_on': "添加于",
        'choose_language': "请选择您的语言："
    }
}

# Cache para armazenar proxies
proxy_cache = {
    'mtproto': {'data': None, 'expires_at': datetime.min},
    'socks': {'data': None, 'expires_at': datetime.min}
}

def convert_timestamp(timestamp):
    """Converte um timestamp Unix para um formato legível."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def fetch_proxies(proxy_type, language):
    """Busca proxies do tipo especificado e retorna botões e informações formatadas."""
    now = datetime.now()
    if proxy_cache[proxy_type]['data'] and proxy_cache[proxy_type]['expires_at'] > now:
        return proxy_cache[proxy_type]['data']

    url = f"https://mtpro.xyz/api/?type={proxy_type}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Erro ao buscar proxies {proxy_type}: {e}")
        return [], language['no_proxies']

    if data and isinstance(data, list):
        filtered_proxies = sorted(
            (proxy for proxy in data if proxy.get('ping', float('inf')) <= 300 and proxy.get('uptime', 0) >= 95),
            key=lambda x: (x['ping'], -x['uptime'])
        )[:10]

        if not filtered_proxies:
            return [], language['no_proxies']

        buttons = []
        proxy_info_texts = []
        for proxy in filtered_proxies:
            label_connect = f"{language['connect']} {proxy['host']}" if proxy_type == 'mtproto' else f"{language['connect']} {proxy['ip']}"
            url_connect = (
                f"https://t.me/proxy?server={proxy['host']}&port={proxy['port']}&secret={proxy['secret']}"
                if proxy_type == 'mtproto' else
                f"tg://socks?server={proxy['ip']}&port={proxy['port']}"
            )
            buttons.append([InlineKeyboardButton(label_connect, url=url_connect)])
            proxy_info_texts.append(format_proxy_info(proxy, proxy_type, language))

        # Adiciona botões de atualizar e trocar protocolo
        buttons.append([InlineKeyboardButton(language['refresh_button'], callback_data=proxy_type)])
        buttons.append([InlineKeyboardButton(
            language['switch_to_mtproto'] if proxy_type == 'socks' else language['switch_to_socks'],
            callback_data='mtproto' if proxy_type == 'socks' else 'socks'
        )])

        proxy_cache[proxy_type] = {
            'data': (buttons, "\n\n".join(proxy_info_texts)),
            'expires_at': now + timedelta(minutes=5)
        }
        return buttons, "\n\n".join(proxy_info_texts)

    return [], language['no_proxies']

def format_proxy_info(proxy, proxy_type, language):
    """Formata informações do proxy para exibição ao usuário."""
    return (
        f"🌍 {language['country']}: {proxy.get('country', 'N/A')}\n"
        f"🔗 {language['host']}: {proxy['host'] if proxy_type == 'mtproto' else proxy['ip']}\n"
        f"🚪 {language['port']}: {proxy['port']}\n"
        f"🔑 {language['secret']}: {proxy.get('secret', 'N/A')}\n"
        f"📈 {language['uptime']}: {proxy.get('uptime', 'N/A')}%\n"
        f"📶 {language['ping']}: {proxy.get('ping', 'N/A')} ms\n"
        f"📅 {language['added_on']}: {convert_timestamp(proxy['addTime'])}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exibe as opções de idioma ao usuário quando o comando /start é enviado."""
    keyboard = [
        [InlineKeyboardButton("🏴 English", callback_data='lang_en'),
         InlineKeyboardButton("🇧🇷 Português", callback_data='lang_pt')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
         InlineKeyboardButton("🇵🇸 العربية", callback_data='lang_ar')],
        [InlineKeyboardButton("🇦🇷 Español", callback_data='lang_es'),
         InlineKeyboardButton("🇨🇳 中文", callback_data='lang_zh')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose your language:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manipula cliques nos botões Inline."""
    query = update.callback_query

    if not query:
        return

    user_language_code = context.user_data.get('language', 'en')
    translation = LANGUAGES[user_language_code]

    if query.data.startswith('lang_'):
        selected_language = query.data.split('_')[1]
        context.user_data['language'] = selected_language
        translation = LANGUAGES[selected_language]
        await query.answer()
        await query.message.reply_text(translation['language_changed'])

        keyboard = [
            [InlineKeyboardButton(translation['mtproto_button'], callback_data='mtproto')],
            [InlineKeyboardButton(translation['socks_button'], callback_data='socks')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(translation['greeting'], reply_markup=reply_markup)

    elif query.data in ['mtproto', 'socks']:
        await query.answer()
        buttons, proxy_info_text = fetch_proxies(query.data, translation)

        if proxy_info_text:
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.reply_text(
                f"{translation['mtproto_msg'] if query.data == 'mtproto' else translation['socks_msg']}\n\n{proxy_info_text}",
                reply_markup=reply_markup
            )
        else:
            await query.message.reply_text(translation['no_proxies'])

def main() -> None:
    """Inicializa o bot e configura os handlers."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
