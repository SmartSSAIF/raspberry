var zerorpc = require("zerorpc");
var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

module.exports = function(app) {
	app.get('/teste', function(req,res){
		console.log("teste");
		var varTeste = req.query.teste;
		// var connection = app.config.dbConnection();
		// var generic = new app.app.models.GenericDAO(connection);
		// try { 
		// 		let instituto = {
		// 			nome: "if sula",
		// 			endereco: 2,


		// 		};
		// 		generic.create(instituto,"instituto", function(error, result){
		// 			if(error)
		// 				console.log(error);
		// 			else console.log("ok");

		// 		});
		
		// 		generic.read('instituto',function(erro,result){
		// 			console.log(result);
		// 		});
		
		// 		generic.find({idEndereco: 2},'endereco',function(erro, result){
		// 			console.log(">>")
		// 			if(erro)
		// 				console.log(erro)
		// 			else console.log(result);

		// 		});
		// 		let novoEndereco = {
		// 			idEndereco: 2,
		// 			rua: 'boboes',
		// 			numero: 362,
		// 			bairro: 'bairro2',
		// 			cidade: 'peteca'
		// 		};

		// 		// generic.update(novoEndereco,'idEndereco', 2,'endereco',function(erro,result){
		// 		// 	if(erro)
		// 		// 		console.log(erro);
		// 		// });
		// 			generic.update(novoEndereco,{idEndereco: 2},'endereco',function(erro,result){
		// 			if(erro)
		// 				console.log(erro);
		// 		})
		// }catch(erro){
		// 	console.log("que porra é val");
		// 	console.log(erro);
		// }

		res.send("recebido");

	}) ;
	app.post('/', function(req,res){
		var corpo = JSON.parse(JSON.stringify(req.body));
		console.log(req.body);
		console.log("chegou msg");
		console.log(corpo);
		res.send("funcionando !");

	});
	app.post('/pontoA', function(req,res){
		var corpo = JSON.parse(JSON.stringify(req.body));
		console.log(req.body);
		console.log("chegou Ponto  A");
		console.log(corpo);
		res.send("funcionando !");
		console.log("---- zerorpc ------ ");
		client.invoke("pontoA", function(error, res, more) {
			console.log(res);
		});

	});
	app.post('/pontoB', function(req,res){
		var corpo = JSON.parse(JSON.stringify(req.body));
		console.log(req.body);
		console.log("chegou ponto B");
		console.log(corpo);
		res.send("funcionando !");
		client.invoke("pontoB", function(error, res, more) {
			console.log(res);
		});

	});
	app.post('/setPWM', function(req,res){
		var corpo = JSON.parse(JSON.stringify(req.body));
		console.log(req.body);
		console.log("Set PWM valor : ", corpo.pwm);
		res.send(corpo);
		client.invoke("setPWM",corpo.pwm, function(error, res, more) {
			console.log(res);
		});

	});
	app.post('/setTime', function(req,res){
		var corpo = JSON.parse(JSON.stringify(req.body));
		console.log(req.body);
		console.log("Set time valor : ",corpo.time);
		res.send(corpo);
		client.invoke("setTime",corpo.time, function(error, res, more) {
			console.log(res);
		});

	});
	app.post('/setDistancia', function(req,res){
		var corpo = JSON.parse(JSON.stringify(req.body));
		console.log(req.body);
		console.log("Set distancia valor : ",corpo.distancia);
		res.send(corpo);
		client.invoke("setDistancia",corpo.distancia, function(error, res, more) {
			console.log(res);
		});

	});
	
	
}