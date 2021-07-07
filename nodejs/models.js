const Sequelize = require('sequelize');
const mysqlHost = 'localhost';
const mysqlUsername = "rstaakir_mysql";
const mysqlPassword = "Vi8Um-i(2*v;";
const mysqlDatabase = 'rstaakir_rostaak'; 

const sequelize = new Sequelize(mysqlDatabase, mysqlUsername, mysqlPassword, {
    host: mysqlHost,
    dialect: 'mysql',
    define: {
        charset: 'utf8',
        collate: 'utf8_general_ci',
        freezeTableName: true,
        underscored: false,
        timestamps: false
    }
});

const User = sequelize.define('user', {
    userId: {
        type: Sequelize.STRING,
        primaryKey: true,
        unique: true,
        allowNull: false
    },
    cellNumber: {
        type: Sequelize.STRING,
        unique: true
    },
    createdDatetime: {
        type: Sequelize.STRING
    },
    password: {
        type: Sequelize.STRING
    },
    name: {
        type: Sequelize.STRING
    },
    family: {
        type: Sequelize.STRING
    },
    fullName: {
        type: Sequelize.STRING
    },
    nationalCode: {
        type: Sequelize.STRING
    },
    address: {
        type: Sequelize.TEXT
    }
}, {
    tableName: 'user'
});

const Product = sequelize.define('product', {
    productId: {
        type: Sequelize.STRING,
        primaryKey: true,
        unique: true,
        allowNull: false
    },
    ownerId: {
        type: Sequelize.STRING,
        // references: {
        //     model: User,
        //     key: 'userId',
        // }
    },
    // categoryId: {
    //     type: Sequelize.STRING,
    //     references: {
    //         model: Childcategory,
    //         key: 'categoryId',
    //     }
    // },
    // shopId: {
    //     type: Sequelize.STRING,
    //     references: {
    //         model: Shop,
    //         key: 'shopId',
    //     }
    // },
    createdDatetime: {
        type: Sequelize.STRING
    },
    title: {
        type: Sequelize.STRING
    },
    description: {
        type: Sequelize.TEXT
    },
    price: {
        type: Sequelize.INTEGER
    },
    imageList: {
        type: Sequelize.JSON
    },
    ifUsed: {
        type: Sequelize.BOOLEAN
    },
    ifPublished: {
        type: Sequelize.BOOLEAN
    },
    vitrin: {
        type: Sequelize.BOOLEAN
    },
    rostaakLocation: {
        type: Sequelize.JSON
    },
    ordered: {
        type: Sequelize.INTEGER
    },
    viewList: {
        type: Sequelize.JSON
    },
    likeList: {
        type: Sequelize.JSON
    },
}, {
    tableName: 'product'
});

//User.hasOne(Product, {as: 'owner', foreignKey : 'ownerId'});
//User.hasMany(Product, {as: 'owner', foreignKey : 'ownerId'});

User.associate = models => {
    User.hasMany(models.Product, { foreignKey: 'ownerId'});
}


// module.exports = User;
// module.exports = Product;

module.exports = {
    User: User,
    Product: Product
};
