import time

while True:
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(str(time.ctime()) + "\n")
    print(str(time.ctime()))
    time.sleep(1)