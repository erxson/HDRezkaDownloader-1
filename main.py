from HDRezka import *
from utils import *

from rich.console import Console
from rich.traceback import install

from pathlib import Path
from tqdm import tqdm

import json, os, urllib3, re, sys, requests

install()
console = Console(record=True)

def download(url: str, fname: str, desc: str):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(desc=desc, total=total, unit='iB', unit_scale=True, unit_divisor=1024) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

class Downloader:
	def __init__(self):
		super(Downloader, self).__init__()
		self.hdrezka = HDRezka(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0')

	def inputTranslation(self, translations):
		try:
			console.print('[green]Выберете перевод:')

			for key, translation in enumerate(translations):
				title = translation['title']
				console.print(f'[cyan]{key}. {title}')

			return translations[int(console.input('[yellow]Перевод: '))]['id']
		except KeyboardInterrupt:
			console.print()
			sys.exit(0)
		except:
			clear()
			console.print('[red]Перевод не найден');
			return self.inputTranslation(translations)

	def inputSeasons(self, seasons):
		try:
			console.print(f'[green]Всего сезонов: {len(seasons)}')
			console.print('[green]Введите сезоны\nПример 1: 5 1 2 3\nПример 2: 1-5')
			answer = console.input('[yellow]Сезоны: ')
			res = list(set(answer.split(' ')))
			seas = []

			for x in res:
				split = x.split('-')
				if len(split) < 2:
					break
				for y in range(int(split[0]), int(split[1]) + 1):
					seas.append(str(y))

			seas = list(set(seas))
			return seas if len(seas) > 1 else res
		except KeyboardInterrupt:
			console.print()
			sys.exit(0)
		except Exception as e:
			clear()
			console.print('[red]Ошибка')
			return self.inputSeasons(seasons)

	# def inputSeries(self, series):
		# try:
			
		# except:
		# 	console.print()
		# 	sys.exit(0)
		# except Exception as e:
		# 	clear()
		# 	console.print('[red]Ошибка')
		# 	return self.inputSeries(series)
	
	def inputQuality(self, data):
		try:
			try: 
				global permQuality
				permQuality
			except NameError: 
				console.print('[green]Выберете качество:')

				for key, quality in enumerate(data):
					title = quality[0]
					console.print(f'[cyan]{key}. {title}')
				permQuality = int(console.input('[yellow]Качество: '))

			return data[permQuality]
		except KeyboardInterrupt:
			console.print()
			sys.exit(0)
		except IndexError:
			clear()
			console.print('[red]Качество не найдено');
			return self.inputQuality(data)
	def download(self, name, id, translation, favs, type, season, serie):
		try:
			cdn = self.hdrezka.getCDN(id, translation, favs, type, season, serie)
			quality = self.inputQuality(re.findall(r'\[(.*?)\].*? or (.*?.mp4)', cdn['urls']))

			console.print('[green]Начинаю скачивание')
			if os.path.exists(f"{self.folder}/{season}/{serie}.mp4"):
				clear()
				console.print(f'[yellow][{season}] Уже скачен {serie} пропуск')
				return
			download(quality[1], f"{self.folder}/{season}/{serie}.mp4", f'{name} Сезон {season} серия {serie}')
			clear()
		except Exception as e:
			print('Error', e)
			self.download(name, id, translation, favs, type, season, serie)

	def start(self, id):
		watch = self.hdrezka.watch(id)

		if 'status' in watch and not watch['status']:
			console.print(watch['message'])

		if 'translations' in watch['player']:
			translation = self.inputTranslation(watch['player']['translations'])
			clear()
		else:
			translation = watch['player']['default']['translation']

		name = watch['name'].replace(':', '').replace('\\', '').replace('/', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '-')
		folder = './downloads'
		Path(folder).mkdir(parents=True, exist_ok=True)

		if 'seasons' in watch['player']:
			folder = f"{folder}/{name}"
			Path(folder).mkdir(parents=True, exist_ok=True)
			seasons = self.inputSeasons(watch['player']['seasons'])
			clear()

			for season in seasons:
				Path(f'{folder}/{season}').mkdir(parents=True, exist_ok=True)
				self.folder = folder

				for serie in watch['player']['series'][season]:
					console.print(f'[yellow]Сезон {season} серия {serie}')
					self.download(name, id, translation, watch['favs'], watch['player']['default']['type'], season, serie)
		else:
			for x in range(0, 3):
				try:
					if os.path.exists(f"{folder}/{name}.mp4"):
						clear()
						console.print(f'[yellow]{name} Уже скачен пропуск')
						return
					cdn = self.hdrezka.getCDN(id, translation, watch['favs'], watch['player']['default']['type'])
					quality = self.inputQuality(re.findall(r'\[(.*?)\].*? or (.*?.mp4)', cdn['urls']))
					console.print('[green]Начинаю скачивание')
					download(quality[1], f"{folder}/{name}.mp4", name)
					break
				except Exception as e:
					console.print(f'[yellow]Ошибка при скачивании x{x}\nПовтор')

		console.print('[green]Скачивание завершено')

def main():
	try:
		downloader = Downloader()

		id = console.input('[yellow]Введите ID/LINK: ')
		
		if 'http' in id:
			try:
				id = re.search(r'([0-9]*)-.*?.html', id).group(1)
			except:
				clear()
				console.print('[red]Не удалось спарсить ID')
				return main()
						
		try:
			id = int(id)
		except:
			clear()
			console.print('[red]ID Должен быть числом')
			return main()

		clear()
		
		downloader.start(id)
	except KeyboardInterrupt:
		console.print()
		sys.exit(0)

if __name__ == '__main__':
	main()
	os.system('pause')
