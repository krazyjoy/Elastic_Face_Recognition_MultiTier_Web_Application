
- key location:
	- folder: `C:\Users\huang\CSE546_SSH_KEYS`
	- key: `CSE546_app_tier_key_pair.pem`
- SSH connection:
	`ssh -i ./CSE546_SSH_KEYS/CSE546_app_tier_key_pair.pem ubuntu@ec2-3-86-207-125.compute-1.amazonaws.com`

```
sudo apt-get update
sudo apt install python3.10-venv
python3 -m venv app-tier-venv
source ./app-tier-venv/bin/activate


(install deep-learning model)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

```

- virtual environment: `app-tier-venv`
- inference example:
```
(app-tier-venv) ubuntu@ip-172-31-87-219:~/project1-part2/model$ python face_recognition.py ../dataset/face_images_1000/test_000.jpg


============= RESULT ==============
Paul
```

- setup model and dataset for running instance
	```
	directory list
	===============================
	project1-part2
	|---- dataset
	|-------|---------face_images_1000/
	|---- model
	|-------|-------- data.pt
	|-------|---------face_recognition.py
	
	```
- create AMI from app tier ec2 instance

- connect to an app-tier-instance-#instance
- instance1
```
ssh -i ./CSE546_SSH_KEYS/CSE546_app_tier_key_pair.pem ubuntu@ec2-44-202-63-130.compute-1.amazonaws.com
```


linux instance:
![[run_systemctl.png]]
modify .service file `nano /etc/systemd/system/startup.service`
```
[Unit]
Description=Guicorn instance to run apptier
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/CSE546-Cloud-Computing/hchalla2
ExecStart=/usr/bin/python3 apptier.py
Restart=always
[Install]
WantedBy=multi-user.target





[Unit]
Description=Guicorn instance to run apptier
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/CSE546-Cloud-Computing
ExecStart=/home/ubuntu/app-tier-venv/bin/python apptier.py
Restart=always
[Install]
WantedBy=multi-user.target
```

```
sudo systemctl daemon-reload
sudo systemctl enable startup.service
sudo systemctl daemon-reload
sudo systemctl restart startup.service

```