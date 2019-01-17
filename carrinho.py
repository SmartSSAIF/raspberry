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

ultimaTensao = 0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor
pinoMotorA = 17
pinoMotorB = 18
frequencia = 1000
pwmGlobal = 85

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

    def sentido(self, booleano):
        if (booleano != self.sentidoFrente):
            if (self.emMovimento):
                self.frenagem()
                print("freiou")
            else:
                print("aceleracao")
                # self.aceleracao()
        else:
            print("Sentido já inicializado")
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
        self.alterarPWM(0)
    def continuar(self):
        if(self.emMovimento):
            self.alterarPWM(pwmGlobal)

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
        global pwmGlobal
        if (not (Motor().sentidoFrente) == bool):
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


class USBEncoder(threading.Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global serialEncoder
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


class USBRFID(threading.Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global serialRFID
        while True:
            msg = serialRFID.readline().decode()
            print("Serial RFID: ", msg)


objEncoder = USBEncoder()
objRFID = USBRFID()


# encoder.start()
# rfid.start()

def inicializaSerial(caminho):
    global serialEncoder, objRFID, serialRFID, objEncoder
    try:
        auxiliar = serial.Serial(caminho, 9600)
        msg = auxiliar.readline().decode()

        if ("Iniciando encoder" in msg):
            print("Iniciando python serial ", msg)
            serialEncoder = auxiliar
            objEncoder.start()
        elif ("Iniciando RFID" in msg):
            print("Iniciando python serial ", msg)
            serialRFID = auxiliar
            objRFID.start()
        else:
            print("Erro no caminho: ", caminho)
    except Exception as e:
        print(str(e))


def inicializaComunicacaoSerial():
    for i in arange(0,10):
        inicializaSerial('/dev/ttyACM'+i)
    #inicializaSerial('/dev/ttyACM1')


inicializaComunicacaoSerial()
s = zerorpc.Server(HelloRPC())
s.bind("tcp://0.0.0.0:4242")
s.run()
