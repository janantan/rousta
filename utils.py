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
import re
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
		if 'categoryId' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "categoryId is missed!"}
		if 'shopId' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "shopId is missed!"}
		if 'rostaakLocation' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "rostaakLocation is missed!"}
	return False

def delete_validator(data, object_type):
	if 'cellNumber' not in data.keys():
		return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "cellNumber is missed!"}
	if object_type == 'product':
		if 'productId' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "productId is missed!"}
	elif object_type == 'shop':
		if 'shopId' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "shopId is missed!"}
	elif object_type == 'category':
		if 'categoryId' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "categoryId is missed!"}
	elif object_type == 'user':
		if 'userId' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "userId is missed!"}
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
		record['categoryId'] = data['categoryId']
		record['rostaakLocation'] = transform_rostaak_location(data['rostaakLocation'])
		record['description'] = data['description'] if 'description' in data.keys() else None
		record['price'] = data['price'] if 'price' in data.keys() else (1)
		record['ifUsed'] = data['ifUsed'] if 'ifUsed' in data.keys() else False
		record['ifPublished'] = data['ifPublished'] if 'ifPublished' in data.keys() else True
		record['vitrin'] = data['vitrin'] if 'vitrin' in data.keys() else False
	elif 'shop' in object_type:
		record['shopId'] = objectId
		record['address'] = data['address'] if 'address' in data.keys() else None
		record['description'] = data['description'] if 'description' in data.keys() else None
		record['phoneNumber'] = data['phoneNumber'] if 'phoneNumber' in data.keys() else None
		record['bankAcountsInformation'] = data['bankAcountsInformation'] if 'bankAcountsInformation' in data.keys() else []
		record['shopLink'] = "http://rstaak.ir/"
	elif 'category' in object_type:
		record['categoryId'] = objectId
		record['parentCategory'] = data['parentCategory'] if 'parentCategory' in data.keys() else None
		del record['owner']
	record['title'] = data['title']
	record['createdDatetime'] = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	return record

def transform_rostaak_location(data):
	mongo_cursor = config_mongodb()
	if data['type'] == 'abadi':
		abadi = mongo_cursor.Abadi.find_one({'id': data['id']})
		rostaakLocation = {'type': data['type'], 'name': abadi['name'],
		'ostan': abadi['ostan']['name'], 'shahrestan': abadi['shahrestan']['name'],
		'bakhsh': abadi['bakhsh']['name'], 'dehestan': abadi['dehestan']['name']}
	if data['type'] == 'dehestan':
		dehestan = mongo_cursor.Dehestan.find_one({'id': data['id']})
		rostaakLocation = {'type': data['type'], 'name': dehestan['name'],
		'ostan': dehestan['ostan']['name'], 'shahrestan': dehestan['shahrestan']['name'],
		'bakhsh': dehestan['bakhsh']['name']}
	if data['type'] == 'shahr':
		shahr = mongo_cursor.Shahr.find_one({'id': data['id']})
		rostaakLocation = {'type': data['type'], 'name': shahr['name'],
		'ostan': shahr['ostan']['name'], 'shahrestan': shahr['shahrestan']['name'],
		'bakhsh': shahr['bakhsh']['name']}
	if data['type'] == 'shahrestan':
		shahrestan = mongo_cursor.Shahrestan.find_one({'id': data['id']})
		rostaakLocation = {'type': data['type'], 'name': shahrestan['name'],
		'ostan': shahrestan['ostan']['name']}
	return rostaakLocation

def insert_product(record):
	mongo_cursor = config_mongodb()
	fault_return = {'status': config.HTML_STATUS_CODE['NotFound'],
			'message': "The Parent does not Exist!"}
	shop_result = db.session.query(models.Shop).filter_by(shopId = record['shopId']).first()
	if not shop_result:
		return (fault_return)
	category_result = mongo_cursor.category.find_one({'categoryId': record['categoryId']})
	if not category_result:
		return jsonify(fault_return)
	products_list = copy.deepcopy(shop_result.productsList)
	products_list.append(record['productId'])
	catProductsList = category_result['productsList']
	catProductsList.append({'title': record['title'], 'productId': record['productId']})
	record['shopName'] = shop_result.title
	record['categoryName'] = category_result['title']
	models.Product.create(**record)
	shop_result.productsList = products_list
	db.session.commit()
	mongo_cursor.category.update_many({'categoryId': record['categoryId']}, {'$set':{'productsList': catProductsList}})
	return ({'status': config.HTML_STATUS_CODE['Success'],
		'message': {'productId': record['productId']}})

def insert_shop(record):
	models.Shop.create(**record)
	return ({'status': config.HTML_STATUS_CODE['Success'],
		'message': {'shopId': record['shopId']}})

def insert_category(record):
	mongo_cursor = config_mongodb()
	if record['parentCategory']:
		parent = mongo_cursor.category.find_one({'categoryId': record['parentCategory']})
		if not parent:
			return ({'status': config.HTML_STATUS_CODE['NotFound'],
				'message': "The Parent does not Exist!"})
		childCategories = parent['childCategories']
		childCategories.append({'title': record['title'], 'categoryId': record['categoryId']})
		mongo_cursor.category.update_many({'categoryId': record['parentCategory']},
			{'$set':{'childCategories': childCategories}})
	record['childCategories'] = []
	record['productsList'] = []
	mongo_cursor.category.insert_one(record)
	return ({'status': config.HTML_STATUS_CODE['Success'],
		'message': {'categoryId': record['categoryId']}})

def delete_object(data, object_type):
	if object_type == 'product':
		if db.session.query(models.Product).filter_by(productId = data['productId']).first():
			db.session.query(models.Product).filter_by(productId = data['productId']).delete()
			db.session.commit()
		else:
			return {'status': config.HTML_STATUS_CODE['NotFound'], 'message': object_type+"Id not found!"}
	if object_type == 'shop':
		if db.session.query(models.Shop).filter_by(shopId = data['shopId']).first():
			db.session.query(models.Shop).filter_by(shopId = data['shopId']).delete()
			db.session.commit()
		else:
			return {'status': config.HTML_STATUS_CODE['NotFound'], 'message': object_type+"Id not found!"}
	if object_type == 'user':
		if db.session.query(models.User).filter_by(userId = data['userId']).first():
			db.session.query(models.User).filter_by(userId = data['userId']).delete()
			db.session.commit()
		else:
			return {'status': config.HTML_STATUS_CODE['NotFound'], 'message': object_type+"Id not found!"}
	if object_type == 'category':
		mongo_cursor = config_mongodb()
		if mongo_cursor.category.find_one({'categoryId': data['categoryId']}):
			mongo_cursor.category.remove({'categoryId': data['categoryId']})
		else:
			return {'status': config.HTML_STATUS_CODE['NotFound'], 'message': object_type+"Id not found!"}
	return False

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

def category_query(data, query_type):
	mongo_cursor = config_mongodb()
	objectId = data['categoryId'] if 'categoryId' in data.keys() else None
	if objectId:
		result = []
		result.append(mongo_cursor.category.find_one({'categoryId': objectId}))
		return ({'status': config.HTML_STATUS_CODE['Success'],
			'message': {'result': category_model(result)}})
	child = data['child'] if 'child' in data.keys() else False
	if child:
		parentId = data['parentId'] if 'parentId' in data.keys() else None
		if not parentId: return ({'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "parentId is missed!"})
		return ({'status': config.HTML_STATUS_CODE['Success'],
			'message': {'result': category_model(mongo_cursor.category.find({'parentCategory': parentId}))}})
	return ({'status': config.HTML_STATUS_CODE['Success'],
		'message': {'result': category_model(mongo_cursor.category.find({'parentCategory': None}))}})

def special_shop_query(data):
	mongo_cursor = config_mongodb()
	shopId = data['shopId'] if 'shopId' in data.keys() else None
	if not shopId: return ({'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "shopId is missed!"})
	shop_result = models.Shop.query.filter_by(**{'shopId': shopId}).first()
	if not shop_result: return ({'status': config.HTML_STATUS_CODE['NotFound'], 'message': "shopId not found!"})
	products = []
	vitrin_products = []
	owner = shop_result.owner
	for productId in shop_result.productsList:
		product_result = models.Product.query.filter_by(**{'productId': productId}).first()
		if not product_result:
			continue
		product = {'title': product_result.title, 'productId': product_result.productId,
		'categoryId': product_result.categoryId}
		category = mongo_cursor.category.find_one({'categoryId': product_result.categoryId})
		parentCategory = mongo_cursor.category.find_one({'categoryId': category['parentCategory']})
		product['categoryName'] = category['title']
		product['parentCategory'] = category['parentCategory']
		product['parentCategoryName'] = parentCategory['title'] if parentCategory else None
		product['imageList'] = category['imageList'] if 'imageList' in category.keys() else []
		products.append(product)
		if product_result.vitrin: vitrin_products.append(product_result.productId)
	#return ({'status': config.HTML_STATUS_CODE['Success'], 'message': {'result': products}})
	parents_list = []
	parents = {}
	for product in products:
		if product['parentCategoryName'] in parents.keys():
			flag = False
			for i in range(len(parents[product['parentCategoryName']]['childs'])):
				if product['categoryName'] == parents[product['parentCategoryName']]['childs'][i]['childCategoryName']:
					N = parents[product['parentCategoryName']]['childs'][i]['productNumbers']
					parents[product['parentCategoryName']]['childs'][i]['productNumbers'] = N + 1
					flag = True
					break
			if not flag:
				parents[product['parentCategoryName']]['childs'].append({'childCategoryId': product['categoryId'], 'productNumbers': 1,
					'childCategoryName': product['categoryName'], 'categoryImage': product['imageList']})
		else:
			childs = []
			childs.append({'childCategoryId': product['categoryId'], 'productNumbers': 1,
				'childCategoryName': product['categoryName'], 'categoryImage': product['imageList']})
			parents[product['parentCategoryName']] = {
			'parentCategoryId': product['parentCategory'],
			'childs': childs
			}
	for key, value in parents.items():
		parent = value
		parent['parentCategoryName'] = key
		parents_list.append(parent)
	vitrin_result = []
	for p_id in vitrin_products:
		vitrin_result.append(models.Product.query.filter_by(**{'productId': p_id}).first())
	vitrin = product_model(vitrin_result, owner)
	return ({'status': config.HTML_STATUS_CODE['Success'],
		'message': {'result': parents_list}, 'vitrin': vitrin})

def adRegex_query_postgresql(data):
	pattern = '/^%{}%'.format(data['product'])
	#result = models.Category.query.filter(models.Category.productsList.ilike(pattern)).all()
	result = models.Category.query.filter()
	for r in result:
		output = []
		for item in r.productsList:
			#if re.search(pattern, item):
				#output.append((r.))
			#tsa = m.groups()[0] if m else None
		#if item.childCategories:
			#continue
			print(item.productsList)
	return {'status': config.HTML_STATUS_CODE['NoContent'], 'message': 'There is no result!'}

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
	if query_type == 'adRegex':
		return adRegex_query_mongo(data)
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
		#regex_result.append(('shahrestan', mongo_cursor.Shahrestan.find({'$and':query_list})))
		regex_result.append(('shahr', mongo_cursor.Shahr.find({'$and':query_list})))
		#regex_result.append(('dehestan', mongo_cursor.Dehestan.find({'$and':query_list})))
		regex_result.append(('abadi', mongo_cursor.Abadi.find({'abadi_type':'0', '$and':query_list})))
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

def adRegex_query_mongo(data):
	mongo_cursor = config_mongodb()
	regex_result = []
	query_list = []
	query_list.append({'productsList.title': {'$regex': data['product']}})
	result = mongo_cursor.category.find({'$and':query_list})
	for item in result:
		parent_result = mongo_cursor.category.find_one({'categoryId':item['parentCategory']})
		parent = {'title': parent_result['title'], 'categoryId': parent_result['categoryId']}
		category = {'title': item['title'], 'categoryId': item['categoryId']}
		titles = []
		for product in item['productsList']: titles.append(product['title'])
		product = []
		for title in titles:
			duplicate_flag = False
			for pdct in product:
				if pdct['title'] == title:
					duplicate_flag = True
					break
			if duplicate_flag: continue
			match = re.search('^'+data['product'], title)
			if match: product.append({'count': titles.count(title), 'title': title})
		if not product: continue
		rec = {'product': product, 'category': category, 'parentCategory': parent}
		regex_result.append(rec)
	if regex_result: return {'status': config.HTML_STATUS_CODE['Success'], 'message': {'result': regex_result}}
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
		'shopName': r.shopName,
		'createdDatetime': r.createdDatetime,
		'modified_on': r.modified_on,
		'title' : r.title,
		'categoryId' : r.categoryId,
		'categoryName' : r.categoryName,
		'description' : r.description,
		'price' : r.price,
		'imageList' : r.imageList,
		'ifUsed' : r.ifUsed,
		'ifPublished' : r.ifPublished,
		'vitrin' : r.vitrin,
		'rostaakLocation' : r.rostaakLocation,
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

def category_model(result):
	result_list = []
	for r in result:
		result_dict = {
		'title': r['title'],
		'categoryId': r['categoryId'],
		'createdDatetime': r['createdDatetime'],
		'childCategories': r['childCategories'],
		'parentCategory': r['parentCategory'],
		'imageList': r['imageList']
		}
		result_list.append(result_dict)
	return result_list