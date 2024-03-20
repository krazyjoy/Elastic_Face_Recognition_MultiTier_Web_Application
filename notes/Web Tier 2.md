

```
ssh -i ./CSE546_Developer_Keys/CSE546_WebTier_Key_Pair.pem ec2-user@ec2-34-197-215-119.compute-1.amazonaws.com
```

- create virtual environment
```
python3 -m venv python3-virtualenv

source ./python3-virtualenv/bin/activate
```

- clone dataset, model ...


```
[Unit]
Description=Guicorn instance to run apptier
After=network.target
[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/CSE546-Cloud-Computing
ExecStart=/home/ec2-user/python3-virtualenv/bin/python webtier.py
Restart=always
[Install]
WantedBy=multi-user.target
```

- stop startup service
	- sudo systemctl disable startup.service
	- sudo systemctl stop startup.service


```
[Unit]
Description=Guicorn instance to run apptier
After=network.target
[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/CSE546-Cloud-Computing

[Install]
WantedBy=multi-user.target
```