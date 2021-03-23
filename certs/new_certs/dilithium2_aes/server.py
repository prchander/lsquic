import os

myCmd = '/home/pi/oqs/lsquic/build/bin/./http_server -c www.example.com,key_crt.pem,key_srv.pem -s 10.0.0.200:4433'
os.system(myCmd)