import utils
import uuid
import jdatetime

parent_categories = [
'املاک و مستغلات',
'وسایل نقلیه',
'ادوات کشاورزی',
'خوراکی های محلی',
'محصولات باغی و زراعی',
'صنایع دستی',
'گیاهان دارویی',
'دام و طیور',
'لباس و پوشاک'
]

child_category_1 = [
'زمین کشاورزی',
'زمین مسکونی',
'ویلا',
'خانه روستایی',
'محل نگهداری دام',
'سیلو',
'انبار علوفه',
'اسکان بوم گردی',
'سیار'
]

child_category_2 = [
'تراکتور',
'کمباین',
'تیلر',
'سمپاش',
'اره چوب بری',
'شیردوش'
]

child_category_5 = [
'برنج',
'گندم و جو',
'حبوبات',
'زعفران',
'علوفه و کود'
]

def init(data):
	cursor = utils.config_mongodb()
	for cat in data:
		record = {}
		record['categoryId'] = str(uuid.uuid4())
		record['parentCategory'] = None
		record['childCategories'] = []
		record['productsList'] = []
		record['title'] = cat
		record['createdDatetime'] = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
		cursor.category.insert_one(record)

def childCategory(parentId, data):
	cursor = utils.config_mongodb()
	for cat in data:
		record = {}
		objectId = str(uuid.uuid4())
		record['categoryId'] = objectId
		record['parentCategory'] = parentId
		record['childCategories'] = []
		record['productsList'] = []
		record['title'] = cat
		record['createdDatetime'] = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
		cursor.category.insert_one(record)
		parent = cursor.category.find_one({'categoryId': parentId})
		child_list = parent['childCategories']
		child_list.append({'categoryId': objectId, 'title': cat})
		cursor.category.update_many({'categoryId': parentId}, {'$set':{'childCategories': child_list}})

#childCategory("e5ac72ae-5005-4b21-8326-c9d436614f8f", child_category_5)