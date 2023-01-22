import requests, json
from regex import *
from utils import *
from watchPlayer import *

class HDRezka:
	def __init__(self, url='https://hdrezka.ag', user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/100.0'):
		self.url = url
		self.session = requests.Session()
		self.session.headers.update({
			'User-Agent': user_agent
		})

	def getPage(self, page=None, category=None, genre=None, filter=None):
		url = self.url

		if category:
			url += f'/{category}'

		if genre:
			url += f'/{genre}'

		if page:
			url += f'/page/{page}'

		if filter:
			url += f'/?filter={filter}'

		parse = parsePageData(self.session.get(url).content.decode())
		parse['page'] = int(page)

		return parse

	def watch(self, id):
		req = self.session.get(f'{self.url}/index.php?newsid={id}')
		if req.status_code == 404:
			return { 'status': False, 'message': '[dark_red]Film not found' }
		watch = parseWatchData(req.content.decode(), self)
		return watch

	def search(self, query, page=1):
		response = self.session.get(f'https://rezka.ag/search/?do=search&subaction=search&q={query}&page={page}')
		search = parsePageData(response.content.decode())
		return search

	def getCDN(self, id, translator, favs, action, season=None, series=None):
		if season and series:
			data = f'id={id}&translator_id={translator}&season={season}&episode={series}&favs={favs}&action={action}'
		else:
			data = f'id={id}&translator_id={translator}&is_camrip=0&is_ads=0&is_director=0&favs={favs}&action={action}'

		response = requests.post(f'https://rezka.ag/ajax/get_cdn_series/?t={str(getTime())[:-3]}', data=data, headers={
			'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'	
		}).json()

		data = {}

		if 'url' in response and response['url']:
			data = {
				'urls': clearTrash(response['url']),
				'quality': response['quality'],
				'subtitle': {
					'urls': response['subtitle'],
					'lns': response['subtitle_lns'],
					'def': response['subtitle_def']
				},
			}

		player = None

		if action == 'get_episodes':
			player = watchPlayer('', True)
			data['seasons'] = player.seasons(response['seasons'])
			data['series'] = player.series(response['episodes'])

		return data