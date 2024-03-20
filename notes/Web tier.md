
connect to web tier

```
ssh -i ./CSE546_SSH_KEYS/ec2_key_pair.pem ec2-user@ec2-18-210-115-175.compute-1.amazonaws.com

source ./python3-virtualenv/bin/activate
cd Cloud_Computing_IaaS2/hchalla2
```

ERROR: fail to connect to public_ip:8000  
`pip install facenet-pytorch`



```
 uvicorn webtier2:app --host 127.0.0.1 --port 8000 --reload

```


linux instance
```
 uvicorn webtier:app --host 0.0.0.0 --port 8000
```

search for python3 process
```
ps aux | grep python3
```

