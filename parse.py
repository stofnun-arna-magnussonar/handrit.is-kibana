import os
from bs4 import BeautifulSoup
import json
import glob
import datetime

directory = 'Manuscripts'

def getMsItemData(msItem):
	msItemData = {}
	if len(msItem.findChildren('title', recursive=False)) > 0:
		msItemTitle = msItem.findChildren('title', recursive=False)[0].get_text()
	elif len(msItem.findChildren('incipit', recursive=False)) > 0:
		msItemTitle = msItem.findChildren('incipit', recursive=False)[0].get_text()
	elif len(msItem.findChildren('rubric', recursive=False)) > 0:
		msItemTitle = msItem.findChildren('rubric', recursive=False)[0].get_text()
	elif len(msItem.findChildren('note', recursive=False)) > 0:
		msItemTitle = msItem.findChildren('note', recursive=False)[0].get_text()
	else:
		msItemTitle = None

	msItemText = []
	if len(msItem.findChildren('title', recursive=False)) > 0:
		msItemText.append(msItem.findChildren('title', recursive=False)[0].get_text())
	elif len(msItem.findChildren('incipit', recursive=False)) > 0:
		msItemText.append(msItem.findChildren('incipit', recursive=False)[0].get_text())
	elif len(msItem.findChildren('rubric', recursive=False)) > 0:
		msItemText.append(msItem.findChildren('rubric', recursive=False)[0].get_text())
	elif len(msItem.findChildren('note', recursive=False)) > 0:
		msItemText.append(msItem.findChildren('note', recursive=False)[0].get_text())

	if msItem.findChildren('textLang', recursive=False):
		msItemData['lang'] = msItem.findChildren('textLang', recursive=False)[0].get('mainLang')

	if msItemTitle is not None:
		msItemData['title'] = ' '.join(msItemTitle.split())

	msItemData['text'] = ' '.join((' '.join(msItemText)).split())

	if len(msItem.findChildren('locus', recursive=False)) > 0:
		msItemData['pageFrom'] = msItem.findChildren('locus', recursive=False)[0].get('from')
		msItemData['pageTo'] = msItem.findChildren('locus', recursive=False)[0].get('to')
	
	if len(msItem.findChildren('author', recursive=False)) > 0:
		if msItem.findChildren('author', recursive=False)[0].find('name'):
			authorEl = msItem.findChildren('author', recursive=False)[0].find('name')
		else:
			authorEl = msItem.findChildren('author', recursive=False)[0]

		msItemData['author'] = {
			'id': authorEl.get('key'),
			'name': authorEl.get_text()+(' ('+authorEl.get('key')+')' if authorEl.get('key') is not None else '')
		}
	
	if len([c for c in msItem.findChildren('name') if c.get('type') == 'person' and c.get('key') is not None]) > 0:
		msItemData['relPersons'] = list(map(lambda p: getPersonData(p.get('key')), [c for c in msItem.findChildren('name') if c.get('type') == 'person' and c.get('key') is not None]))

	if msItem.get('class') is not None:
		msItemData['keywords'] = msItem.get('class').split()

	return msItemData

manuscripts = []

placesXml = BeautifulSoup(open('Manuscripts/Authority Files/places.xml'), features='xml')
personsXml = BeautifulSoup(open('Manuscripts/Authority Files/names.xml'), features='xml')

placesDict = {}
personsDict = {}

for placeEl in placesXml.find_all('place'):
	placeObj = {
		'id': placeEl.get('xml:id')
	}

	if placeEl.find('settlement') is not None:
		placeObj['name'] = placeEl.find('settlement').get_text()

	if len(placeEl.findChildren('geo')) > 0:
		geo = placeEl.findChildren('geo')[0].get_text().split(' ')

		if len(geo) == 2:
			placeObj['location'] = {
				'lat': geo[0],
				'lon': geo[1]
			}

	placesDict[placeObj['id']] = placeObj

for personEl in personsXml.find_all('person'):
	personObj = {
		'id': personEl.get('xml:id'),
		'name': ' '.join(personEl.find('persName').get_text().split())+' ('+personEl.get('xml:id')+')'
	}

	personsDict[personObj['id']] = personObj

def getPlaceData(key):
	return placesDict[key] if key in placesDict else None

def getPersonData(key):
	return personsDict[key] if key in personsDict else None

files = glob.glob(directory+'/**/*.xml', recursive=True)

count = 0
for file in files:
	count += 1

	filename = os.fsdecode(file)
	if filename.endswith('.xml'):# and filename == 'GKS04-2365-is.xml':
		fileContent = open(filename)
		s = BeautifulSoup(fileContent, features='xml')

		#fileModified = os.path.getmtime(filename)
		fileModified = str(datetime.datetime.fromtimestamp((os.path.getmtime(filename))))

		msData = {
			'modified': fileModified
		}

		msDateCert = ''
		
		msDescEl = s.find('msDesc');

		if msDescEl is not None:
			msData['url'] = 'https://handrit.is/manuscript/view/'+msDescEl.get('xml:lang')+'/'+'-'.join(msDescEl.get('xml:id').split('-')[:-1])
			if msDescEl.find('physDesc') is not None:
				physDescEl = msDescEl.find('physDesc')

				if physDescEl.find('handDesc') is not None and physDescEl.find('handDesc').find('handNote') is not None:
					try:
						msData['scribe'] = getPersonData([n for n in physDescEl.find('handDesc').find_all('handNote') if n.get('scribe') is not None][0].get('scribe'))
					except:
						pass

				if physDescEl.find('supportDesc') is not None and physDescEl.find('supportDesc').get('material') is not None:
					msData['material'] = physDescEl.find('supportDesc').get('material')
				
				msData['physDesc'] = ' '.join(msDescEl.find('physDesc').get_text().split())

			if msDescEl.find('country'):
				msData['country'] = msDescEl.find('country').get_text();

			if msDescEl.find('institution') is not None:
				msData['institution'] = msDescEl.find('institution').get('key');

			if msDescEl.find('collection'):
				msData['collection'] = msDescEl.find('collection').get('key');

			if msDescEl.find('msIdentifier').find('idno'):
				msId = s.find('msDesc').find('msIdentifier').find('idno').get_text()

				msData['msId'] = msId
			else:
				#print(msDescEl.find('msIdentifier'))
				break

			if msDescEl.find('msIdentifier').find('msName'):
				msName = msDescEl.find('msIdentifier').find('msName').get_text()
				msData['name'] = msName

			if msDescEl.find('history') and msDescEl.find('history').find('provenance'):
				if not 'history' in msData:
					msData['history'] = {}
				msData['history']['persons'] = list(map(lambda p: getPersonData(p.get('key')), [c for c in msDescEl.find('history').find('provenance').findChildren('name') if c.get('type') == 'person' and c.get('key') is not None]))

			if msDescEl.find('history') and msDescEl.find('history').find('provenance'):
				if not 'history' in msData:
					msData['history'] = {}
				places = list(map(lambda p: p.get('key'), [c for c in msDescEl.find('history').find('provenance').findChildren('name') if c.get('type') == 'place' and c.get('key') is not None]))

				msData['history']['places'] = list(map(lambda p: getPlaceData(p), places))


			if msDescEl.find('history') and msDescEl.find('history').find('origin'):
				origDateEl = msDescEl.find('history').find('origin').find('origDate')

				if origDateEl is not None:
					msDateFrom = None
					msDateTo = None

					if origDateEl.get('from'):
						msDateFrom = origDateEl.get('from')
					if origDateEl.get('to'):
						msDateTo = origDateEl.get('to')

					if origDateEl.get('notBefore'):
						msDateFrom = origDateEl.get('notBefore')
					if origDateEl.get('notAfter'):
						msDateTo = origDateEl.get('notAfter')

					if origDateEl.get('when'):
						msDateFrom = origDateEl.get('when')
						msDateTo = origDateEl.get('when')
					
					if msDateFrom is not None:
						msData['dateFrom'] = msDateFrom
					if msDateTo is not None:
						msData['dateTo'] = msDateTo

					if origDateEl.get('cert'):
						msDateCert = origDateEl.get('cert')
						msData['dateCert'] = msDateCert

			if msDescEl.find('history'):
				if not 'history' in msData:
					msData['history'] = {}
				msData['history']['text'] = ' '.join(msDescEl.find('history').get_text().split())
			
			if msDescEl.find('history') and msDescEl.find('history').find('acquisition'):
				if msDescEl.find('history').find('acquisition').get('when'):
					msData['acquisition'] = msDescEl.find('history').find('acquisition').get('when')

			if msDescEl.find('msContents') is not None:
				for msItem in msDescEl.find('msContents').findChildren('msItem', recursive=False):
					msItemData = getMsItemData(msItem)

					if not 'items' in msData:
						msData['items'] = []

					if msItem.find_all('msItem') is not None:
						for msSubItem in msItem.find_all('msItem'):
							msSubItemData = getMsItemData(msSubItem)

							#if not 'items' in msItemData:
							#	msItemData['items'] = []
							
							msData['items'].append(msSubItemData)

					#if not 'items' in msData:
					#	msData['items'] = []
					
					msData['items'].append(msItemData)
			
			if s.find('facsimile') and len(s.find('facsimile').findChildren('graphic')) > 0:
				msData['images'] = True

			manuscripts.append(msData)

			#print(json.dumps(msData, indent=4, ensure_ascii=False))
		else:
			pass
			#print(s)

print(json.dumps(manuscripts, indent=4, ensure_ascii=False))
