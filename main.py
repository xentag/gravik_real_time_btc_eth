import websockets
import asyncio
import json
import time
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# Взял бы среднее квадратическое отклонение btc и eth вычел бы их потом, понял бы реальное изменение цены без кореляции btc
# Или взял бы индикатор ATR биткойна вычел бы оттуда atr eth и так бы учитывал изменение цены 
# Решил воспользоваться через вебсокет потому, что он не закрывает соединение если делать допустим тоже самое через реквест
# данные будут более поздними. Сами котировки брал с api бинанс
# График не обновляетя через pycharm только через vs code
# Сделал выбор котировок по желаю с бинанс


xdata_btc = []
ydata_btc = []
xdata = []
ydata = []
fig, ax = plt.subplots()
plt.xticks(rotation=45)
kotirovka = "ethusdt"  # Можно выбрать любой тикер какой есть на бинансе


def update_graph():
    ax.plot(xdata, ydata, color='g')
    ax.legend([f"Last price: {ydata[-1]}$"])
    fig.canvas.draw()
    plt.pause(0.1)


async def main(kotirovka, current_time):
    url = f"wss://stream.binance.com:9443/stream?streams={kotirovka}@miniTicker"
    url_btc = f"wss://stream.binance.com:9443/stream?streams=btcusdt@miniTicker"
    async with websockets.connect(url) as client:
        async with websockets.connect(url_btc) as client_btc:
            while True:
                data_btc = json.loads(await client_btc.recv())['data']
                event_time_btc = time.localtime(data_btc['E'] // 1000)
                event_time_btc = f"{event_time_btc.tm_hour}:{event_time_btc.tm_min}:{event_time_btc.tm_sec}"
                print(event_time_btc, data_btc['c'])
                xdata_btc.append(event_time_btc)
                ydata_btc.append((int(float(data_btc['c']))))
                print(np.std(ydata_btc))

                data = json.loads(await client.recv())['data']
                event_time = time.localtime(data['E'] // 1000)
                event_time = f"{event_time.tm_hour}:{event_time.tm_min}:{event_time.tm_sec}"
                print(event_time, data['c'])
                xdata.append(event_time)
                ydata.append(int((float(data['c']))))
                print(np.std(ydata))
                std = np.std(ydata_btc) - np.std(ydata)
                if ((int(float(ydata[0]))) + int(std)) >= int((float(ydata[-1]))) or int(
                        (float(ydata[0])) - int(std)) <= int((float(ydata[-1]))):
                    if datetime.now() >= current_time:
                        print('Условие сработало')  # Можно сделать отпрвку в телеграм допустим через фреймворк telethon
                update_graph()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(kotirovka=kotirovka, current_time=datetime.now() + timedelta(minutes=60)))
