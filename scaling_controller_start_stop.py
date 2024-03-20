import time
from config import *
import boto3

session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
)
sqs_client = session.client('sqs', region_name='us-east-1')
ec2_client = session.client('ec2', region_name='us-east-1')

ami_id = 'ami-0fd67e1495e09e341'
instance_type = 't2.micro'
keypair_name = 'CSE546-app-tier-key-pair'

running_app_instances = []


def start_instances(num_instances):

    instance_ids = []
    if num_instances <= 0:
        return instance_ids

    response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['app-tier-instance-*']}])
    count = 0
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']

            # total_states = ['pending', 'running', 'shutting-down', 'terminated', 'stopping']

            # if instance['State']['Name'] == 'stopped' or instance['State']['Name'] == 'stopping':
            if instance['State']['Name'] != 'running' and instance['State']['Name'] != 'terminated':
                ec2_client.start_instances(InstanceIds=[instance_id])
                instance_ids.append(instance_id)
                print(f'Started instance {instance_id}.')
                count += 1
                if count == num_instances:
                    print(f'Started {num_instances} instances.')
                    return instance_ids

    return instance_ids


def stop_instances():
    response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['app-tier-instance-*']}])
    cnt = 0
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            print(instance_id)
            print(instance['State']['Name'])
            if instance['State']['Name'] != 'stopped' and instance['State']['Name'] != 'terminated':
                ec2_client.stop_instances(InstanceIds=[instance_id])
                cnt += 1
                print(f'Stopped instance {instance_id}.')

    print(f'Stopped {cnt} instances.')


def get_stopping_instances_count():
    response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['app-tier-instance-*']}])
    stopping_count = 0
    stopping_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # stopping_ids.append(instance['InstanceId'])
            instance_state = instance['State']['Name']
            if instance_state == 'stopping':
                stopping_count += 1
    # print("stopping ids", stopping_ids)
    return stopping_count


def get_queue_length(queue_name):
    queue_url = f'https://sqs.us-east-1.amazonaws.com/637423581378/{queue_name}'

    response = sqs_client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
    )

    return int(response['Attributes']['ApproximateNumberOfMessages']) + int(
        response['Attributes']['ApproximateNumberOfMessagesNotVisible'])


def auto_scaling_controller():

    while True:

        in_cnt = 0
        queue_length = 0
        while in_cnt < 3:
            queue_length = get_queue_length('1229960136-req-queue')
            if queue_length == 0:
                in_cnt = 0
                time.sleep(1)
                continue
            in_cnt += 1


        while get_stopping_instances_count() != 0:
            time.sleep(1)
            print('waiting until all instances are stopped')
        start_instance_cnt = min(queue_length, 20)
        print('Starting : ', start_instance_cnt, ' instances')
        new_instance_ids = start_instances(start_instance_cnt)
        running_app_instances.extend(new_instance_ids)

        ter_cnt = 0
        while ter_cnt < 10:
            if get_queue_length('1229960136-req-queue') > 0 or get_queue_length('1229960136-resp-queue') > 0:
                ter_cnt = 0
                time.sleep(0.5)
                continue
            ter_cnt += 1

        while get_queue_length('1229960136-req-queue') != 0:
            time.sleep(0.5)

        stop_instances()
        while get_stopping_instances_count() != 0:
            time.sleep(1)

        print(f'All Instances Stopped, {get_stopping_instances_count()} instances in stopping state.')
        running_app_instances.clear()


if __name__ == "__main__":

    response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['app-tier-instance-*']}])
    cnt = 0
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            if instance['State']['Name'] == 'stopped':
                cnt+=1
    print(cnt)
    #
    #         if instance['State']['Name'] != 'running' and instance['State']['Name'] != 'terminated':
    #             print(instance_id)
    #             print(instance['State']['Name'])
    #             instances.append(instance_id)
    #             ec2_client.start_instances(InstanceIds=[instance_id])
    # print(len(instances))
    #
    # stop_instances()