import hashlib
# objetivo = "$%COCACOLA"
objetivo = "$%COCACOLA"
wordlist = 'rockyou.txt'
hashObjetivo = hashlib.md5(objetivo.encode('utf-8')).hexdigest()
arquivo = open(wordlist,'r', errors="ignore")
senha = arquivo.readline()
while senha:
    # print('Testando a senha: ' + senha)
    hashSenha = hashlib.md5(senha.rstrip().encode('utf-8')).hexdigest()
    # print ('=> {} ?'.format(hashSenha))
    if hashSenha == hashObjetivo:
        print ('Senha encontrada: {}'. format(senha))
        exit(0)
    senha = arquivo.readline()
print ('Senha nao encontrada!')
exit(0)