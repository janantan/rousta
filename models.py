from rousta import db
from sqlalchemy.dialects.postgresql import JSON
import datetime, jdatetime

class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()

    @classmethod
    def delete(cls, obj):
        db.session.delete(obj)
        db.session.commit()

class User(BaseMixin, db.Model):
	__tabelname__ = 'users'
	#id = db.Column(db.BigInteger())
	userId = db.Column(db.String(200), primary_key=True)
	cellNumber = db.Column(db.String(13), unique=True, index=True)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	password = db.Column(db.String(300))
	name = db.Column(db.String(150))
	family = db.Column(db.String(250))
	fullName = db.Column(db.String(400))
	nationalCode = db.Column(db.String(10), index=True)
	address = db.Column(db.Text())
	adList = db.Column(JSON)
	purchaseHistory = db.Column(JSON)
	shopList = db.Column(JSON)

	def __init__(self, cellNumber, userId, createdDatetime, password=None,
		name=None, family=None, nationalCode=None, address=None, adList=[],
		purchaseHistory=[], shopList=[]):
		self.cellNumber = cellNumber
		self.userId = userId
		self.createdDatetime = createdDatetime
		self.password = password
		self.name = name
		self.family = family
		self.nationalCode = nationalCode
		self.address = address
		self.adList = adList
		self.purchaseHistory = purchaseHistory
		self.shopList = shopList

class Product(BaseMixin, db.Model):
	__tabelname__ = 'products'
	#id = db.Column(db.BigInteger())
	productId = db.Column(db.String(200), primary_key=True)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	owner = db.Column(db.String(200), index=True)
	title = db.Column(db.String(200), index=True)
	categoryId = db.Column(db.String(200))
	categoryName = db.Column(db.String(200))
	description = db.Column(db.Text())
	price = db.Column(db.Integer())
	imageList = db.Column(JSON)
	ifUsed = db.Column(db.Boolean())
	ifPublished = db.Column(db.Boolean())
	vitrin = db.Column(db.Boolean())
	rostaakLocation = db.Column(JSON)
	shopId = db.Column(db.String(200))
	shopName = db.Column(db.String(200))
	byer = db.Column(db.String(200))
	ordered = db.Column(db.Integer())
	viewList = db.Column(JSON)
	likeList = db.Column(JSON)

	def __init__(self, productId, createdDatetime, owner, title, categoryId,
		shopId, rostaakLocation, shopName, categoryName,description=None, price=None,
		imageList=[], ifUsed=False, ifPublished=True, vitrin=False, byer=None,
		ordered=0, viewList=[], likeList=[]):
		self.productId = productId
		self.createdDatetime = createdDatetime
		self.owner = owner
		self.title = title
		self.categoryId = categoryId
		self.description = description
		self.price = price
		self.imageList = imageList
		self.ifUsed = ifUsed
		self.ifPublished = ifPublished
		self.vitrin = vitrin
		self.rostaakLocation = rostaakLocation
		self.shopId = shopId
		self.byer = byer
		self.ordered = ordered
		self.viewList = viewList
		self.likeList = likeList

class Shop(BaseMixin, db.Model):
	__tabelname__ = 'shops'
	#id = db.Column(db.BigInteger())
	shopId = db.Column(db.String(200), primary_key=True)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	owner = db.Column(db.String(200), index=True)
	title = db.Column(db.String(200), index=True)
	description = db.Column(db.Text())
	imageList = db.Column(JSON)
	address = db.Column(db.Text())
	phoneNumber = db.Column(db.String(13))
	productsList = db.Column(JSON)
	customersList = db.Column(JSON)
	bankAcountsInformation = db.Column(JSON)
	viewList = db.Column(JSON)
	likeList = db.Column(JSON)
	shopLink = db.Column(db.String(200))

	def __init__(self, shopId, createdDatetime, owner, title, description=None,
		imageList=[], address=None, phoneNumber=None, productsList=[], customersList=[],
		bankAcountsInformation=[], viewList=[], likeList=[], shopLink=None):
		self.shopId = shopId
		self.createdDatetime = createdDatetime
		self.owner = owner
		self.title = title
		self.description = description
		self.imageList = imageList
		self.address = address
		self.phoneNumber = phoneNumber
		self.productsList = productsList
		self.customersList = customersList
		self.bankAcountsInformation = bankAcountsInformation
		self.viewList = viewList
		self.likeList = likeList
		self.shopLink = shopLink

class Category(BaseMixin, db.Model):
	__tabelname__ = 'categories'
	#id = db.Column(db.BigInteger())
	categoryId = db.Column(db.String(200), primary_key=True)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	title = db.Column(db.String(200), index=True)
	childCategories = db.Column(JSON)
	imageList = db.Column(JSON)
	parentCategory = db.Column(db.String(200))
	productsList = db.Column(JSON)

	def __init__(self, categoryId, createdDatetime, title, childCategories=[],
		parentCategory=None, productsList=[], imageList=[]):
		self.categoryId = categoryId
		self.createdDatetime = createdDatetime
		self.title = title
		self.childCategories = childCategories
		self.parentCategory = parentCategory
		self.productsList = productsList
		self.imageList = imageList

db.create_all()