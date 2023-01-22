import re

class watchPlayer:
	def __init__(self, data, f=False):
		super(watchPlayer, self).__init__()
		self.player = {}
		self.data = data
		if not f:
			self.parse()

	def translations(self, data):
		response = []
		translations = re.findall(r'<li (.*?)</li>', data)
		for translation in translations:
			res = re.search(r'title=\"(?P<title>.*?)\".*?data-translator_id=\"(?P<id>.*?)\"', translation).groupdict()
			response.append({
				'id': res['id'],
				'title': res['title']				
			})
		return response

	def seasons(self, data):
		response = []
		seasons = re.findall(r'<li(.*?)</li>', data)
		for season in seasons:
			season = re.search(r'.*?data-tab_id=\"(?P<id>.*?)\">(?P<title>.*)', season).groupdict()
			response.append({
				'id': season['id'],
				'title': season['title']	
			})
		return response

	def series(self, data):
		response = {}
		series = re.findall(r'<li(.*?)</li>', data)
		for serie in series:
			serie = re.search(r'data-season_id=\"(?P<season>.*?)\".*?data-episode_id=\"(?P<episode>.*?)\".*?>(?P<title>.*)', serie)
			if serie['season'] not in response:
				response[serie['season']] = {}
			if serie['episode'] not in response[serie['season']]:
				response[serie['season']][serie['episode']] = serie['title']
		return response

	def parse(self):
		translations = re.search(r'<ul id=\"translators-list\".*?>(.*?)</ul>', self.data)
		if translations:
			self.player['translations'] = self.translations(translations.group(1))

		seasons = re.search(r'<ul.*?id=\"simple-seasons-tabs\".*?>(.*?)</ul>', self.data)
		if seasons:
			self.player['seasons'] = self.seasons(seasons.group(1))

		series = re.search(r'<div id=\"simple-episodes-tabs\">(.*?)</ul></div>', self.data)
		if series:
			self.player['series'] = self.series(series.group(1))

	def get(self):
		return self.player