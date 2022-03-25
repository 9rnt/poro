import boto3
import botocore
import enlighten

# returns a list of publicly accessible EC2
# returns [[loadbalancer ARN,[loadbalancer dns, [attached security groups],region]]]

def getELB(log,session):
    log.info('[getELB] Start')
    # initialize ELB list
    publicLoadbalancers=[]
    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('elbv2')
    bar_format = '{desc}{desc_pad}{percentage:3.0f}%|{bar}| ' 
    manager = enlighten.get_manager()
    pbar = manager.counter(total=len(available_regions), desc=f'Scanning ELB: ', bar_format=bar_format) 
    log.info(f'[getELB] available regions: {available_regions}')
    for region in available_regions:    
        log.info(f'[getELB] scanning in region: {region} ')
        try: 
            # get the list of ELB
            client = session.client('elbv2',region_name=region)
            response = client.describe_load_balancers()
            loadBalancers=response['LoadBalancers']
            log.info(f'[getELB] loadBalancers list: {loadBalancers} ')
            
            # check if loadbalancer is internet facing
            for elb in loadBalancers:
                if elb['Scheme']=='internet-facing':
                    log.debug(f"[getELB] ELB data: {elb}")
                    publicLoadbalancers.append([elb['LoadBalancerArn'],[elb['DNSName'],elb['SecurityGroups'],region]])
        except botocore.exceptions.ClientError as e :
            log.info("[getELB] Unexpected error when scanning elbv2 in the region %s: %s" %(region, e.response['Error']['Message']))
        pbar.update(1)
    log.info('[getELB] End')
    return publicLoadbalancers
