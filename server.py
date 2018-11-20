import zerorpc

class HelloRPC(object):
    def segundoMetodo(self, texto):
        return "baiano"
    def hello(self, name):
        return "Hello, %s" % name
s = zerorpc.Server(HelloRPC())
s.bind("tcp://0.0.0.0:4242")
s.run()
