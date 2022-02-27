import json
import os
import time
import uuid
import logging

import telepot
from prettytable import PrettyTable
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from PIL import Image, ImageDraw

from controller.sqlalchemy_start import sqlalchemy_starter
from model.compra import Compra
from model.paramentrosistema import ParametroSistema

Session, Base, engine = sqlalchemy_starter()
Base.metadata.create_all(engine)
session = Session()

TOKEN = session.query(ParametroSistema).filter(ParametroSistema.nome == 'telegram_token')[0].valor
REQUESTER_ID = session.query(ParametroSistema).filter(ParametroSistema.nome == 'requester_id')[0].valor
URL_API = session.query(ParametroSistema).filter(ParametroSistema.nome == 'url_api')[0].valor
MESES_DO_ANO = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO",
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO"
}
bot = telepot.Bot(TOKEN)


def handle(msg):
    try:
        if 'inline_keyboard' in str(msg):
            query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
            bot.answerCallbackQuery(query_id, text='Carregando dados do mês')
            checar_condicoes_de_retorno(msg, False)
        else:
            checar_condicoes_de_retorno(msg, True)
    except Exception as e:
        logging.exception(e)


def meses_botoes():
    return [{"texto_botao": MESES_DO_ANO[i], "callback": '1-' + str(i)} for i in MESES_DO_ANO]


def cadastrar_compra(compra):
    try:
        item = {
            "cartao_id": compra.cartao_id,
            "titulo": compra.titulo,
            "valor": compra.valor,
            "qtd_parcelas": compra.qtd_parcelas
        }
        r = requests.post('{URL_API}/compra', json=item)
        return r.status_code
    except Exception as e:
        logging.exception(e)


def gerar_imagem(tabela, qtd_linhas):
    try:
        definir_height = qtd_linhas / 5 if qtd_linhas > 5 else 1
        img = Image.new('RGB', (350, int(160 * definir_height)), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10, 10), tabela)
        tabela_em_imagem = f'{uuid.uuid4().hex}.png'
        img.save(f'img_outputs\{tabela_em_imagem}')
    except Exception as e:
        logging.exception(e)

    return tabela_em_imagem


def get_total_mes(cartao_id, mes):
    r = requests.get(f'{URL_API}/compra/{cartao_id}/{mes}')
    t = PrettyTable(['Data Compra', 'Título', 'Valor'])
    qtd_linhas = 0
    for i in json.loads(r.text):
        t.add_row([i['data'], i['titulo'], i['valor']])
        qtd_linhas += 1
    return gerar_imagem(str(t), qtd_linhas)


def checar_condicoes_de_retorno(msg, is_texto):
    try:
        if msg.get('text', None) == '/mesescc' and is_texto:
            send_button_telepot("Escolha o mês:", meses_botoes())
        elif str(msg.get('text', None)).upper().startswith('COMPREI') and is_texto:
            dados_da_compra = str(msg.get('text', None)).split(' ')[1].split('/')
            compra = Compra(dados_da_compra[0], dados_da_compra[1], dados_da_compra[2], dados_da_compra[3])
            cadastrar_compra(compra)
        elif '-' in str(msg.get('data', None)):
            dado = msg.get('data', None)
            cartao_id, mes = dado.split('-')[0], dado.split('-')[1]
            bot.sendMessage(REQUESTER_ID, f'Buscando dados do mês {mes}...')
            photo = f'img_outputs\{get_total_mes(cartao_id, mes)}'
            bot.sendPhoto(REQUESTER_ID, photo=open(photo, 'rb'))
            if os.path.exists(photo):
                os.remove(photo)
    except Exception as e:
        logging.exception(e)


def send_button_telepot(msg, botoes):
    try:
        bts = [[InlineKeyboardButton(text=i["texto_botao"], callback_data=i["callback"])] for i in botoes]
        keyboard = InlineKeyboardMarkup(inline_keyboard=bts)
        bot.sendMessage(REQUESTER_ID, msg, reply_markup=keyboard, parse_mode='Markdown')
    except Exception as e:
        logging.exception(e)


def main():
    MessageLoop(bot, handle).run_as_thread()
    while 1:
        time.sleep(10)


if __name__ == '__main__':
    main()