import multiprocessing as mp
import hashlib
import time

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
                print("I found it!!! " + mp.current_process()._name)
                outq.put("password found: " + line)
                running_flag.value = 0
                time.sleep(0.5)
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


def minion(h, filename, raw):
    mp.freeze_support()

    running_flag.value = 1

    nCores = 3
    process = []
    wantedHash = hashlib.md5(h.encode('utf-8')).hexdigest()
    nLines = 0
    maxLines = 50000
    temp = ""

    tasks = mp.Queue()
    results = mp.Queue()

    for _ in range(nCores):    
        prc = mp.Process(target=worker, args=(running_flag, tasks, results))
        process.append(prc)
        prc.start()

    if (raw): 
        f = filename.splitlines()
    else:
        f = open(filename, 'r', errors="ignore")

    for line in f:
        if running_flag.value == 0:
            break
        if nLines < maxLines:
            temp += line+'\n'
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
        # print('...killing remaining process')
        for prc in process:  
            prc.terminate()

    for prc in process:
        prc.join()

    if not results.empty():
        out = results.get()
    else:
        out = "password not found"
    print(out)
    
    if not tasks._closed:
        tasks.close()
    if not results._closed:
        results.close()
    return out


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-file', type=str, default='rockyou.txt')
    parser.add_argument('-hash', type=str, default='iloveyou')
    args = parser.parse_args()

    filename = args.file
    h = args.hash
    minion(h, filename, False)