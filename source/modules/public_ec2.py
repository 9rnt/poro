import boto3
import botocore

def listPublicEC2(log,session):
    log.info("[listPublicEC2] Start")
    publicInbound=['0.0.0.0/0','0.0.0.0/8','0.0.0.0/16','0.0.0.0/24','0.0.0.0/32','::/0','::/16','::/32','::/48','::/64']
    # Initialize ec2 list
    publicEC2=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('ec2')
    accountId=session.client('sts').get_caller_identity().get('Account')

    for region in available_regions:    
        # Get EC2 instances list
        resource=session.resource('ec2', region_name=region)
        try:
            instances=resource.instances.all()
            
            #check if the instance has a public IP address and that its reacheable from the internet
            for instance in instances:
                if instance.public_ip_address:
                    for sg  in instance.security_groups:
                        securityGroup=resource.SecurityGroup(sg['GroupId'])
                        sgIsPublic=False
                        for inbound in securityGroup.ip_permissions:
                            for authorizedIps in inbound['IpRanges']:
                                if(authorizedIps['CidrIp'] in publicInbound):
                                    sgIsPublic=sg['GroupId']
                        if sgIsPublic:
                            publicEC2.append(
                                {
                                    "instanceId":instance.id,
                                    "region":region,
                                    "publicIpAddress":instance.public_ip_address,
                                    "arn":f"arn:aws:ec2:{region}:{accountId}:instance/{instance.id}",
                                    "service":"ec2",
                                    "resourceType":"instance",
                                    "securityGroupId":sg['GroupId'],
                                    "securityGroupArn":f"arn:aws:ec2:{region}:{accountId}:security-group/{sg['GroupId']}"
                                }
                            )
        except botocore.exceptions.ClientError as e :
            log.info("[listPublicEC2] Unexpected error when scanning ec2 in the region %s: %s" %(region, e.response['Error']['Message']))

    log.info("[listPublicEC2] End")
    return publicEC2

def getEC2Tags(log,session,ec2):
    log.info(f'[getEC2Tags] Start')
    client=session.client('ec2',region_name=ec2["region"])
    try:
        response=client.describe_tags(Filters=[
            {
                'Name': 'resource-id',
                'Values': [
                    ec2["instanceId"],
                ]
            },
        ])
        return response['Tags']
            
    except botocore.exceptions.ClientError as e :
        log.info(f'[getEC2Tags] unexpected error when looking for tag {e.response.get("Error")}')
        return None