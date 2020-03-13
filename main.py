import multiprocessing as mp


def fib(n):
    if n <= 2:
        return 1
    elif n == 0:
        return 0
    elif n < 0:
        raise Exception('fib(n) is undefined for n < 0')
    return fib(n - 1) + fib(n - 2)


def worker(inq, outq):
    while True:
        data = inq.get()
        if data is None:
            return
        fn, arg = data
        outq.put(fn(arg))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=1)
    parser.add_argument('number', type=int, nargs='?', default=34)
    args = parser.parse_args()

    assert args.n >= 1, 'The number of threads has to be > 1'

    tasks = mp.Queue()
    results = mp.Queue()
    
    #Fase 01: Execução

    #Atribuir os valores das Tasks a serem executadas: função, argumento
    for i in range(args.n):
        tasks.put((fib, args.number))

    #Criar e inicar os processos worker para executar as tarefas na fila de Tasks
    for i in range(args.n):
        mp.Process(target=worker, args=(tasks, results)).start()

    #Fase 02: Resultados
    for i in range(args.n):
        print(results.get())
        
    #Fase 03: Finalização da execução
    for i in range(args.n):
       tasks.put(None)
