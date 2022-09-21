import boto3
import botocore

# returns a list of publicly accessible EC2
# returns [[DB Instance Identifier,[DB region,the attached public sg]]]

def listPublicDB(log,session):
    log.info("[listPublicDB] Start")
    publicInbound=['0.0.0.0/0','0.0.0.0/8','0.0.0.0/16','0.0.0.0/24','0.0.0.0/32','::/0','::/16','::/32','::/48','::/64']

    # Initializate public DB list
    publicDB=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('rds')

    # get RDS DBs list
    for region in available_regions:
        try:
            # get rds list in every region
            client = session.client('rds', region_name=region)
            localRDS = client.describe_db_instances()['DBInstances']
            for lRDS in localRDS:
                # check if RDS DB is publicly accessible
                if (lRDS['PubliclyAccessible']):
                    # check if the RDS DB is reachable from the internet through VPC SG or DB SG (some false positive may appear)
                    resource=session.resource('ec2', region_name=region)
                    for securitygroup in lRDS['DBSecurityGroups']:
                        SG=resource.SecurityGroup(securitygroup['DBSecurityGroupId'])
                        sgIsPublic=False
                        for inbound in SG.ip_permissions:
                            for authorizedIps in inbound['IpRanges']:
                                if(authorizedIps['CidrIp'] in publicInbound):
                                    sgIsPublic=securitygroup['DBSecurityGroupId']
                        if sgIsPublic:
                            publicDB.append([lRDS['DBInstanceIdentifier'],[region,sgIsPublic]])
                    for securitygroup in lRDS['VpcSecurityGroups']:
                        SG=resource.SecurityGroup(securitygroup['VpcSecurityGroupId'])
                        sgIsPublic=False
                        for inbound in SG.ip_permissions:
                            for authorizedIps in inbound['IpRanges']:
                                if(authorizedIps['CidrIp'] in publicInbound):
                                    sgIsPublic=securitygroup['VpcSecurityGroupId']
                        if sgIsPublic:
                            publicDB.append([lRDS['DBInstanceIdentifier'],[region,sgIsPublic]])

        except botocore.exceptions.ClientError as e :
            log.info("[listPublicDB] Unexpected error when scanning RDS in the region %s: %s" %(region, e.response['Error']['Message']))
    log.info("[listPublicDB] End")
    return publicDB