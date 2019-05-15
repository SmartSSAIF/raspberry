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

GPIO.setup(trigger1, GPIO.OUT)
GPIO.setup(echo1, GPIO.IN)
GPIO.setup(trigger2, GPIO.OUT)
GPIO.setup(echo2, GPIO.IN)

GPIO.setup(4, GPIO.OUT)

instrucoes = []
boleanoMotor = False
semaforoInstrucoes = threading.Semaphore()


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

    def zerar(self):
        global serialEncoder
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
        print("Setou pwm para ", valor)
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
    def recebeInstrucao(self, instrucao):
        global tagDeParada
        instrucao = json.loads(instrucao)
        tagDeParada = instrucao['destinoRfid']
        distancia = instrucao['distancia']
        print("Tag de parada ", tagDeParada)
        print("Distancia ", distancia)
        self.zerar()
        #self.setDistancia()
        # if(instrucao['peso'] == 1):
        #     self.pontoA()
        # else:
        #     self.pontoB()
        #print("Instrucao do servidor ", instrucao)
        #instrucoes.append(instrucao)
        #print('Tam ', len(instrucoes))


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
            print("Serial Encoder: ", msg)
            if ("Deslocou o valor desejado" in msg):
                print("Tem que parar")
                Motor().alterarPWM(0)
                Motor().setMovimento(False)
            elif("Sem obstaculo" in msg):
                Motor().continuar()
                print("Sem obstaculo, ligando motor")
            elif ("Obstaculo" in msg):
                Motor().pausar()
                print("Obstaculo no caminho")
            elif "Velocidade" in msg:
                encoderLocal = int(msg.replace("Velocidade:",""))
                print("Encoder local ", encoderLocal)
                #Motor().encoder += Motor().encoder +  
                encoderSaida = encoderLocal - Motor().encoder
                Motor().encoder = encoderLocal
                print("Valor do encoder ", encoderSaida)
                if encoderSaida >= 0:
                #encoderLocal = encoderLocal - Motor().encoder 
                    try:
                        print("Teste")
                        if not(Motor().emMovimento):
                            encoderSaida=0
                        
                        r = requests.post("http://192.168.10.99:3001/posicao", {'velocidade': encoderSaida, 'sentido' : int(Motor().sentidoFrente), 'tag': ultimaTag, 'novaTag': 0}, timeout = 1)
                        
                        
                    except Exception as e:
                        print("Error ", e)
            else:
                print("Else ", msg)
            print("Ok")

        print("Finalizou encoder")
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
                    Motor().alterarPWM(0)
                    Motor().setMovimento(False)
                obj = { 'tag' : s, 'novaTag' : 1, 'velocidade': 0}
                Motor().encoder2 = Motor().encoder +0
                print("Mensagem pro servidor ", obj)
                r = requests.post("http://192.168.10.99:3001/posicao", {'velocidade': 0, 'sentido' : int(Motor().sentidoFrente), 'tag': ultimaTag, 'novaTag': 1})

    def stop(self):
        self.continua = False
        print("Finalizando RFID", self.continua)
objEncoder = USBEncoder()
objRFID = USBRFID()


# encoder.start()
# rfid.start()

def inicializaSerial(caminho):
    global serialEncoder, objRFID, serialRFID, objEncoder
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
            objEncoder.start()
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

