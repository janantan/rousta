from pymongo import MongoClient
import utils

cursor = utils.config_mongodb()

def ostan():
	ostan_result = cursor.ostan.find()
	for state in ostan_result:
		record = {'code': state['id'], 'name': state['name']}
		cursor.states.insert_one(record)

def shahrestan():
	for s in cursor.states.find():
		shahrestan = []
		for sh in cursor.shahrestan.find():
			if sh['ostan'] == s['code']:
				shahrestan.append(
					{
					'name': sh['name'],
					'code': sh['id']
					})
		cursor.states.update_many(
            {'code': s['code']},
            {'$set':{
            'shahrestan': shahrestan
            }}
            )

def bakhsh():
	for s in cursor.states.find():
		shahrestan = []
		for sh in s['shahrestan']:
			sh_dict = {
			'name': sh['name'],
			'code': sh['code']
			}
			bakhsh = []
			for b in cursor.bakhsh.find():
				if b['ostan'] == s['code']:					
					if b['shahrestan'] == sh['code']:
						bakhsh.append(
							{
							'name': b['name'],
							'code': b['id']
							})
			sh_dict['bakhsh'] = bakhsh
			shahrestan.append(sh_dict)
		cursor.states.update_many(
	        {'code': s['code']},
	        {'$set':{
	        'shahrestan': shahrestan
	        }}
	        )

def ostan_mod():
	for ostan in cursor.ostan.find():
		rec = {'id': ostan['id'], 'name': ostan['name'],
		'amar_code': ostan['amar_code']}
		cursor.Ostan.insert_one(rec)

def shahrestan_mod():
	for shahrestan in cursor.shahrestan.find():
		r = cursor.ostan.find_one({'id':shahrestan['ostan']})
		if r:
			rec = {'id': shahrestan['id'], 'name': shahrestan['name'],
			'amar_code': shahrestan['amar_code'],
			'ostan':{'id':r['id'], 'name':r['name']}}
			cursor.Shahrestan.insert_one(rec)

def bakhsh_mod():
	for bakhsh in cursor.bakhsh.find():
		r = cursor.Shahrestan.find_one({'id':bakhsh['shahrestan']})
		if r:
			rec = {'id': bakhsh['id'], 'name': bakhsh['name'],
			'amar_code': bakhsh['amar_code'],
			'ostan': r['ostan'],
			'shahrestan': {'id': r['id'], 'name': r['name']}}
			cursor.Bakhsh.insert_one(rec)

def shahr_mod():
	for shahr in cursor.shahr.find():
		r = cursor.Bakhsh.find_one({'id':shahr['bakhsh']})
		if r:
			rec = {'id': shahr['id'], 'name': shahr['name'],
			'amar_code': shahr['amar_code'],
			'shahr_type': shahr['shahr_type'],
			'ostan': r['ostan'],
			'shahrestan': r['shahrestan'],
			'bakhsh': {'id': r['id'], 'name': r['name']}}
			cursor.Shahr.insert_one(rec)

def dehestan_mod():
	for dehestan in cursor.dehestan.find():
		r = cursor.Bakhsh.find_one({'id':dehestan['bakhsh']})
		if r:
			rec = {'id': dehestan['id'], 'name': dehestan['name'],
			'amar_code': dehestan['amar_code'],
			'ostan': r['ostan'],
			'shahrestan': r['shahrestan'],
			'bakhsh': {'id': r['id'], 'name': r['name']}}
			cursor.Dehestan.insert_one(rec)

def abadi_mod():
	for abadi in cursor.abadi.find():
		if 'bakhsh' in abadi.keys():
			r = cursor.Dehestan.find_one({'id':abadi['dehestan']})
			if r:
				rec = {'id': abadi['id'], 'name': abadi['name'],
				'amar_code': abadi['amar_code'],
				'abadi_type': abadi['abadi_type'],
				'diag': abadi['diag'],
				'ostan': r['ostan'],
				'shahrestan': r['shahrestan'],
				'bakhsh': r['bakhsh'],
				'dehestan': {'id': r['id'], 'name': r['name']}}
				cursor.Abadi.insert_one(rec)

#ostan_mod()
#shahrestan_mod()
#bakhsh_mod()
#shahr_mod()
#dehestan_mod()
#abadi_mod()