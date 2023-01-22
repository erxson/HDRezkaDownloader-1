import re

class watchInfo:
	def __init__(self, data):
		super(watchInfo, self).__init__()
		self.info = {}
		self.data = data
		self.infoParser = {
			'Рейтинги': { 'callback': self.rating, 'name': 'Рейтинги' },
			'Входит в списки': { 'callback': self.includeList, 'name': 'Входит в списки' },
			'Дата выхода': { 'callback': self.releaseDate, 'name': 'Дата выхода' },
			'Страна': { 'callback': self.country, 'name': 'Страна' },
			'Режиссер': { 'callback': self.producer, 'name': 'Режиссер' },
			'Жанр': { 'callback': self.genre, 'name': 'Жанр' },
			'В качестве': { 'callback': self.quality, 'name': 'В качестве' },
			'В переводе': { 'callback': self.translations, 'name': 'В переводе' },
			'Возраст': { 'callback': self.age, 'name': 'Возраст' },
			'Время': { 'callback': self.time, 'name': 'Время' },
			'Из серии': { 'callback': self.aseries, 'name': 'Из серии' },
			'В ролях актеры': { 'callback': self.cast, 'name': 'В ролях актеры' },
			'Слоган': { 'callback': self.slogan, 'name': 'Слоган' },
			'Год:': { 'callback': self.year, 'name': 'Год' }
		}
		self.parse()

	def year(self, data):
		years = re.findall(r'<a href=\".*?\">(.*?)</a>', data)
		return ' - '.join(years)

	def rating(self, data):
		response = {}
		rating = re.findall(r'<span class=\"b-post__info_rates.*?\">.*?rel=\"nofollow\">(.*?)<.*?bold\">(.*?)<.*?i>\((.*?)\)',
			re.search(r'<h2>(.*?)<\/h2>.*<td>(.*?)<\/td>', data).group(2))
		for x in rating:
			response[x[0]] = {
				'rating': float(x[1]),
				'votes': int(x[2].replace(' ', ''))
			}
		return response

	def includeList(self, data):
		response = []
		list = re.findall(r'<a href=\"(.*?)\">(.*?)<\/a> \((.*?)\)',
			re.search(r'<h2>(.*?)<\/h2>.*<td class=\"rd\">(.*?)<\/td>', data).group(2))
		for include in list:
			response.append({
				# 'href': urlparse(include[0]).path,
				'title': include[1],
				'place': include[2]
			})

		return response

	def releaseDate(self, data):
		release = re.search(r'<h2>(.*?)<\/h2>.*?<td>(.*?) <.*?>(.*?)<', data)
		return {
			'day': release.group(2),
			'year': release.group(3)
		}

	def country(self, data):
		response = []
		contries = re.findall(r'<a href=\".*?\">(.*?)<\/a>',
			re.search(r'<h2>(.*?)<\/h2>.*?<td>(.*?)<\/td>', data).group(2))
		for country in contries:
			response.append(country)
		return response

	def producer(self, data):
		response = []
		producers = re.findall(r'<a href=\"(.*?)\".*?>.*?itemprop=\"name\">(.*?)<\/span><\/a>',
			re.search(r'<h2>(.*?)<\/h2>.*?<div class=\"persons-list-holder\">(.*?)<\/div>', data).group(2))
		for producer in producers:
			response.append(producer[1])
		return response

	def genre(self, data):
		response = []
		genres = re.findall(r'<a href=\"(.*?)\".*?>.*?itemprop=\"genre\">(.*?)<\/span><\/a>',
			re.search(r'<h2>(.*?)<\/h2>.*<td>(.*?)<\/td>', data).group(2))
		for genre in genres:
			response.append(genre[1])
		return response

	def quality(self, data):
		quality = re.search(r'<h2>(.*?)<\/h2>.*<td>(.*?)<\/td>', data)
		return quality.group(2)

	def translations(self, data):
		translations = re.search(r'<h2>(.*?)<\/h2>.*<td>(.*?)<\/td>', data)
		return translations.group(2).split(', ')

	def age(self, data):
		age = re.search(r'<span.*?>(.*?)<\/span> (.*)',
			re.search(r'<h2>(.*?)<\/h2>.*<td>(.*?)<\/td>', data).group(2))
		return {
			'limit': age.group(1),
			'desc': age.group(2)
		}

	def time(self, data):
		return re.search(r'<h2>(.*?)<\/h2>.*?<td itemprop=\"duration\">(.*?)<\/td>', data).group(2)

	def aseries(self, data):
		response = []
		aseries = re.findall(r'<a href=\"(.*?)\">(.*?)</a>',
			re.search(r'<h2>(.*?)<\/h2>.*?<td>(.*?)</td>', data).group(2))
		for aserie in aseries:
			response.append(aserie[1])
		return response

	def cast(self, data):
		response = []
		actors = re.findall(r'<a href=\"(.*?)\".*?><span itemprop=\"name\">(.*?)</span></a>',
			re.search(r'<h2>(.*?)</h2>.*?</span>(.*?)</td>', data).group(2))
		for actor in actors:
			response.append(actor[1])
		return response

	def slogan(self, data):
		return re.search(r'<h2>(.*?)<\/h2>.*?<td>(.*?)<\/td>', data).group(2)

	def parse(self):
		tr = re.findall(r'<tr>(.*?)<\/tr>', self.data)
		for line in tr:
			name = re.search(r'<h2>(.*?)<\/h2>', line)
			td = re.search(r'<td.*?>(.*?)<\/td>', line).group(1)
			if name:
				name = name.group(1)
			else:
				name = td
			if name in self.infoParser:
				self.info[self.infoParser[name]['name']] = self.infoParser[name]['callback'](line)

	def get(self):
		return self.info