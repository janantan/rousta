from ippanel import Client, Error, HTTPError, ResponseCode
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from rousta import app
import random2
import base64
import os
import config

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
		    config.SMS_PATTERN_CODE,    # pattern code
		    config.SMS_ORIGINATOR,      # originator
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