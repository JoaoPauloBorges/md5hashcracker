import hashlib
import asyncio

def descobrirHash(arquivo, senhaTeste):
    arq = open(arquivo, 'r', errors="ignore")
    th = testarHash(senhaTeste)
    next(th)
    for senha in arq:
        th.send(senha.rstrip())

def testarHash(senhaTeste):
    try:
        while True:
            senha = (yield)
            hashSenha = hashlib.md5(senha.encode('utf-8')).hexdigest()
            if hashSenha == senhaTeste:
                print('Senha encontrada: {}'. format(senha))
                exit(0)
    except GeneratorExit:
        print('Senha nao encontrada!')
        exit(0)


senha = "$%COCACOLA"
arq = 'rockyou.txt'
teste = hashlib.md5(senha.encode('utf-8')).hexdigest()
descobrirHash(arq, teste)
