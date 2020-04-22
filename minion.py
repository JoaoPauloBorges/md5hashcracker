import multiprocessing as mp
import hashlib


running_flag = mp.Value("i", 1)

def descobrirHash(running_flag, outq, arq, wanted):
    th = testarHash(running_flag, wanted, outq)
    next(th)
    for line in arq.splitlines():
        th.send(line)
    th.close()

def testarHash(running_flag, wanted, outq):
    try:
        while True:
            line = (yield)
            hashTest = hashlib.md5(line.encode('utf-8')).hexdigest()
            if hashTest == wanted:
                # print("I found it!!! " + mp.current_process()._name)
                outq.put("password found: " + line)
                running_flag.value = 0
    except GeneratorExit:
        return


def worker(running_flag, inq, outq):
    while True:
        if not inq.empty():
            data = inq.get()
            if data == 'STOP':
                break
            fn, arg = data
            fn(running_flag, outq, arg[0], arg[1])


if __name__ == '__main__':

    nCores = 3
    process = []
    filename = "rockyou.txt"
    wantedHash = hashlib.md5("$%COCACOLA".encode('utf-8')).hexdigest()
    nLines = 0
    maxLines = 100000
    temp = ""

    tasks = mp.Queue()
    results = mp.Queue()

    for i in range(nCores):    
        prc = mp.Process(target=worker, args=(running_flag, tasks, results))
        process.append(prc)
        prc.start()

    with open(filename, 'r', errors="ignore") as f:
        for line in f:
            if running_flag.value == 0:
                break
            if nLines < maxLines:
                temp += line
                nLines += 1
            else:
                nLines = 0
                tasks.put((descobrirHash, (temp, wantedHash)))
                temp = ""

    if running_flag.value != 0:
        tasks.put((descobrirHash, (temp, wantedHash)))
        # print("end of file reached... tasks remaining: " + str(tasks.qsize()))
        for prc in process:
            tasks.put('STOP')
    else:
        print('...killing remaining process')
        for prc in process:  
            prc.terminate()

    for prc in process:
        prc.join()

    if not results.empty():
        print(results.get())
    else:
        print("password not found")
