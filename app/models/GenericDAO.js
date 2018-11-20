function GenericDAO(connection){

	this._connection = connection;
}

GenericDAO.prototype.create = function(field,table,callback){
	console.log("chegou para criar")
	let x = this._connection.query("insert into "+table+" set ?",[field], callback);
}
GenericDAO.prototype.read = function(table, callback) {
	console.log("leia");
	this._connection.query("select * from "+table, callback);
}
GenericDAO.prototype.find = function(field,table, callback) {
//	this._connection.query("select * from  ? where ? = ?", [field, field2, table], callback);
this._connection.query("select * from "+table+" where ?",field, callback);

}
GenericDAO.prototype.update = function(value,field2,table, callback){
	//this._connection.query("update "+table+" set ? where "+field+"= ?",[value,field2],callback);
	this._connection.query("update "+table+" set ? where ?",[value,field2],callback);
}
// call
module.exports = function(){
	return GenericDAO;
}


