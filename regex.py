import re, json

from urllib.parse import urlparse
from watchInfo import *
from watchPlayer import *
from utils import *

def parseLastPage(data):
	navigation = re.search(r'\"b-navigation\">(.*?)</div>', data)
	if navigation:
		items = re.findall(r'(?:<a.*?href=\".*?\".*?>(\d+)</a>|<span>(\d+)</span>)', navigation.group(1))
		return int(max([int(x[0] or x[1]) for x in items]))
	return 0

def parsePageItemInfo(data):
	info = re.search(r'\"entity\">(?P<category>.*?)<.*?href=\".*?\">(?P<title>.*?)</a>.*?<div.*?>(?P<data>.*?)</div>', data).groupdict()
	data = info['data'].split(',')

	country = None if len(data) < 3 else data[1].strip()
	genre = data[1].strip() if len(data) < 3 else data[2].strip()

	return {
		'title': info['title'],
		'category': info['category'],
		'year': data[0],
		'country': country,
		'genre': genre
	}

def parsePageData(data):
	response = []

	pattern = re.compile(r'\"b-content__inline_item\".*?\"(?P<id>.*?)\".*?src=\"(?P<poster>.*?)\".*?class=\"cat (?P<category>.*?)\">(?P<info>.*?)</div></div>')
	items = re.search(r'<div class=\"b-content__inline_items\">(.*?)<div id=\".*?\">', data)
	for item in [m.groupdict() for m in pattern.finditer(items.group(1))]:
		info = parsePageItemInfo(item['info'])
		response.append({
			'id': item['id'],
			'poster': item['poster'],
			'category': item['category'],
			'info': info
		})

	return {
		'last_page': parseLastPage(data),
		'count': len(response),
		'data': response
	}

def parseWatchData(data, HDRezka):
	response = {
		'name': re.search(r'<h1 itemprop=\"name\">(.*?)</h1>', data).group(1),
		'original_name': None,
		'poster': re.search(r'<img itemprop=\"image\" src=\"(.*?)\".*?>', data).group(1),
		'about': {
			'title': re.search(r'<div class=\"b-post__description_title\"><h2>(.*?)</h2>:</div>', data).group(1),
			'content': re.search(r'<div class=\"b-post__description_text\"> (.*?)</div>', data).group(1)
		},
		'favs': re.search(r'<input type=\"hidden\" id=\"ctrl_favs\" value=\"(.*?)\" \/>', data).group(1),
		'info': watchInfo(re.search(r'<table class=\"b-post__info\">(.*?)</table>', data).group(1)).get(),
		'player': watchPlayer(data).get()
	}

	orig_name = re.search(r'<div class=\"b-post__origtitle\" itemprop=\"alternativeHeadline\">(.*?)</div>', data)
	if orig_name:
		response['original_name'] = orig_name.group(1)

	default = re.search(r'sof.tv.(?P<type>.*?)\((?P<id>.*?), (?P<translation>.*?),', data).groupdict()
	default['type'] = 'get_stream' if default['type'] == 'initCDNSeriesEvents' else 'get_movie'
	if 'series' in response['player']:
		default['cdn'] = HDRezka.getCDN(default['id'], default['translation'], response['favs'], default['type'], list(response['player']['series'])[0], 1)
	else:
		default['cdn'] = HDRezka.getCDN(default['id'], default['translation'], response['favs'], default['type'])
	if default:
		response['player']['default'] = default

	return response

def parseCDNurl(data):
	response = {}
	split = data.split(',')
	for quality in split:
		s = re.search(r'\[(?P<quality>.*?)\](?P<link1>.*?) or (?P<link2>.*)', quality)
		response[s['quality']] = {
			'link1': s['link1'],
			'link2': s['link2']
		}
	return response

def parseSearchData(data):
	response = {}
	return data