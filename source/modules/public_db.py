import boto3
import botocore

def listPublicDB(log,session):
    log.info("[listPublicDB] Start")
    publicInbound=['0.0.0.0/0','0.0.0.0/8','0.0.0.0/16','0.0.0.0/24','0.0.0.0/32','::/0','::/16','::/32','::/48','::/64']

    # Initializate public DB list
    publicDB=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('rds')
    accountId=session.client('sts').get_caller_identity().get('Account')

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
                            publicDB.append(
                                {
                                    "instanceId":lRDS['DBInstanceIdentifier'],
                                    "arn":f"arn:aws:rds:{region}:{accountId}:db:{lRDS['DBInstanceIdentifier']}",
                                    "service":"rds",
                                    "resourceType":"instance",
                                    "region":region
                                }
                            )
                    for securitygroup in lRDS['VpcSecurityGroups']:
                        SG=resource.SecurityGroup(securitygroup['VpcSecurityGroupId'])
                        sgIsPublic=False
                        for inbound in SG.ip_permissions:
                            for authorizedIps in inbound['IpRanges']:
                                if(authorizedIps['CidrIp'] in publicInbound):
                                    sgIsPublic=securitygroup['VpcSecurityGroupId']
                        if sgIsPublic:
                            publicDB.append(
                                {
                                    "instanceId":lRDS['DBInstanceIdentifier'],
                                    "arn":f"arn:aws:rds:{region}:{accountId}:db:{lRDS['DBInstanceIdentifier']}",
                                    "service":"rds",
                                    "resourceType":"instance",
                                    "region":region
                                }
                            )

        except botocore.exceptions.ClientError as e :
            log.info("[listPublicDB] Unexpected error when scanning RDS in the region %s: %s" %(region, e.response['Error']['Message']))
    log.info("[listPublicDB] End")
    return publicDB


def getRdsInstanceTags(log,session,db):
    log.info(f'[getRdsInstanceTags] Start')
    client=session.client('rds',region_name=db["region"])
    try:
        response=client.list_tags_for_resource(ResourceName=db["arn"])
        return response['TagList']
    except botocore.exceptions.ClientError as e :
        log.info(f'[getRdsInstanceTags] unexpected error when looking for tag {e.response.get("Error")}')
        return None