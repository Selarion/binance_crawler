import os
import time
import json
import tornado

from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from functools import partial


SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'NEOUSDT', 'LTCUSDT', 'BNBUSDT']


@gen.coroutine
def main_loop():
    http_client = AsyncHTTPClient()
    depth_url_mask = "https://www.binance.com/api/v1/depth?symbol={}&limit=5"

    while True:
        for sym in SYMBOLS:
            http_client.fetch(
                depth_url_mask.format(sym),
                partial(handle_response, sym)
            )
        yield gen.sleep(1)
        print('----')


def handle_response(sym, response):
    if response.error:
        subline = "error: {}".format(response.error)
    else:
        # Парсим полученный ответ
        dict_response = json.loads(response.body.decode("utf-8"))
        max_buy_price = dict_response['bids'][-1][0]
        min_sell_price = dict_response['asks'][1][0]
        price_substr ='{}/{}'.format(max_buy_price, min_sell_price)

        subline = 'buy_price/sell_price = {} || depth: {}'.format(price_substr, response.body)

    # Формируем новую строку на запись
    new_line = 'timestamp - {} || {}\n'
    timestamp = round(time.time())
    new_line = new_line.format(timestamp, subline)

    # Создаем файл или дозаписываем строку в уже существующий
    file_name = os.path.join(os.getcwd(), 'logs', '{}.txt'.format(sym))
    append_write = 'a' if os.path.exists(file_name) else 'w'
    with open(file_name, append_write) as f:
        f.write(new_line)

    # Рисуем в консоль, чтобы не скучно было.
    print(response)


if __name__ == '__main__':
    # Проверяем существование директории с логами
    if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
        os.mkdir(os.path.join(os.getcwd(), 'logs'))

    current_ioloop = tornado.ioloop.IOLoop.current()
    current_ioloop.spawn_callback(main_loop)
    tornado.ioloop.IOLoop.instance().start()
