import logging
from datetime import datetime, timedelta
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuração do token e logging
my_secret = os.getenv('token')  # Carrega o token do arquivo .env
my_secret = os.environ['token']  # Para Replit (ou outro ambiente)

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
        'no_proxies_msg': "No proxies available at the moment. Please try again later.",
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
        'socks_msg': "Aqui estão seus SOCKS proxies:",
        'no_proxies_msg': "Nenhum proxy disponível no momento. Por favor, tente novamente mais tarde.",
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
        return [], language['no_proxies_msg']

    if data and isinstance(data, list):
        filtered_proxies = sorted(
            (proxy for proxy in data if proxy.get('ping', float('inf')) <= 500),
            key=lambda x: x['ping']
        )[:10]

        if not filtered_proxies:
            return [], language['no_proxies_msg']

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

    return [], language['no_proxies_msg']

def format_proxy_info(proxy, proxy_type, language):
    """Formata informações do proxy para exibição ao usuário."""
    return (
        f"🌍 {language['country']}: {proxy.get('country', 'N/A')}\n"
        f"🔗 {language['host']}: {proxy['host'] if proxy_type == 'mtproto' else proxy['ip']}\n"
        f"🚪 {language['port']}: {proxy['port']}\n"
        f"🔑 {language['secret']}: {proxy.get('secret', 'N/A')}\n"
        f"📈 {language['uptime']}: {proxy.get('uptime', 'N/A')}%\n"
        f"📶 {language['ping']}: {proxy.get('ping', 'N/A')} ms\n"
        f"📅 {language['added_on']}: {convert_timestamp(proxy.get('addTime', datetime.now().timestamp()))}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exibe as opções de idioma ao usuário quando o comando /start é enviado."""
    keyboard = [
        [InlineKeyboardButton("🏴 English", callback_data='lang_en'),
         InlineKeyboardButton("🇧🇷 Português", callback_data='lang_pt')]
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
            await query.message.reply_text(proxy_info_text, reply_markup=reply_markup)

def main() -> None:
    """Inicializa o bot e configura os handlers."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
