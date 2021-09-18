from typing import NamedTuple, Union
import os
import sys
os.chdir("D:/GitHub/Analisador Lexico")

dataset = sys.argv[1]

ERRO = 0
IDENTIFICADOR = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4
FRASE = 5
RESERVADAS = 6
SEM_ATRIBUTOS = 7
OP_RELACIONAL = 8
OP_LOGICO = 9
PALAVRAS_RESERVADAS = ['ALGORITMO','ATE','CADEIA', 'CARACTER','ENQUANTO','ENTAO','FACA','FIM','FUNCAO','INICIO','INTEIRO','PARA','PASSO','PROCEDIMENTO','REAL','REF','RETORNE','SE','SENAO','VARIAVEL']
PALAVRAS_SEM_ATRIBUTOS = ['<-', '.', '(', ')', ';', ',', '-', '+', '*', '/', '%']
PALAVRAS_OP_RELACIONAL = ['<', '<=', '=', '<>', '>', '>=']
PALAVRAS_OP_LOGICO = ['&', '$', '|']
DICT_SEM_ATRIBUTOS = {'<-':'ATRIBUICAO', '.':'PONTO', '(':'ABRE_PAR', ')':'FECHA_PAR', ';':'PONTO_VIRGULA', ',':'VIRGULA', '-':'SUBTRACAO', '+':'ADICAO', '*':'MULTIPLICACAO', '/':'DIVISAO', '%':'RESTO'}
DICT_OP_RELACIONAL = {'<':'ME', '<=':'MEI', '=':'IG', '<>':'DI', '>':'MA', '>=':'MAI'}
DICT_OP_LOGICO = {'&':'E', '$':'OU', '|':'NEG'}

class Atomo(NamedTuple):
  tipo: str
  lexema: str
  valor: Union[int, float]
  linha: int


class Analisador_Lexico:
  def __init__(self, buffer):
    self.buffer = buffer + '\0'
    self.i = 0
    self.nlinha = 1

  def proximo_char(self):
     c = self.buffer[self.i]
     self.i += 1
     return c

  def retrair(self):
    self.i -= 1

  def tratar_identificador(self):
    lexema = self.buffer[self.i - 1]
    c = self.proximo_char()
    while (c.isalpha() or c.isdigit()):
      lexema = lexema + c
      c = self.proximo_char()
    self.retrair()
    if lexema.upper() in PALAVRAS_RESERVADAS:
      return Atomo('RESERVADAS', lexema.upper(), 0, self.nlinha)
    else:
      return Atomo('IDENTIFICADOR', lexema, 0, self.nlinha)

  def tratar_sem_atributos(self):
    lexema = self.buffer[self.i - 1]
    c = self.proximo_char()
    self.retrair()
    try:
      if lexema in PALAVRAS_SEM_ATRIBUTOS:
        return Atomo(DICT_SEM_ATRIBUTOS[lexema], lexema, 0, self.nlinha)
    except Exception:
      pass

  def tratar_relacional(self):
    lexema = self.buffer[self.i - 1]
    c = self.proximo_char()
    while (c in PALAVRAS_SEM_ATRIBUTOS):
      lexema = lexema + c
      c = self.proximo_char()
    self.retrair()
    if lexema in PALAVRAS_OP_RELACIONAL:
      return Atomo(DICT_OP_RELACIONAL[lexema], lexema, 0, self.nlinha)

  def tratar_logico(self):
    lexema = self.buffer[self.i - 1]
    c = self.proximo_char()
    while (c in PALAVRAS_SEM_ATRIBUTOS):
      lexema = lexema + c
      c = self.proximo_char()
    self.retrair()
    if lexema in PALAVRAS_OP_LOGICO:
      return Atomo(DICT_OP_LOGICO[lexema], lexema, 0, self.nlinha)

  def tratar_frase(self):
    lexema = self.buffer[self.i - 1]
    c = self.proximo_char()
    while (True):
      lexema = lexema + c
      if len(lexema)>0 and c=='\"':
        self.proximo_char()
        break
      c = self.proximo_char()
    self.retrair()
    return Atomo('FRASE', lexema, 0, self.nlinha)

  def tratar_numeros(self):
    lexema = self.buffer[self.i - 1]
    estado = 1
    c = self.proximo_char()

    while True:
      if estado == 1:
        if c.isdigit():
          lexema = lexema + c
          estado = 1
        elif c == '.':
          lexema = lexema + c
          estado = 3
        else:
          estado = 2
          continue
      elif estado == 2:
        self.retrair()
        return Atomo('NUM_INT', lexema, int(lexema), self.nlinha)
      elif estado == 3:
        if c.isdigit():
          lexema = lexema + c
          estado = 4
        else:
          return Atomo('ERRO', '', 0, self.nlinha)
      elif estado == 4:
        if c.isdigit():
          lexema = lexema + c
          estado = 4
        else:
          estado = 5
          continue
      elif estado == 5:
        self.retrair()
        return Atomo('NUM_REAL', lexema, float(lexema), self.nlinha)
      
      c = self.proximo_char()
  
  def tratar_excecao(self):
    lexema = self.buffer[self.i - 1]
    estado = 1
    c = self.proximo_char()
    self.retrair()
    return Atomo('EXCEÇÃO', lexema, 0, self.nlinha)

  def proximo_atomo(self):
    atomo = ERRO

    c = self.proximo_char()
    while c in [' ', '\t', '\n', '\0']:
      if c == '\n':
        self.nlinha = self.nlinha + 1
      if c == '\0':
        return Atomo(EOS, '', 0, self.nlinha)
      c = self.proximo_char()

    if c in PALAVRAS_SEM_ATRIBUTOS:  
      atomo = self.tratar_sem_atributos()
    elif c in PALAVRAS_OP_RELACIONAL:  
      atomo = self.tratar_relacional()
    elif c in PALAVRAS_OP_LOGICO:  
      atomo = self.tratar_logico()
    elif c.isalpha():  
      atomo = self.tratar_identificador()
    elif c.isdigit():  
      atomo = self.tratar_numeros()
    elif c == '\"':  
      atomo = self.tratar_frase()
    else:
      atomo = self.tratar_excecao()
    return atomo

def leia_arquivo():
  arquivo = open(dataset, 'r')
  buffer = arquivo.read()
  arquivo.close()
  return buffer

def main():
  buffer = leia_arquivo()
  lexico = Analisador_Lexico(buffer)
  msg_atomo = ['ERRO', 'IDENTIF', 'NUM_INT', 'NUM_REAL', 'EOS', 'FRASE', 'RESERVADAS', 'SEM ATRIBUTOS','RELACIONAL', 'LOGICO']
  atomo = lexico.proximo_atomo()
  while (atomo.tipo != ERRO and atomo.tipo != EOS):
    print('Linha: {}  - atomo: {} \t lexema: {}'.format(atomo.linha, atomo.tipo, atomo.lexema))
    atomo = lexico.proximo_atomo()

main()
