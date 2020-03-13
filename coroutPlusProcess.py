import multiprocessing as mp
import hashlib
import time

running_flag = mp.Value("i", 1)

def descobrirHash(running_flag, outq, arq, senhaTeste):
    th = testarHash(senhaTeste, running_flag, outq)
    next(th)
    for line in arq.splitlines():
        th.send(line)
    th.close()

def testarHash(senhaTeste, running_flag, outq):
    try:
        while True:
            line = (yield)
            hashSenha = hashlib.md5(line.encode('utf-8')).hexdigest()
            if hashSenha == senhaTeste:
                running_flag.value = 0
                print("achei")
                outq.put("Senha encontrada: " + line)
                break
    except GeneratorExit:
        return


def worker(running_flag, inq, outq):
    while True:
        data = inq.get()
        if running_flag.value != 0:
            running_flag.value = 3
            fn, arg = data
            fn(running_flag, outq, arg[0], arg[1])
            if running_flag.value != 0:
                running_flag.value = 1
        else:
            return

def queueDestruction(q):
    #precisa desse sleep pq se n vai rápido d+ e a queue fica doida
    time.sleep(0.01)
    while(not q.empty()):
        q.get()

if __name__ == '__main__':
    tasks = mp.Queue()
    results = mp.Queue()

    # Fase 01: Execução
    nCores = 4
    processos = []
    filename = "rockyou.txt"

    # teste = hashlib.md5('140332'.encode('utf-8')).hexdigest()
    teste = hashlib.md5("$%COCACOLA".encode('utf-8')).hexdigest()
    blocks = []  
    nLines = 0
    maxLines = 5000
    temp = ""

    # Criar e inicar os processos worker para executar as tarefas na fila de Tasks
    for i in range(nCores):
        processos.append(mp.Process(target=worker, args=(running_flag, tasks, results)))
    for prc in processos:
        prc.start()
    
    f = open(filename, 'r', errors="ignore")
    for line in f:
        if running_flag.value == 0:
            blocks.clear()

            queueDestruction(tasks)

            if (not tasks.empty or tasks.qsize() > 0):
                print("deu ruim: ")
                print(tasks.qsize())
            else:
                tasks.close()
                tasks.join_thread()
                break
        if nLines < maxLines:
            temp += line
            nLines += 1
        else:
            blocks.append(temp)
            temp = ""
            nLines = 0
            if len(blocks) == nCores:
                for block in blocks:
                    tasks.put((descobrirHash, (block, teste)))
                #precisa desse sleep pq se n vai rápido d+ e a queue fica doida
                # time.sleep(0.0001)
                blocks.clear()

    print("sai do for")
    print(tasks.qsize())
    if not tasks._closed:
        # if tasks.qsize() > 0 or not tasks.empty() or running_flag.value == 3:
        while tasks.qsize() > 0 and running_flag.value == 3:
            time.sleep(2)
        while tasks.qsize() > 0 or not tasks.empty():
            queueDestruction(tasks)
        tasks.close()
        tasks.join_thread()
    
    print("depois: ")
    print(tasks.qsize())

    for prc in processos:
        prc.terminate()
        prc.join()

    # Fase 02: Resultados
    if results.empty() or results.qsize() == 0:
        print("senha não encontrada")
        results.close()
        results.join_thread()
    else:
        print(results.get())