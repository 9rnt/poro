import boto3
import botocore

def keyExists(o,k):
    if k in o:
        return o[k]
    else:
        return None

def getELB(log,session):
    log.info('[getELB] Start')
    # initialize ELB list
    publicLoadbalancers=[]
    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('elbv2')
    log.debug(f'[getELB] available regions: {available_regions}')
    for region in available_regions:    
        log.debug(f'[getELB] scanning in region: {region} ')
        try: 
            # get the list of ELB
            client = session.client('elbv2',region_name=region)
            response = client.describe_load_balancers()
            loadBalancers=response['LoadBalancers']
            log.debug(f'[getELB] loadBalancers list: {loadBalancers} ')
            
            # check if loadbalancer is internet facing
            for elb in loadBalancers:
                log.debug(f"[getELB] ELB data: {elb}")
                response=client.describe_target_groups(LoadBalancerArn=elb['LoadBalancerArn'])
                if elb['Scheme']=='internet-facing':
                    response=client.describe_target_groups(LoadBalancerArn=elb['LoadBalancerArn']).get('TargetGroups')     
                    targetGroups=[]
                    for tg in response:
                        targetGroups.append(tg.get('TargetGroupArn'))
                    publicLoadbalancers.append({
                        "service":"elbv2",
                        "resourceType":"loadbalancer",
                        "arn":elb['LoadBalancerArn'],
                        "dnsName":elb['DNSName'],
                        "region":region,
                        "securityGroups":keyExists(elb,'SecurityGroups'),
                        "targetGroupsArns":targetGroups,
                        "rational":"internet-facing"
                        }
                    )
        except botocore.exceptions.ClientError as e :
            log.info("[getELB] Unexpected error when scanning elbv2 in the region %s: %s" %(region, e.response['Error']['Message']))
    log.info('[getELB] End')
    return publicLoadbalancers

def getELBTags(log,session,elb):
    log.info('[getELBTags] Start')
    client=session.client('elbv2',region_name=elb["region"])
    try:
        response=client.describe_tags(ResourceArns=[elb["arn"]])
        log.debug(f"[getELBTags] tag response for {elb['arn']} is {response}")
        if response['TagDescriptions']:
            return response['TagDescriptions'][0]['Tags']
                
    except botocore.exceptions.ClientError as e :
        log.info(f'[getELBTags] unexpected error when looking for tag {e.response.get("Error")}')
        return None
