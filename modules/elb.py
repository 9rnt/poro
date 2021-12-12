import boto3
import botocore

# returns a list of publicly accessible EC2
# returns [[loadbalancer ARN,[loadbalancer dns, [attached security groups]]]]

def getELB():
    # initialize ELB list
    publicLoadbalancers=[]
    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('elbv2')

    for region in available_regions:    
        try: 
            # get the list of ELB
            client = boto3.client('elbv2')
            response = client.describe_load_balancers()
            loadBalancers=response['LoadBalancers']
            
            # check if loadbalancer is internet facing
            for elb in loadBalancers:
                if elb['Scheme']=='internet-facing':
                    publicLoadbalancers.append([elb['LoadBalancerArn'],[elb['DNSName'],elb['SecurityGroups']]])
        except botocore.exceptions.ClientError as e :
            print("Unexpected error when scanning elbv2 in the region %s: %s" %(region, e.response['Error']['Message']))

    return publicLoadbalancers