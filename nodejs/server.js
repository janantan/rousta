const {User, Product} = require('./models.js');
const {MongoClient, mysqlAuth, uri, mongoDatabase} = require('./config.js');

const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const moment = require('moment');
const mongo = require('mongodb');
const mysql = require('mysql');
var uuid = require('uuid');

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

//for send a message in chat
io.on('connection', (socket) => {

    //mongo cursor
    MongoClient.connect(uri, {useUnifiedTopology: true},
        function (err, db) {
            if (err) throw err;
            cur = db.db(mongoDatabase);
        });

    //mysql connection
    var con = mysql.createConnection(mysqlAuth);
    con.connect(function(err) { if (err) throw err; });

    //register user
    socket.on('register', (phone_number) => {
        var query = {cellNumber: phone_number};
        cur.collection("users").findOne(query, function (err, result) {
            if (err) console.log(err);
            if (result) {
                var user_info = {cellNumber: phone_number, socket_id: "", location: "", location_id: ""};
                cur.collection("users").insertOne(user_info);
            }
        });
    });

    //set socket id
    socket.on('set_socket_id', (data) => {
        var query = {cellNumber: data.phone_number};
        var newValues = {$set: {socket_id: socket.id, location: data.location, location_id: data.id}};
        cur.collection("users").updateOne(query, newValues, function (err, res) {
            if (err) throw err;
            console.log('set_socket_id');
        });
    });

    //remove socket id
    socket.on('remove_socket_id', (phone_number) => {
        var query = {cellNumber: phone_number};
        var newValues = {$set: {socket_id: "", location: "", location_id: ""}};
        cur.collection("users").updateOne(query, newValues, function (err, res) {
            if (err) throw err;
            console.log('remove_socket_id');
        });
    });

    //send messages in chat
    socket.on('message', (data) => {
        console.log(data);
        //{$or: [{sender: phone_number}, {receiver: phone_number}]}
        cur.collection("products").findOne({productId: data.productId}, (err, result) => {
            if (err) throw err;
            if (result) {
                userIdList = result.userIdList;
                if (data.sender === result.ownerId) {
                    query = {productId: data.productId};
                    newMessage = newMessage(data.chatId, data.sender, data.content, true, false, false);
                    if (userIdList.indexOf(data.receiver)>=0) {
                        oldValue = result[data.receiver];
                    } else {
                        oldValue = [];
                        userIdList.push(data.receiver)
                    }
                    oldValue.push(newMessage);
                    setObject = {};
                    setObject[data.receiver] = oldValue;
                    setObject['userIdList'] = userIdList;
                    newValues = {$set: setObject};
                    cur.collection("products").updateOne(query, newValues, function (err, res) {
                        if (err) throw err;
                    });
                } else if (userIdList.indexOf(data.sender)>=0) {
                    var query = {productId: data.productId};
                    var oldValue = result[data.sender];
                    newMessage = newMessage(data.chatId, data.sender, data.content, true, false, false);
                    oldValue.push(newMessage);
                    setObject = {};
                    setObject[data.sender] = oldValue;
                    var newValues = {$set: setObject};
                    cur.collection("products").updateOne(query, newValues, function (err, res) {
                        if (err) throw err;
                    });
                } else {
                    query = {productId: data.productId};
                    newMessage = newMessage(data.chatId, data.sender, data.content, true, false, false);
                    oldValue = [];
                    oldValue.push(newMessage);
                    userIdList.push(data.sender);
                    setObject = {};
                    setObject[data.sender] = oldValue;
                    setObject['userIdList'] = userIdList;
                    newValues = {$set: setObject};
                    cur.collection("products").updateOne(query, newValues, function (err, res) {
                        if (err) throw err;
                    });
                }
                query = {userId: data.sender};
                cur.collection("users").findOne(query, function (err, result) {
                    if (err) throw err;
                    if (result.socket_id !== "") io.to(result.socket_id).emit("message", {sent: true});
                });
                query = {userId: data.receiver};
                cur.collection("users").findOne(query, function (err, result) {
                    if (err) throw err;
                    if (result.socket_id !== "") {
                        io.to(result.socket_id).emit("message", {message: data.content});
                        cur.collection("products").findOne({productId: data.productId}, function (err, result) {
                            var chatList = [];
                            for (chat of result[sender]) {
                                if (chat.chatId === data.chatId) {
                                    var newChat = newMessage(data.chatId, data.sender, data.content, true, true, false);
                                    chatList.push(newChat);
                                } else {

                                    chatList.push(chat);
                                }
                            }
                            setObject = {};
                            setObject[result[sender]] = chatList;
                            var newValues = {$set: setObject};
                            cur.collection("products").updateOne({productId: data.productId}, newValues, function (err, res) {
                                if (err) throw err;
                            });
                            cur.collection("users").findOne({userId: data.sender}, function (err, result) {
                                if (err) throw err;
                                if (result.socket_id !== "") io.to(result.socket_id).emit("message", {delivered: true});
                            });
                        });
                    }
                });
            } else {
                con.query("SELECT * FROM product WHERE productId = ?", data.productId, function (err, result) {
                    if (err) throw err;
                    var ownerId = result[0].ownerId;
                    con.query("SELECT * FROM user WHERE userId = ?", ownerId, (err, result) => {
                        if (err) throw err;
                        var msgList = [];
                        var userIdList = [];
                        var newMessage = newMessage(data.chatId, data.sender, data.content, true, false, false);
                        msgList.push(newMessage);
                        var rec = {
                            productId: data.productId,
                            ownerId: ownerId
                        };
                        userIdList.push(data.sender);
                        rec['userIdList'] = userIdList;
                        rec[data.sender] = msgList;
                        rec['if_newChat'] = true;
                        cur.collection("products").insertOne(rec, function (err, res) {
                            if (err) throw err;
                            var query = {userId: data.receiver};
                            cur.collection("users").findOne(query, function (err, result) {
                                if (err) throw err;
                                if (result.socket_id !== "") {
                                    io.to(result.socket_id).emit("message", {message: data.content});
                                    cur.collection("products").findOne({productId: data.productId}, function (err, result) {
                                        var chatList = [];
                                        for (chat of result[sender]) {
                                            if (chat.chatId === data.chatId) {
                                                var newChat = newMessage(data.chatId, data.sender, data.content, true, true, false);
                                                chatList.push(newChat);
                                            } else {

                                                chatList.push(chat);
                                            }
                                        }
                                        setObject = {};
                                        setObject[result[sender]] = chatList;
                                        var newValues = {$set: setObject};
                                        cur.collection("products").updateOne({productId: data.productId}, newValues, function (err, res) {
                                            if (err) throw err;
                                        });
                                        cur.collection("users").findOne({userId: data.sender}, function (err, result) {
                                            if (err) throw err;
                                            if (result.socket_id !== "") io.to(result.socket_id).emit("message", {delivered: true});
                                        });
                                    });
                                }
                            });
                            query = {userId: data.sender};
                            cur.collection("users").findOne(query, function (err, result) {
                                if (err) throw err;
                                if (result.socket_id !== "") io.to(result.socket_id).emit("message", {sent: true});
                            });
                        });
                    });
                });
            }
        });
    });

    //view a chat by receiver
    socket.on('view', data => {
        var query = {productId: data.productId};
        cur.collection("products").findOne(query, function (err, result) {
            if (err) throw err;
            var chatList = [];
            for (chat of result[data.userId]) {
                if (chat.chatId === data.chatId) {
                    var newChat = newMessage(chat.chatId, chat.sender, chat.content, true, true, true);
                    chatList.push(newChat);
                } else {
                    chatList.push(chat);
                }
            }
            setObject = {};
            setObject[result[data.userId]] = chatList;
            var newValues = {$set: setObject};
            cur.collection("products").updateOne(query, newValues, function (err, res) {
                if (err) throw err;
            });
            cur.collection("users").findOne({userId: data.userId}, function (err, result) {
                if (err) throw err;
                if (result.socket_id !== "") io.to(result.socket_id).emit("message", {viewed: true});
            });
        });
    });

    //models test
    socket.on('models_test', productId => {
        var newChat = newMessage('123', 'mohammadreza', 'mohtava', true, true, false);
        io.emit('models_test', newChat.sender);
        Product.findOne({ where: {productId: productId}, include: [{model: User, as: 'owner'}] }).then( result => {
            console.log(result.getUsers());
            console.log(result.owner);
            io.emit('models_test', result.title);
        }, error => {
            console.log(error);
        });
    });

    //disconnect
    socket.on('disconnect', () => {
        console.log('user disconnected');
    });

});

server.listen(5000, () => {
    console.log('listening on localhost:5000');
});

function newMessage(chatId, sender, content, sent, delivered, viewed) {
    newMessage = {
        chatId: chatId,
        sender: sender,
        sendDateTime: moment().format(),
        content: content,
        sent: sent,
        delivered: delivered,
        viewed: viewed
    };
    return newMessage;
}