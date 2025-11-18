from urllib.request import urlopen

while True:
    for i in range(256):
        url=f"http://192.168.72.{i}:5000/whoami"
        try:
            data = urlopen(url, timeout=0.01).read().decode("utf-8")
            if data == "deadpool":
                print(url)
        except:
            pass