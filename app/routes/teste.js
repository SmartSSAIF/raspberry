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


	app.post("/confirmaPedido", (req, res)=>{

		console.log("Confirmando Pedido");
		client.invoke("confirmaPedido", function(error, res, more) {
			console.log(res);
		});

		res.send(req.body)
	})



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

	app.post('/setUltrassom', function(req,res){
		var corpo = JSON.parse(JSON.stringify(req.body));
		console.log(req.body);
		console.log("Set ultrassom valor : ",corpo.distancia);
		res.send(corpo);
		client.invoke("setUltrassom",corpo.distancia, function(error, res, more) {
			console.log(res);
		});

	});


	app.post('/zerar', function(req,res){
		var corpo = JSON.parse(JSON.stringify(req.body));
		console.log("Zerando distancia");
		res.send(corpo);
		client.invoke("zerar", function(error, res, more) {
			console.log(res);
		});

	});

       app.post('/setTensao', function(req,res){
           var corpo = JSON.parse(JSON.stringify(req.body));
           res.status(200).send(corpo);
           client.invoke("setTensao",corpo.tensao, function(error, res, more){
	   if(error){
	   console.log(error);
	   }
	   console.log(res);
	});
       });

       app.post('/setTempoBateria', function(req, res){
	   var corpo = JSON.parse(JSON.stringify(req.body));
	   res.status(200).send(corpo);

         client.invoke("setTempoBateria", corpo.tempo, function(error, res, more){
		if(error){
		 console.log(error);
		}
                  console.log(res);

	});


    });

		app.post('/instrucao', function(req,res){
			console.log("Body ", req.body)
			client.connect("tcp://0.0.0.0:4242");
			var lista = [];
			var instrucoes = JSON.parse(req.body.inst)
			for(var instrucao of instrucoes){
					if(JSON.stringify(instrucao).includes("node")){
	
						var enviar = {
									lugar: instrucao.node.lugar,
									rfid: instrucao.node.rfid,
									peso: instrucao.peso,
									distancia: instrucao.distancia,
									isFinal : instrucao.isFinal,
									pedido : req.body
							}
							lista.push(JSON.stringify(enviar))
							console.log('e ',enviar)        }
					else {
						console.log('Vem ',instrucao)
		
					}
			}
		// client.invoke("addInstrucao", req.body.inst, function(error, res, more) {
			client.invoke("recebeInstrucao", lista, function(error, res, more) {
				console.log(res);
			});
			return res.status(200).send({ok:1})


		})


}
