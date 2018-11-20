
var crypto = require('crypto');
module.exports = function(app) {
	app.post('/user/register', function(req,res){
		var connection = app.config.dbConnection();
		var generic = new app.app.models.GenericDAO(connection);
		console.log("Chegou no caminho de registro")
		var requisicao =  JSON.parse(JSON.stringify(req.body));
		console.log(requisicao);
		var senhaCriptografada = crypto.createHash('md5').update("teste").digest('hex');
		var usuario = "teste";
		console.log(usuario)
		try{
		generic.find({usuario: usuario},'usuario',function(error, result){
			if(error){
				
				console.log(error);
			}
			if( result.length > 0){
			result = result[0];
			console.log(result.senha);
			console.log(senhaCriptografada);
			if(senhaCriptografada == result.senha && usuario == result.usuario){
				res.json("senha ok")
			}
			else {

				res.json("senha invalida");
			}
			console.log(result);
		} else {
			res.json("login invalido");
		}

		});
	}catch(error){
			console.log("error");
	}
	});


}