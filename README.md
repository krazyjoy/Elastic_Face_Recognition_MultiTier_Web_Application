## Elastic Face Recognition Application IaaS

command for generating workload images

```angular2html
python ./workload_generator.py --num_request 1 --url 'http://34.197.215.119:8000' --image_folder "./dataset/face_images_1000/" --prediction_file './dataset/classification_results_1000.csv'
```



### Web Tier: ip (`34.197.215.119:8000`)
1. use FastAPI to run `uvicorn.run(app=app, host="0.0.0.0", port=8000, lifespan="on")`
    <br> a. post request handler accepts image objects and decode image bytes to string, <br>
   forward dictionary of `{'image-name': 'image-string'}` to request queue
2. use threading to open a new thread, this thread listens to the response queue to see if any result was sent back
    <br> a. store the result in a global dictionary `filename_output_map `
    <br> b. the fetch output function inside the post request handler looks into the map to find corresponding image result to allow asynchronous process
3. use threading to open a new thread, this thread supports auto-scaling number of webtiers based on request queue's length

### App Tier
1. use facenet to perform inference on the images that are waiting in request queue,
2. store `{'image-name.jpg': 'image object'}` in S3 `in-bucket`, store `{'image-name': 'prediction_person_name'}`
in S3 `out-bucket`
3. send back prediction to response queue

- create environment
    ```angular2html
    sudo apt-get update
    sudo apt install python3.10-venv
    python3 -m venv app-tier-venv
    source ./app-tier-venv/bin/activate
    
    
    (install deep-learning model)
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    
    ```
  
- execute
    `python apptier.py`
- run in background
    - modify .service file `nano /etc/systemd/system/startup.service`
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
    ```
- reload files and start service
    ```angular2html
    sudo systemctl daemon-reload
    sudo systemctl enable startup.service
    sudo systemctl restart startup.service
    ```
  
- disable startup service
    ```angular2html
    sudo systemctl disable startup.service
    sudo systemctl stop startup.service
    ```
  

### Auto-scaling

- Mechanism
  1. create 20 ec2 instances in stopped state and name them with prefix `app-tier-instance-` + `#`
  2. as post request comes in to the request queue, the number of requests remain fluctuating, the `in_cnt` waits for three iteration, until the number goes stable
  3. the `start_instance_cnt = min(queue_length, 20)` makes sure the number of instances started is below the created number of instances
  4. the `ter_cnt` waits 10 iteration, until the both queue has no more messages, then start to stop the instances

