var mysql = require('mysql');
var connMySQL = function(){
	console.log("Criou conexao ");
	return mysql.createConnection({
		host : 'db4free.net',
		user : 'petequinha',
		password : 'petequinha',
		database : 'webduplainter'

	});
	// 	return mysql.createConnection({
	// 	host : 'localhost',
	// 	user : 'peteca',
	// 	password : 'petecambulante123',
	// 	database : 'webdupla'

	// });
};



module.exports = function(){
	console.log("Conectou ao servidor bd");
	return connMySQL;
};