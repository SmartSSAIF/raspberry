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
import requests
import json
import asyncio
import websockets

ultimaTensao = 0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor
pinoMotorA = 17
pinoMotorB = 18
frequencia = 1000
pwmGlobal = 50

GPIO.setup(pinoMotorA, GPIO.OUT)
GPIO.setup(pinoMotorB, GPIO.OUT)

pwm1 = GPIO.PWM(pinoMotorA, frequencia)
pwm2 = GPIO.PWM(pinoMotorB, frequencia)
pwm1.start(0)
pwm2.start(0)

# Arduino RFID
ultimaTag = ""
serialRFID = ""
objRFID = ""
trocouTAG = False
tagDeParada = ""

# Arduino Encoder
serialEncoder = ""
objEncoder = ""
trigger1 = 25
echo1 = 13
echo2 = 6
trigger2 = 5


# Instrucao Gambiarra 

proximaInstrucao = False

GPIO.setup(trigger1, GPIO.OUT)
GPIO.setup(echo1, GPIO.IN)
GPIO.setup(trigger2, GPIO.OUT)
GPIO.setup(echo2, GPIO.IN)

GPIO.setup(4, GPIO.OUT)

boleanoMotor = False
semaforoInstrucoes = threading.Semaphore()

loop = asyncio.new_event_loop()


# class serialDistancia(Thread):

instrucoes = []

class Instrucao():
    def __init__(self, tagA, tagB, angulo, peso, prioridade=1):
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
        self.rpm = 0
        self.zerarValores()
        self.valorPWMAtual = 0
        self.emMovimento = False
        self.fimDeCurso = True
        self.encoder = 0
        self.encoder2 = 0

    def sentido(self, booleano):
        if (booleano != self.sentidoFrente):
            if (self.emMovimento):
                self.frenagem()
                print("freiou")
            else:
                print("aceleracao")
                # self.aceleracao()
        else:
            print("Sentido j? inicializado")
        self.sentidoFrente = booleano

    def setMovimento(self, valor):
        self.emMovimento = valor
    def alterarRPM(self, valor, tagDestino):
        global ultimaTag
        print("saiu for")
        # time.sleep(10)
        print("vai while")
        while self.rpm < valor and self.valorPWMAtual < 100 and not (ultimaTag in tagDestino) and self.motorPode:
            print(self.valorPWMAtual)
            self.valorPWMAtual += 1
            self.alterarPWM(self.valorPWMAtual)
            time.sleep(0.1)

        print("PWM " + str(self.valorPWMAtual) + " RPM " + str(self.rpm))

    def zerarValores(self):
        global pwm1
        global pwm2
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)

    def alterarPWM(self, valor):
        global pwm1
        global pwm2
        self.valorPWMAtual = valor
        # print("Sentido ",self.sentidoFrente)
        if (self.sentidoFrente):
            pwm1.ChangeDutyCycle(valor)
        else:
            pwm2.ChangeDutyCycle(valor)

    def aceleracao(self):
        for i in range(0, 100, 1):
            if (self.rpm < 250):
                self.alterarPWM(i)
                time.sleep(0.001)

    def frenagem(self):
        for i in range(int(self.valorPWMAtual), 0, -1):
            self.alterarPWM(i)
            time.sleep(0.001)
            self.zerarValores()
    def pausar(self):
        Motor().alterarPWM(0)
    def continuar(self):
        global pwmGlobal
        if(self.emMovimento):
            print("pwm ligando ", pwmGlobal)
            Motor().aceleracao()
            Motor().alterarPWM(pwmGlobal)

Motor().iniciar()



class EnviaEncoder(object):
    def pontoA(self):
        print("Ponto A")
        self.executa(False)

    def pontoB(self):
        print("Ponto B")
        self.executa(True)

    def setDistancia(self, valor):
        print("Set distancia ", valor)
        global serialEncoder
        saida = "Distancia " + str(valor)
        serialEncoder.write(saida.encode())

    def setUltrassom(self, valor):
        global serialEncoder
        saida = "Ultrassom " + str(valor)
        serialEncoder.write(saida.encode())

    def confirmaPedido(self):
        global proximaInstrucao
        proximaInstrucao = True
        print("Confirmou proxima instrucao")


    def zerar(self):
        global serialEncoder
        # print('Zerou ')
        msg = "Zerar\n"
        serialEncoder.write(msg.encode())

    def executa(self, bool):
        Motor().encoder = 0
        global pwmGlobal
        #if (not (Motor().sentidoFrente) == bool):
        print("ta aqui ")
        Motor().sentido(bool)
        Motor().aceleracao()
        Motor().alterarPWM(pwmGlobal)
        Motor().setMovimento(True)
        print("acabou if")

    def setPWM(self, valor):
        global pwmGlobal
        # print("Setou pwm para ", valor)
        try:
            pwmGlobal = float(valor)
        except e:
            print("erro na conversao Pwm")
            print(e)
        print("setou pwm")


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
        print("Set distancia ", valor)
        global serialEncoder
        saida = "Distancia " + str(valor)
        serialEncoder.write(saida.encode())

    def setUltrassom(self, valor):
        global serialEncoder
        saida = "Ultrassom " + str(valor)
        serialEncoder.write(saida.encode())

    def confirmaPedido(self):
        global proximaInstrucao
        proximaInstrucao = True
        print("Confirmou proxima instrucao")


    def zerar(self):
        global serialEncoder
        # print('Zerou ')
        msg = "Zerar\n"
        serialEncoder.write(msg.encode())

    def executa(self, bool):
        Motor().encoder = 0
        global pwmGlobal
        #if (not (Motor().sentidoFrente) == bool):
        print("ta aqui ")
        Motor().sentido(bool)
        Motor().aceleracao()
        Motor().alterarPWM(pwmGlobal)
        Motor().setMovimento(True)
        print("acabou if")

    def setPWM(self, valor):
        global pwmGlobal
        # print("Setou pwm para ", valor)
        try:
            pwmGlobal = float(valor)
        except e:
            print("erro na conversao Pwm")
            print(e)
        print("setou pwm")

    def setTime(self, valor):
        global tempoCaminho
        print("Setou tempo para ", valor)
        try:
            tempoCaminho = float(valor)
        except e:
            print("erro na conversao Time")
            print(e)

    def setPercurso(self, valor):
        print("comunicacao usb")
        com = serialDistancia()
    def recebeInstrucao(self, serverInstrucoes):
        global tagDeParada
        global serialEncoder
        global proximaInstrucao
        global instrucoes
        for i in serverInstrucoes:
            if "peso" in i: 
                instrucoes.append(i)
        print('\t\t\t\t\t antes for')
 
        #self.setDistancia()
        # if(instrucao['peso'] == 1):
        #     self.pontoA()
        # else:
        #     self.pontoB()
        #print("Instrucao do servidor ", instrucao)
        #instrucoes.append(instrucao)
        #print('Tam ', len(instrucoes))




def mandaNotificacao(msg, destinoPage):
    print("Fazendo notificacao")
    url = "https://fcm.googleapis.com/fcm/send"
    payload = "{\r\n \"to\" : \"ettR9Jmqqlg:APA91bHrdMTWf2x8GlEtqQztuX4eyiibO8z6eElAmmR8LMJMZTPuDGvDQX_LAdd-0XfE9AvKnhepDAsoCQK1Tu2J24Ry1GO5S5nnMQ_gjbX6fwN3Sz-FvhF4zeY5PXfg0zXRuYnIWTqh\",\r\n \"collapse_key\" : \"type_a\",\r\n \"notification\" : {\r\n     \"body\" : \" " + msg +"\",\r\n     \"title\": \"THAS\",\r\n     \"sound\": \"default\"\r\n },\r\n \"data\" : { \r\n \t \"click_action\": \"FLUTTER_NOTIFICATION_CLICK\",\r\n     \"body\" : \"Body of Your Notification in Data\",\r\n     \"title\": \"Title of Your Notification in Title\",\r\n     \"key_1\" : \"Value for key_1\",\r\n     \"key_2\" : \"Value for key_2\",\r\n     \"status\": \"done\",\r\n     \"screen\": \"" +destinoPage +" \"\r\n }\r\n}"
    headers = {
    'Authorization': "key=AAAArpJIlpQ:APA91bEzVdxHZTC4sJV0Jy4LTvFw_DRZS79Rtkl_oar19rRQ2p4KAdeyDWYviof22roX4fQF3Y-DoneBdM-ONpimyIvO4QTWUOyarewyMJ3ByCfSfV_Q_ObawB0v0e0BgNZnzw7PQfUS",
    'Content-Type': "application/json",
    'User-Agent': "PostmanRuntime/7.13.0",
    'Accept': "/",
    'Cache-Control': "no-cache",
    'Postman-Token': "43669051-114d-4d9b-adc9-f893859aa45a,90119e72-c037-4929-802e-c49728858e29",
    'Host': "fcm.googleapis.com",
    'accept-encoding': "gzip, deflate",
    'content-length': "613",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print("Response" ,response)
    print("Status", response.status_code)
    print("Saida notificacao ", response.text)


def encoder(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(web())

async def web():
        async with websockets.connect("ws://192.168.10.100:5010") as ws:
            global serialEncoder
            global ultimaTag
            global trocouTAG
            contador =0
            while True:
                velocidade = 0
                msg = serialEncoder.readline().decode()
                # print("Serial Encoder: ", msg)
                if ("Deslocou o valor desejado" in msg):
                    print("Tem que parar")
                    # Motor().alterarPWM(0)
                    # Motor().setMovimento(False)
                elif("Sem obstaculo" in msg):
                    Motor().continuar()
                    print("Sem obstaculo, ligando motor")
                elif ("Obstaculo" in msg):
                    Motor().pausar()
                    print("Obstaculo no caminho")
                elif "Zerando contador" in msg:
                    print("Zerou contador")
                elif "Velocidade" in msg:
                    encoderLocal = int(msg.replace("Velocidade:",""))
                    # print("Encoder local ", encoderLocal)
                    #Motor().encoder += Motor().encoder +  
                    encoderSaida = encoderLocal - Motor().encoder
                    Motor().encoder = encoderLocal
                    # print("Valor do encoder ", encoderSaida)
                    if encoderSaida >= 0:
                    #encoderLocal = encoderLocal - Motor().encoder 
                        try:
                            # print("Teste")
                            if not(Motor().emMovimento):
                                encoderSaida=0
                            saida = {'velocidade': encoderSaida, 'sentido' : int(Motor().sentidoFrente), 'tag': ultimaTag, 'novaTag': 0}
                            ws.send(saida)
                            #r = requests.post("http://192.168.10.100:3001/posicao", {'velocidade': encoderSaida, 'sentido' : int(Motor().sentidoFrente), 'tag': ultimaTag, 'novaTag': 0}, timeout = 0.5)
                        except Exception as e:
                            print("Error ", e)
                else:
                    pass
                    # print("Else ", msg)
                # print("Ok")

            print("Finalizou encoder")
            serialEncoder.close()


class ExecutaInstrucao(threading.Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global proximaInstrucao
        global instrucoes
        global tagDeParada
        enviarNotificacao = False
        while True:
            for instrucao in instrucoes:
                enviarNotificacao = True
                instrucao = json.loads(instrucao)
                EnviaEncoder().zerar()
                print('Instrucao ', instrucao)
                tagDeParada = instrucao['rfid']
                distancia = instrucao['distancia']
                print(" vai ser Tag de parada ", tagDeParada)
                print("Distancia ", distancia)
                EnviaEncoder().setDistancia(distancia)
                proximaInstrucao = False
                if "peso" in instrucao.keys(): 
                    if instrucao['peso'] == 1:
                        print('Pra frente')
                        EnviaEncoder().pontoA()
                    else:
                        print("Pra tras")
                        EnviaEncoder().pontoB()
                    while Motor().emMovimento:
                        time.sleep(2)
                    print("Finalizou instrucao")
                    EnviaEncoder().zerar()
                if instrucao['isFinal'] = 1:
                    r = requests.post("http://192.168.10.100:3001/fimDeInstrucao", {'acabou ': 0})
                    #mandaNotificacao("Um pedido foi realizado", "/pedido/" + str(instrucao['pedido']))
                    while proximaInstrucao == False:
                        time.sleep(2)
            if enviarNotificacao == True:
                r = requests.post("http://192.168.10.100:3001/fimDeInstrucao", {'acabou ': 1})
                #mandaNotificacao("Seu pedido foi finalizado.", "home")
                enviarNotificacao = False
            time.sleep(1)

executa = ExecutaInstrucao()
executa.start()



class USBEncoder(threading.Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continua = True
    def run(self):
        self.velocidade = 0
        global serialEncoder
        global ultimaTag
        global trocouTAG
        self.contador =0
        while True:
            msg = serialEncoder.readline().decode()
            # print("Serial Encoder: ", msg)
            if ("Deslocou o valor desejado" in msg):
                print("Tem que parar")
                # Motor().alterarPWM(0)
                # Motor().setMovimento(False)
            elif("Sem obstaculo" in msg):
                Motor().continuar()
                print("Sem obstaculo, ligando motor")
            elif ("Obstaculo" in msg):
                Motor().pausar()
                print("Obstaculo no caminho")
            elif "Zerando contador" in msg:
                print("Zerou contador")
            elif "Velocidade" in msg:
                encoderLocal = int(msg.replace("Velocidade:",""))
                # print("Encoder local ", encoderLocal)
                #Motor().encoder += Motor().encoder +  
                encoderSaida = encoderLocal - Motor().encoder
                Motor().encoder = encoderLocal
                # print("Valor do encoder ", encoderSaida)
                if encoderSaida >= 0:
                #encoderLocal = encoderLocal - Motor().encoder 
                    try:
                        # print("Teste")
                        if not(Motor().emMovimento):
                            encoderSaida=0
                        
                        r = requests.post("http://192.168.10.100:3001/posicao", {'velocidade': encoderSaida, 'sentido' : int(Motor().sentidoFrente), 'tag': ultimaTag, 'novaTag': 0}, timeout = 0.5)
                        
                        
                    except Exception as e:
                        print("Error ", e)
            else:
                pass
                # print("Else ", msg)
            # print("Ok")

        # print("Finalizou encoder")
        serialEncoder.close()
    def stop(self):
        self.continua = False
        print("Funcao stop ", self.continua)

class USBRFID(threading.Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continua = True
    def run(self):
        global serialRFID
        global ultimaTag
        global trocouTAG
        global tagDeParada
        while self.continua:
            msg = serialRFID.readline().decode()
           # print("Serial RFID: ", msg)
            if "RFID" in msg:
                print("Serial RFID: ", msg)
                s = msg.replace("RFID:","").replace("\r\n", "")
                ultimaTag = s

                if(s == tagDeParada):
                    print('Tag de parada ',tagDeParada)
                    Motor().alterarPWM(0)
                    Motor().setMovimento(False)
                obj = { 'tag' : s, 'novaTag' : 1, 'velocidade': 0}
                Motor().encoder2 = Motor().encoder +0
                print("Mensagem pro servidor ", obj)
                r = requests.post("http://192.168.10.100:3001/posicao", {'velocidade': 0, 'sentido' : int(Motor().sentidoFrente), 'tag': ultimaTag, 'novaTag': 1})

    def stop(self):
        self.continua = False
        print("Finalizando RFID", self.continua)
objEncoder = USBEncoder()
objRFID = USBRFID()


# encoder.start()
# rfid.start()

def inicializaSerial(caminho):
    global serialEncoder, objRFID, serialRFID, objEncoder, loop
    try:
        auxiliar = serial.Serial(caminho, 9600, timeout = 2)
        msg = auxiliar.readline().decode()
        print('Msg:',msg,'Caminho:',caminho)

        if ("Iniciou" in msg):
            print("Iniciando python serial ", msg)
            serialRFID = auxiliar
            objRFID.start()
        else:
            print("Iniciando python serial ", msg)
            serialEncoder = auxiliar
            #objEncoder.start()
            t = Thread(target = encoder, args=(loop,))
            t.start()

    except Exception as e:
        print(str(e))


def inicializaComunicacaoSerial():
    for i in range(0,10):
        inicializaSerial('/dev/ttyACM'+str(i))
    #inicializaSerial('/dev/ttyACM1')

try:
    inicializaComunicacaoSerial()
    s = zerorpc.Server(HelloRPC())
    s.bind("tcp://0.0.0.0:4242")
    s.run()
except KeyboardInterrupt:
    try:
        #serialEncoder.close()
        objEncoder.stop()
        #serialRFID.close()
    except Exception as e:
        print(e)
    sys.exit()

