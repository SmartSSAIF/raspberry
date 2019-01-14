import socket
import sys
import subprocess
import os
import time
import RPi.GPIO as GPIO
import threading
from threading import Thread
import _thread
import serial
from datetime import datetime
import zerorpc
##Apresentacao BH/
tempoCaminho = 2
pwmGlobal = 85


serialEncoder = None

frequencia = 1000
ultimaTensao = 0
ultimaTag = ""

GPIO.setmode(GPIO.BCM)
pinoMotorA = 17
pinoMotorB = 18
trigger1 = 25
echo1 = 13
trigger2 = 5
echo2 = 6
GPIO.setwarnings(False)
GPIO.setup(4,GPIO.OUT)
GPIO.setup(trigger1, GPIO.OUT)
GPIO.setup(echo1, GPIO.IN)
GPIO.setup(trigger2, GPIO.OUT)
GPIO.setup(echo2, GPIO.IN)

GPIO.setup(pinoMotorA, GPIO.OUT)
GPIO.setup(pinoMotorB, GPIO.OUT)
GPIO.setwarnings(False)
pwm1 = GPIO.PWM(pinoMotorA, frequencia)
pwm2 = GPIO.PWM(pinoMotorB, frequencia)
pwm1.start(0)
pwm2.start(0)
instrucoes = []
boleanoMotor = False
semaforoInstrucoes = threading.Semaphore()
#class serialDistancia(Thread):



class Instrucao():
    def  __init__(self, tagA, tagB, angulo, peso, prioridade = 1):
        self.tagA = tagA
        self.tagB = tagB
        self.angulo = angulo
        self.peso = peso
        self.prioridade = prioridade

class Motor():
    motor = None
    def __new__(cls, *args, **kwargs):
        if not cls.motor:
            cls.motor = super(Motor, cls).__new__(cls, *args, **kwargs)
        return cls.motor
    def __init__(self):
        self.ptk = 0
    def iniciar(self):
        self.motorPode = True
        print("---------------------------------------------------------")
        self.sentidoFrente = False
        #GPIO.setmode(GPIO.BCM)
        #self.pinoMotorA = 17
        #self.pinoMotorB = 27
        #GPIO.setup(self.pinoMotorA, GPIO.OUT)
        #GPIO.setup(self.pinoMotorB, GPIO.OUT)
        # GPIO.setwarnings(False)
        # self.pwm1 = GPIO.PWM(self.pinoMotorA, 100)
        # self.pwm2 = GPIO.PWM(self.pinoMotorB, 100)
        # self.pwm1.start(0)
        # self.pwm2.start(0)
        self.rpm = 0
        self.zerarValores()
        self.valorPWMAtual = 0
        self.emMovimento = False
        self.fimDeCurso = True
    def sentido(self, booleano):
        if(booleano != self.sentidoFrente):
            if(self.emMovimento):
                self.frenagem()
                print("freiou")
            else:
                print("aceleracao")
                #self.aceleracao()
        else:
            print("Sentido já inicializado")
        self.sentidoFrente = booleano
    def alterarRPM(self, valor, tagDestino):
        global ultimaTag

        #for i in range(1,70):
        #    self.valorPWMAtual=i
        #    self.alterarPWM(self.valorPWMAtual)
        #    time.sleep(0.1)
        print("saiu for")
       # time.sleep(10)
        print("vai while")
        while self.rpm < valor and self.valorPWMAtual < 100 and not(ultimaTag in tagDestino) and self.motorPode:
            print(self.valorPWMAtual)
            self.valorPWMAtual+=1
            self.alterarPWM(self.valorPWMAtual)
            time.sleep(0.1)

        print("PWM "+str(self.valorPWMAtual)+" RPM "+str(self.rpm))
    def zerarValores(self):
        global pwm1
        global pwm2
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)
    def alterarPWM(self, valor):
        global pwm1
        global pwm2
        self.valorPWMAtual = valor
        #print("Sentido ",self.sentidoFrente)
        if(self.sentidoFrente):
            pwm1.ChangeDutyCycle(valor)
        else:
            pwm2.ChangeDutyCycle(valor)
    def aceleracao(self):
        for i in range(0,100,1):
            if(self.rpm<250):
                self.alterarPWM(i)
                time.sleep(0.001)

    def frenagem(self):
        for i in range(int(self.valorPWMAtual),0,-1):
            self.alterarPWM(i)
            time.sleep(0.001)
        self.zerarValores()
Motor().iniciar()

class serialDistancia(Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cm = serial.Serial("/dev/ttyACM1", 9600)

    def run(self):
        print("Iniciando serial")
        while True:
            self.msgSerial = self.cm.readline()
            try:
                self.msgSerial = self.msgSerial.decode()
                self.trataSerial(self.msgSerial)
            except:
                p = 0
    def trataSerial(self, msg):
        if(len(msg) > 0):
            Motor().frenagem()
            Motor().zerarValores()

    def setPulso(self, valor):
        self.cm.write(str(valor).encode())
serial = serialDistancia()
serial.start()
class HelloRPC(object):
    def segundoMetodo(self):
        x = (input('Set'))
        if (x == 'a'):
            GPIO.output(4, 1)
        elif (x == 's'):
            GPIO.output(4, 0)
        else:
            y = int(x)
            print("condicao ", (y > 0))
            Motor().sentido(y > 0)
            if (y != 0):
                Motor().aceleracao()
                Motor().alterarPWM(abs(y))
            else:
                Motor().zerarValores()
    def pontoA(self):
        print("Ponto A")
        self.executa(False)


    def pontoB(self):
        print("Ponto B")
        self.executa(True)
    def setDistancia(self, valor):
        global serialEncoder
        serialEncoder.write(valor)
    def executa(self, bool):
        global pwmGlobal
        if (not(Motor().sentidoFrente) == bool):
            print("ta aqui ")
            Motor().sentido(bool)
            Motor().aceleracao()
            Motor().alterarPWM(pwmGlobal)
        print("acabou if")
    def setPWM(self, valor):
        global pwmGlobal
        print("Setou pwm para ",valor)
        try:
            pwmGlobal = float(valor)
        except e:
            print("erro na conversao Pwm")
            print(e)
        print("setou pwm")

    def setTime(self,valor):
        global tempoCaminho
        print("Setou tempo para ",valor)
        try:
            tempoCaminho = float(valor)
        except e:
            print("erro na conversao Time")
            print(e)
    def setPercurso(self, valor):
        #Valor em centimetros
        print("comunicacao usb")
        com = serialDistancia()



server = HelloRPC()

class UsbComunicacao(threading.Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global server
        cm = serial.Serial('/dev/ttyACM0',9600)
        while True:
            msg = cm.readline().decode()
            print("Serial: ", msg)
            if("Deslocou o valor desejado" in msg):
                print("Tem que parar")
                server.setPWM(0)
            if("Monitor" in msg):
                split = msg.split(" ")
                r = Relatorio()
                r.gravar(split[1])

u = UsbComunicacao()
u.start()   










s = zerorpc.Server(server)
s.bind("tcp://0.0.0.0:4242")
s.run()

#fim motor
class Relatorio(Thread):
    def __init__(self):
        Thread.__init__(self)
    def gravar(self, tensao):
        nomeArq = 'relatorio.txt'
        arq = open(nomeArq,'a')
        arq.write("\n")
        d = datetime.now()
        s = str(str(d.day)+"/"+str(d.month)+"\t"+str(d.hour)+":"+str(d.minute)+":"+str(d.second))
        arq.write(s)
        arq.write("\n ")
        msg = "Tensao: " + tensao+"\n"
        arq.write(msg)

class Comunicacao(threading.Thread):
    def __init__(self):
        Thread.__init__(self)
        self.portaEnvio = 5010
        self.portaRecebe = 5005
        self.servidor = "192.168.0.120"
        self.motor = Motor()
    def run(self):
        print("Thread iniciada")
        self.listener()
    def enviarMensagem(self,  mensagem):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.sendto(mensagem.encode(), (self.servidor, self.portaEnvio))

    def listener(self):
        print("Iniciou listener")
        host = ""
        udpListener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpListener.bind((host, self.portaRecebe))
        while True:
            msg, cliente = udpListener.recvfrom(1024)
            _thread.start_new(self.tratamentoMensagem, (msg,))
    def tratamentoMensagem(self, mensagem):
        global sentido
        global liberado
        mensagem = mensagem.decode()
        print(mensagem)
        if(liberado):
            self.enviarMensagem("Liberado")
        if("Frente" in mensagem):
            self.motor.sentidoFrente = True
            self.motor.zerarValores()
        elif "Tras" in mensagem:
            self.motor.sentidoFrente = False
            self.motor.zerarValores()
        elif ("PWM" in mensagem):
            split = mensagem.split(" ")
            self.motor.alterarPWM(int(split[1]))
        elif("Ponto" in mensagem):
            _thread.start_new(self.enviarMensagem, tuple(self.servidor, ""))
        elif ("Instrucoes" in mensagem):

            try:
                mensagem = mensagem.replace("Instrucoes ", "")
                split = mensagem.split("/")
                print(split[0])
                for i in split:
                    if(len(i) <3):
                        break

                    print("i vale \t",i)
                    splitInstrucao = i.split(" ")
                    tagA = splitInstrucao[0]
                    tagB = splitInstrucao[1]
                    angulo = splitInstrucao[2]
                    peso = splitInstrucao[3]
                    prioridade = 1
                    instrucao = Instrucao(tagA, tagB, angulo, peso, prioridade)
                    semaforoInstrucoes.acquire()
                    instrucoes.append(instrucao)
                    semaforoInstrucoes.release()
            except:
                print("Erro linha 168 ", sys.exc_info()[0])

        # elif("Instrucoes" in mensagem):
        #     semaforoInstrucoes.acquire()
        #     try:
        #         mensagem = mensagem.decode().replace("Instrucoes ","")
        #         split = mensagem.split("/")
        #         for i in split:
        #             splitInstrucao = i.split(" ")
        #             tagA = splitInstrucao[0]
        #             tagB = splitInstrucao[1]
        #             angulo = splitInstrucao[2]
        #             peso = splitInstrucao[3]
        #             instrucao = Instrucao(tagA,tagB,angulo,peso,prioridade=1)
        #             instrucoes.append(instrucao)
        #         #     MUDAR ESTRUTURA DE INSTRUCAO !!!!!!!!!!!!
        #
        #
        #         ##parei aqui
        #     finally:
        #         semaforoInstrucoes.release()
        else:
            print("Mensagem inválida")
    def leituraSerial(self):
        global ultimaTag
        global ultimaTensao
        cm = serial.Serial('/dev/ttyACM0', 9600)
        while True:
            msgSerial = cm.readline()
            msgSerial = msgSerial.decode()
            #print(msgSerial)
            if("RFID" in msgSerial):
                splt = msgSerial.split(" ")
                ultimaTag = splt[1]
                print("ULTIMA TAG \t\t\t\t"+splt[1])
            if("Monitor" in msgSerial):
                split = msgSerial.split(" ")
                ultimaTensao = int(split[1])
                r = Relatorio()
                r.gravar(split[1])
            self.enviarMensagem(msgSerial)


print("Comunicacao")
comunicacao = Comunicacao()
print("Vai comecar")
comunicacao.start()
print("Passou o start")





#-------------------------------------------------------------------------------
#





def trataSerial( msgSerial):
    global ultimaTag
    global ultimaTensao
    comunicacao.enviarMensagem(msgSerial)
    if(not("Distancia" in msgSerial)):
        print(msgSerial)
        Motor().motorPode = False
    if ("RFID" in msgSerial):
        rfd = msgSerial.replace(" ","")
        splt = rfd.split(":")
        ultimaTag = splt[1]
    elif ("Monitor" in msgSerial):
        split = msgSerial.split(" ")
        ultimaTensao = int(split[1])
        r = Relatorio()
        r.gravar(split[1])
    elif ("ENC" in msgSerial):
        split = msgSerial.split(" ")
        split2 = split[1].split(".")
        Motor().rpm = int(split2[0])
        # elif("ENC" in msgSerial):
        #     print("ENC e distancia")
        #     _thread.start_new_thread(calculaDistancia, ())
    else:
        i = 0


############# NA FUNCCAO QUE TRATA AS MENSAGENS


#------------------------------------------------------------------------------

class Logica(Thread):
    def __init__(self):

        threading.Thread.__init__(self)

    def realizaInstrucao(self, instrucao):
        # global liberado
        global ultimaTag

        global instrucoes
        print("Realizando instrucao")
        if (instrucao.tagA != ultimaTag):
            print("adotando sentido")
            if (instrucao.peso == 1):
                Motor().sentido(True)
            else:
                Motor().sentido(False)
            print("bostona")
            Motor().alterarRPM(250, instrucao.tagB)
            print("Esperando por \t "+str(instrucao.tagB))
            print(ultimaTag)

            while not( instrucao.tagB in ultimaTag):
                o = 0
               # print(ultimaTag)

            print("acabou")
            #time.sleep(5)
            if (len(instrucoes) == 0):
                Motor().frenagem()
        #liberado = False
        return

        #


                # comunicacao.enviarMensagem(msgSerial)

    def run(self):
        print("Iniciando logica das instrucoes")
        global liberado
        while True:
            try:
                while(len(instrucoes)>0):
                    semaforoInstrucoes.acquire()
                    instrucao = instrucoes.pop()
                    semaforoInstrucoes.release()
                    self.realizaInstrucao(instrucao)


                liberado = True

            finally:
                p = 0


if(comunicacao.motor == Motor()):
    print("Singleton ta top")
else:
    print("Deu ruim o singleton")


#l = Logica()
#l.start()
#s = serialDistancia()
#s.start()
#cm = serial.Serial("/dev/ttyACM0", 9600)

print("Ta no final")
#while True:
#    msgSerial = cm.readline()
#    try:
#        msgSerial = msgSerial.decode()
#        trataSerial(msgSerial)
#    except: p=0

