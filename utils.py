from ippanel import Client, Error, HTTPError, ResponseCode
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from rousta import app
import datetime
import jdatetime
import random2
import base64
import uuid
import os
import config, models

#Config MongoDB
def config_mongodb():
	#mongodb://mongodb_user:password@localhost:27017/mongodb_db
	uri = "mongodb://{}:{}@{}:{}".format(
		config.MONGODB_USERNAME,
		config.MONGODB_PASSWORD,
		config.MONGODB_HOST,
		config.MONGODB_PORT
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

def input_validator(data, object_type):
	if 'cellNumber' not in data.keys():
		return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "cellNumber is missed!"}
	if 'title' not in data.keys():
		return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "title is missed!"}
	if 'category' in object_type:
		if 'category' not in data.keys():
			return {'status': config.HTML_STATUS_CODE['NotAcceptable'], 'message': "category is missed!"}
	return False

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
		model = ({'productId': objectId}, models.Product)
		result = filter_query(data, model, objectId, l1, l2)
		return product_model(result)
	elif 'shop' in query_type:
		objectId = data['shopId'] if 'shopId' in data.keys() else None
		model = ({'shopId': objectId}, models.Shop)
		result = filter_query(data, model, objectId, l1, l2)
		return shop_model(result)
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
			if (value) and key not in ['number', 'factor']:
				q[key] = value
		result = list(model[1].query.filter_by(**q))[-(l1+1):-(l2+1):-1]
	return result

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
		'adList': r.adList,
		'purchaseHistory': r.purchaseHistory,
		'shopList': r.shopList
		}
		result_list.append(result_dict)
	return result_list

def product_model(result):
	result_list = []
	for r in result:
		result_dict = {
		'productId' : r.productId,
		'owner' : r.owner,
		'createdDatetime': r.createdDatetime,
		'modified_on': r.modified_on,
		'title' : r.title,
		'category' : r.category,
		'description' : r.description,
		'price' : r.price,
		'imageList' : r.imageList,
		'ifUsed' : r.ifUsed,
		'city' : r.city,
		'byer' : r.byer,
		'ordered' : r.ordered,
		'viewed' : r.viewed
		}
		result_list.append(result_dict)
	return result_list

def shop_model(result):
	result_list = []
	for r in result:
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
		'customersList': r.customersList,
		'bankAcountsInformation': r.bankAcountsInformation,
		'viewed': r.viewed,
		'shopLink': r.shopLink
		}
		result_list.append(result_dict)
	return result_list