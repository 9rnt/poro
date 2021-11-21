import boto3
import botocore

# returns a list of publicly accessible EC2
# returns [{loadbalancer ARN:[loadbalancer dns, [attached security groups]]}]

def getELB():
    # initialize ELB list
    publicLoadbalancers=[]

    # get the list of ELB
    client = boto3.client('elbv2')
    response = client.describe_load_balancers()
    loadBalancers=response['LoadBalancers']
    
    for elb in loadBalancers:
        if elb['Scheme']=='internet-facing':
            publicLoadbalancers.append({elb['LoadBalancerArn']:[elb['DNSName'],elb['SecurityGroups']]})

    return publicLoadbalancers
