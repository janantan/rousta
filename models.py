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
	id = db.Column(db.BigInteger(), primary_key=True)
	cellNumber = db.Column(db.String(13), unique=True, index=True)
	userId = db.Column(db.String(200), index=True)
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
	id = db.Column(db.BigInteger(), primary_key=True)
	productId = db.Column(db.String(200), unique=True, index=True)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	owner = db.Column(db.String(200), index=True)
	title = db.Column(db.String(200))
	category = db.Column(db.String(300))
	description = db.Column(db.Text())
	price = db.Column(db.Integer())
	imageList = db.Column(JSON)
	ifUsed = db.Column(db.Boolean())
	city = db.Column(db.String(10))
	byer = db.Column(db.String(200))
	ordered = db.Column(db.Integer())
	viewed = db.Column(db.Integer())

	def __init__(self, productId, createdDatetime, owner, title, category,
		description=None, price=None, imageList=[], ifUsed=False, city=None, byer=None,
		ordered=0, viewed=0):
		self.productId = productId
		self.createdDatetime = createdDatetime
		self.owner = owner
		self.title = title
		self.category = category
		self.description = description
		self.price = price
		self.imageList = imageList
		self.ifUsed = ifUsed
		self.city = city
		self.byer = byer
		self.ordered = ordered
		self.viewed = viewed

class Shop(BaseMixin, db.Model):
	__tabelname__ = 'shops'
	id = db.Column(db.BigInteger(), primary_key=True)
	shopId = db.Column(db.String(200), unique=True, index=True)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	owner = db.Column(db.String(200), index=True)
	title = db.Column(db.String(200))
	description = db.Column(db.Text())
	image = db.Column(JSON)
	address = db.Column(db.String(10))
	phoneNumber = db.Column(db.String(13))
	productsList = db.Column(JSON)
	customersList = db.Column(JSON)
	bankAcountsInformation = db.Column(JSON)
	viewed = db.Column(db.Integer())
	shopLink = db.Column(db.String(200))

	def __init__(self, shopId, createdDatetime, owner, title, description=None,
		image=[], address=None, phoneNumber=None, productsList=[], customersList=[],
		bankAcountsInformation={}, viewed=0, shopLink=None):
		self.shopId = shopId
		self.createdDatetime = createdDatetime
		self.owner = owner
		self.title = title
		self.description = description
		self.image = image
		self.address = address
		self.phoneNumber = phoneNumber
		self.productsList = productsList
		self.customersList = customersList
		self.bankAcountsInformation = bankAcountsInformation
		self.viewed = viewed
		self.shopLink = shopLink

class Category(BaseMixin, db.Model):
	__tabelname__ = 'categories'
	id = db.Column(db.BigInteger(), primary_key=True)
	categoryId = db.Column(db.String(200), unique=True)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	title = db.Column(db.String(200))
	description = db.Column(db.Text())
	image = db.Column(JSON)
	productsList = db.Column(JSON)
	subsetList = db.Column(JSON)
	viewed = db.Column(db.Integer())

	def __init__(self, categoryId, createdDatetime, title, description=None,
		image=[], productsList=[], subsetList=[], viewed=0):
		self.categoryId = categoryId
		self.createdDatetime = createdDatetime
		self.title = title
		self.description = description
		self.image = image
		self.productsList = productsList
		self.subsetList = subsetList
		self.viewed = viewed

db.create_all()