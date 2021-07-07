from rousta import db
from sqlalchemy.dialects.postgresql import JSON
import datetime, jdatetime
import uuid

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
	userId = db.Column(db.String(200), primary_key=True, nullable=False, default=uuid.uuid4)
	cellNumber = db.Column(db.String(13), unique=True, index=True)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	password = db.Column(db.String(300), default=None)
	name = db.Column(db.String(150), default=None)
	family = db.Column(db.String(250), default=None)
	fullName = db.Column(db.String(400), default=None)
	nationalCode = db.Column(db.String(10), index=True, default=None)
	address = db.Column(db.Text(), default=None)
	productsList = db.relationship('Product', backref='owner')
	#purchaseHistory = db.relationship('Product', backref='purchases')
	shopList = db.relationship('Shop', backref='owner')

class Product(BaseMixin, db.Model):
	__tabelname__ = 'products'
	productId = db.Column(db.String(200), primary_key=True, nullable=False, default=uuid.uuid4)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	ownerId = db.Column(db.String(200), db.ForeignKey('user.userId'))
	categoryId = db.Column(db.String(200), db.ForeignKey('childcategory.categoryId'))
	shopId = db.Column(db.String(200), db.ForeignKey('shop.shopId'))
	title = db.Column(db.String(200), index=True)
	description = db.Column(db.Text(), default=None)
	price = db.Column(db.Integer(), default=None)
	imageList = db.Column(JSON, default=[])
	ifUsed = db.Column(db.Boolean(), default=False)
	ifPublished = db.Column(db.Boolean(), default=True)
	vitrin = db.Column(db.Boolean(), default=False)
	rostaakLocation = db.Column(JSON)
	ordered = db.Column(db.Integer(), default=0)
	viewList = db.Column(JSON, default=[])
	likeList = db.Column(JSON, default=[])

class Shop(BaseMixin, db.Model):
	__tabelname__ = 'shops'
	shopId = db.Column(db.String(200), primary_key=True, nullable=False, default=uuid.uuid4)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	ownerId = db.Column(db.String(200), db.ForeignKey('user.userId'))
	title = db.Column(db.String(200), index=True)
	description = db.Column(db.Text(), default=None)
	imageList = db.Column(JSON, default=[])
	address = db.Column(db.Text(), default=None)
	phoneNumber = db.Column(db.String(13), default=None)
	bankAcountsInformation = db.Column(JSON, default=[])
	viewList = db.Column(JSON, default=[])
	likeList = db.Column(JSON, default=[])
	shopLink = db.Column(db.String(200), default=None)
	productsList = db.relationship('Product', backref='shop')

class Childcategory(BaseMixin, db.Model):
	__tabelname__ = 'childcategories'
	categoryId = db.Column(db.String(200), primary_key=True, nullable=False, default=uuid.uuid4)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	title = db.Column(db.String(200), index=True)
	parentCategory = db.Column(db.String(200), db.ForeignKey('parentcategory.categoryId'))
	imageList = db.Column(JSON, default=[])
	productsList = db.relationship('Product', backref='category')

class Parentcategory(BaseMixin, db.Model):
	__tabelname__ = 'parentcategories'
	categoryId = db.Column(db.String(200), primary_key=True, nullable=False, default=uuid.uuid4)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	title = db.Column(db.String(200), index=True)
	imageList = db.Column(JSON, default=[])
	childCategories = db.relationship('Childcategory', backref='parent')

class Image(BaseMixin, db.Model):
	__tabelname__ = 'images'
	imageId = db.Column(db.String(200), primary_key=True, nullable=False, default=uuid.uuid4)
	createdDatetime = db.Column(db.String(20))
	modified_on = db.Column(db.DateTime(), onupdate=datetime.datetime.now)
	productId = db.Column(db.String(200), db.ForeignKey('product.productId'))
	shopId = db.Column(db.String(200), db.ForeignKey('shop.shopId'))
	shopId = db.Column(db.String(200), db.ForeignKey('childcategory.categoryId'))
	shopId = db.Column(db.String(200), db.ForeignKey('parentcategory.categoryId'))
	imageType = db.Column(db.String(200), index=True)
	imageDir = db.Column(db.String(200))

db.create_all()