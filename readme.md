Aplicação para quebra de hashs via brute force
utilizando multiprocessos e processamento distribuído
com rabbitMQ, desenvolvida para a matéria de Sistemas Distribuídos da PUC-GO.

Para pesquisar por um hash via linha de comando são necessários executar os seguintes:
- minionRPC.py
- DataServer.py
- ao menos uma instância de minionWorker.py em alguma máquina com acesso ao ip onde está rodandno o DataServer.py

para pesquisar por um hash via web sào necessário executar:
 
- CliAndDataServer.py
- ao menos uma instância de minionWorker.py em alguma máquina com acesso ao ip onde está rodandno o CliAndDataServer.py

CliAndDataServer.py a DataServer.py
- para que os DataServers possam servir os arquivos, é necessário roda a primeira vez passando os argumentos de criação das wordlists. 
Para isso são necessários uma wordlist inicial completa.
Os argumentos para iniciar as wordlists sào: -initF true -file "caminhoParaWordlistInicial.txt"