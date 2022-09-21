import boto3
import botocore

# returns a list of publicly accessible EC2
# returns [[instanceID:[instance public IP, public security group]]]

def listPublicEC2(log,session):
    log.info("[listPublicEC2] Start")
    publicInbound=['0.0.0.0/0','0.0.0.0/8','0.0.0.0/16','0.0.0.0/24','0.0.0.0/32','::/0','::/16','::/32','::/48','::/64']
    # Initialize ec2 list
    publicEC2=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('ec2')


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
                            publicEC2.append([instance.id,[region,instance.public_ip_address,sgIsPublic]])
        except botocore.exceptions.ClientError as e :
            log.info("[listPublicEC2] Unexpected error when scanning ec2 in the region %s: %s" %(region, e.response['Error']['Message']))

    log.info("[listPublicEC2] End")
    return publicEC2
