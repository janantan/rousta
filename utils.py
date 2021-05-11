from ippanel import Client, Error, HTTPError, ResponseCode
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from rousta import app, db
import datetime
import jdatetime
import random2
import base64
import uuid
import copy
import os
import config, models

#Config MongoDB
def config_mongodb():
	#mongodb://mongodb_user:password@localhost:27017/mongodb_db
	uri = "mongodb://{}:{}@{}:{}/{}".format(
		config.MONGODB_USERNAME,
		config.MONGODB_PASSWORD,
		config.MONGODB_HOST,
		config.MONGODB_PORT,
		config.DB_NAME
	)
	cur = MongoClient(uri)[config.DB_NAME]
	return cur

def send_sms(phoneNumber, code):
	client = Client(config.IPPANEL_API_KEY)

	pattern_values = {"code": code}
	try:
		bulk_id = client.send_pattern(
			config.SMS_PATTERN_CODE,	# pattern code
			config.SMS_ORIGINATOR,	  # originator
			phoneNumber,  # recipient
			pattern_values,  # pattern values
		)
		return(bulk_id)
	except Error as e:
		print("Error handled => code: %s, message: %s" % (e.code, e.message))
		if e.code == ResponseCode.ErrUnprocessableEntity.value:
			for field in e.message:
				print("Field: %s , Errors: %s" % (field, e.message[field]))
	except HTTPError as e:
		print("Error handled => code: %s" % (e))
	return (None)

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def save_image_from_form(image, owner, Id):
	filename = secure_filename(image.filename)
	if allowed_file(filename):
		directory = os.path.join(config.IMAGE_FILE_FOLDER, owner, Id)
		if not os.path.exists(directory):
			os.makedirs(directory)
		file_type  = filename.rsplit('.', 1)[1].lower()
		img_name = str(random2.randint(10000, 99999))+'.'+file_type
		img_directory = os.path.join(directory, img_name)
		img_path = os.path.join(config.IMAGE_URL_PATH, owner, Id, img_name)
		image.save(img_directory)
		return img_path
	else:
		return False

def save_encoded_image(image, owner, Id):
	try:
		file_type = 'png'
		directory = os.path.join(config.IMAGE_FILE_FOLDER, owner, Id)
		if not os.path.exists(directory):
			os.makedirs(directory)
		img_name = str(random2.randint(10000, 99999))+'.'+file_type
		img_directory = os.path.join(directory, img_name)
		img_path = os.path.join(config.IMAGE_URL_PATH, owner, Id, img_name)
		image_result = open(img_directory, 'wb') # create a writable image and write the decoding result
		image_result.write(image)
		#image.save(img_directory)
		return img_path
	except:
		return False

def if_input_exists(data):
	if not data:
		return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': {'error': 'There is no data!'}}
	return False

def initiation_validator(data):
	if if_input_exists(data):
		return (False, if_input_exists(data))
	if 'cellNumber' not in data.keys():
		return (False, {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "cellNumber is missed!"})
	return (True, None)

def input_validator(data, object_type):
	if 'cellNumber' not in data.keys():
		return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "cellNumber is missed!"}
	if 'title' not in data.keys():
		return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "title is missed!"}
	if 'product' in object_type:
		if 'category' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "category is missed!"}
		if 'shopId' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "shopId is missed!"}
	return False

def like_view_validator(data, scope):
	if if_input_exists(data):
		return (False, if_input_exists(data))
	if 'userId' not in data.keys():
		return (False, {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "userId is missed!"})
	if scope == 'product':
		if 'productId' not in data.keys():
			return (False, {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "productId is missed!"})
	elif scope == 'shop':
		if 'shopId' not in data.keys():
			return (False, {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "shopId is missed!"})
	return (True, None)

def validating_request(data, object_type):
	if if_input_exists(data):
		return (False, if_input_exists(data))
	if input_validator(data, object_type):
		return (False, input_validator(data, object_type))
	user = models.User.query.filter_by(cellNumber = data['cellNumber']).first()
	if not user:
		return (False, {'status': config.HTML_STATUS_CODE['NotFound'],
			'message': "The User is not Registered!"})
	return (True, {'owner': user.userId})

def make_record(data, object_type, record):
	objectId = str(uuid.uuid4())
	encoded_img_list = data['imageList'] if 'imageList' in data.keys() else []
	record['imageList'] = []
	for encoded_img in encoded_img_list:
		decoded_img = base64.b64decode(encoded_img)
		img_directory = save_encoded_image(decoded_img, record['owner'], objectId)
		if img_directory:
			record['imageList'].append(img_directory)
		else:
			return False
	if 'product' in object_type:
		record['productId'] = objectId
		record['shopId'] = data['shopId']
		record['category'] = data['category']
		record['price'] = data['price'] if 'price' in data.keys() else (1)
		record['ifUsed'] = data['ifUsed'] if 'ifUsed' in data.keys() else False
		record['city'] = data['city'] if 'city' in data.keys() else None
	elif 'shop' in object_type:
		record['shopId'] = objectId
		record['address'] = data['address'] if 'address' in data.keys() else None
		record['phoneNumber'] = data['phoneNumber'] if 'phoneNumber' in data.keys() else None
		record['bankAcountsInformation'] = data['bankAcountsInformation'] if 'bankAcountsInformation' in data.keys() else []
		record['shopLink'] = "http://rstaak.ir/"
	record['title'] = data['title']
	record['description'] = data['description'] if 'description' in data.keys() else None
	record['createdDatetime'] = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	return record

def query_range(data):
	number = data['number'] if 'number' in data.keys() else 50
	factor = data['factor'] if 'factor' in data.keys() else 1
	return (number*(factor-1), number*factor)

def query_result(data, query_type, l1, l2):
	if 'product' in query_type:
		objectId = data['productId'] if 'productId' in data.keys() else None
		userId = data['userId'] if 'userId' in data.keys() else None
		model = ({'productId': objectId}, models.Product)
		result = filter_query(data, model, objectId, l1, l2)
		return product_model(result, userId)
	elif 'shop' in query_type:
		objectId = data['shopId'] if 'shopId' in data.keys() else None
		userId = data['userId'] if 'userId' in data.keys() else None
		model = ({'shopId': objectId}, models.Shop)
		result = filter_query(data, model, objectId, l1, l2)
		return shop_model(result, userId)
	elif 'user' in query_type:
		objectId = data['userId'] if 'userId' in data.keys() else None
		model = ({'userId': objectId}, models.User)
		result = filter_query(data, model, objectId, l1, l2)
		return user_model(result)

def location_query(data, query_type):
	mongo_cursor = config_mongodb()
	result = []
	if query_type == 'ostan':
		result = mongo_cursor.Ostan.find(data)
	elif query_type == 'shahrestan':
		result = mongo_cursor.Shahrestan.find(data)
	elif query_type == 'bakhsh':
		result = mongo_cursor.Bakhsh.find(data)
	elif query_type == 'shahr':
		result = mongo_cursor.Shahr.find(data)
	elif query_type == 'dehestan':
		result = mongo_cursor.Dehestan.find(data)
	elif query_type == 'abadi':
		result = mongo_cursor.Abadi.find(data)
	elif query_type == 'dehshahr':
		r1 = mongo_cursor.Dehestan.find(data)
		for r in r1:
			result.append(('dehestan', r))
		r2 = mongo_cursor.Shahr.find(data)
		for r in r2:
			result.append(('shahr', r))
	return location_query_result_list(query_type, result)
	
def location_query_result_list(query_type, result):
	result_list = []
	for item in result:
		if query_type == 'dehshahr':
			rec = all_items_for_location_query(item[1])
			rec['type'] = item[0]
		else:
			rec = all_items_for_location_query(item)
			rec['type'] = query_type
		result_list.append(rec)
	if result_list:
		return {'status': config.HTML_STATUS_CODE['Success'],
		'message': {'result': result_list}, 'found records': len(result_list)}
	return {'status': config.HTML_STATUS_CODE['NoContent'], 'message': 'There is no result!'}

def regex_query(data, query_type):
	mongo_cursor = config_mongodb()
	regex_result = []
	query_list = []
	all_flag = False
	for key, value in data.items():
		if key == 'all':
			query_list.append({'name':{'$regex': value }})
			all_flag = True
			break
		elif key in config.LOCATION_QUERY:
			query_list.append({'name':{'$regex': value }})
		else:
			query_list.append({key: value})
	if all_flag:
		regex_result.append(('shahrestan', mongo_cursor.Shahrestan.find({'$and':query_list})))
		regex_result.append(('shahr', mongo_cursor.Shahr.find({'$and':query_list})))
		regex_result.append(('dehestan', mongo_cursor.Dehestan.find({'$and':query_list})))
		regex_result.append(('abadi', mongo_cursor.Abadi.find({'$and':query_list})))
	else:
		regex_result.append(mongo_cursor.Abadi.find({'$and':query_list}))
	return regex_query_result_list(regex_result)

def regex_query_result_list(result):
	mongo_cursor = config_mongodb()
	result_list = []
	if len(result) > 1:
		for res in result:
			for item in res[1]:
				rec = all_items_for_location_query(item)
				rec['type'] = res[0]
				result_list.append(rec)
	else:
		for item in result:
			result_list.append({'name': item['name'], 'id': item['id']})
	if result_list:
		return {'status': config.HTML_STATUS_CODE['Success'],
		'message': {'result': result_list}, 'found records': len(result_list)}
	return {'status': config.HTML_STATUS_CODE['NoContent'], 'message': 'There is no result!'}

def all_items_for_location_query(item):
	rec = {'name': item['name'], 'id': item['id']}
	if 'ostan' in item.keys():
			rec['ostan'] = item['ostan']
	if 'shahrestan' in item.keys():
		rec['shahrestan'] = item['shahrestan']
	if 'bakhsh' in item.keys():
			rec['bakhsh'] = item['bakhsh']
	if 'dehestan' in item.keys():
		rec['dehestan'] = item['dehestan']
	return rec

def filter_query(data, model, objectId, l1, l2):
	if objectId:
		result = model[1].query.filter_by(**model[0])
	else:
		q = {}
		for key, value in data.items():
			if (value) and key not in ['number', 'factor', 'userId']:
				q[key] = value
		result = list(model[1].query.filter_by(**q).order_by(model[1].createdDatetime))[-(l1+1):-(l2+1):-1]
	return result

def like_view_action(data, action_type, scope):
	status = config.HTML_STATUS_CODE['Duplicate']
	if scope == 'product':
		scope_result = db.session.query(models.Product).filter_by(productId = data['productId']).first()
	elif scope == 'shop':
		scope_result = db.session.query(models.Shop).filter_by(shopId = data['shopId']).first()
	if action_type == 'view':
		v_list = copy.deepcopy(scope_result.viewList)
		if data['userId'] in v_list:
			return (False, {'status': status, 'message': "viewed before!"})
		v_list.append(data['userId'])
		scope_result.viewList = v_list
	elif action_type == 'like':
		l_list = copy.deepcopy(scope_result.likeList)
		if data['userId'] in l_list:
			return (False, {'status': status, 'message': "liked before!"})
		l_list.append(data['userId'])
		scope_result.likeList = l_list
	elif action_type == 'dislike':
		l_list = copy.deepcopy(scope_result.likeList)
		if data['userId'] not in l_list:
			return (False, {'status': status, 'message': "the user didn't like this product!"})
		l_list.remove(data['userId'])
		scope_result.likeList = l_list
	db.session.commit()
	l1, l2 = (len(scope_result.viewList), len(scope_result.likeList))
	db.session.close()
	return (True, [l1, l2])

def user_model(result):
	result_list = []
	for r in result:
		result_dict = {
		'cellNumber': r.cellNumber,
		'userId': r.userId,
		'createdDatetime': r.createdDatetime,
		'modified_on': r.modified_on,
		'name': r.name,
		'family': r.family,
		'nationalCode': r.nationalCode,
		'address': r.address,
		'shopList': r.shopList
		}
		result_list.append(result_dict)
	return result_list

def product_model(result, userId):
	result_list = []
	for r in result:
		likeFlag = True if userId in r.likeList else False
		result_dict = {
		'productId' : r.productId,
		'owner' : r.owner,
		'shopId': r.shopId,
		'createdDatetime': r.createdDatetime,
		'modified_on': r.modified_on,
		'title' : r.title,
		'category' : r.category,
		'description' : r.description,
		'price' : r.price,
		'imageList' : r.imageList,
		'ifUsed' : r.ifUsed,
		'city' : r.city,
		'viewedNumber' : len(r.viewList),
		'likedNumber': len(r.likeList),
		'likeFlag': likeFlag
		}
		result_list.append(result_dict)
	return result_list

def shop_model(result, userId):
	result_list = []
	for r in result:
		likeFlag = True if userId in r.likeList else False
		result_dict = {
		'shopId' : r.shopId,
		'owner' : r.owner,
		'createdDatetime': r.createdDatetime,
		'modified_on': r.modified_on,
		'title' : r.title,
		'description' : r.description,
		'address' : r.address,
		'imageList' : r.imageList,
		'phoneNumber': r.phoneNumber,
		'productsList': r.productsList,
		'bankAcountsInformation': r.bankAcountsInformation,
		'shopLink': r.shopLink,
		'viewedNumber' : len(r.viewList),
		'likedNumber': len(r.likeList),
		'likeFlag': likeFlag
		}
		result_list.append(result_dict)
	return result_list