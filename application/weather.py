import urllib.request
import json

def weather2text():
	text = '\n'
	url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=130010'
	html = urllib.request.urlopen(url)
	resp = json.loads(html.read().decode('utf-8'))

	text += '**************************' + '\n'
	text += resp['title'] + '\n'
	text += '**************************' + '\n'
	text += resp['description']['text'] + '\n'

	for forecast in resp['forecasts']:
		text += '**************************' + '\n'
		text += forecast['dateLabel'] + '(' + forecast['date'] + ')' + '\n'
		text += forecast['telop'] + '\n'

	text += '**************************' + '\n'

	return text