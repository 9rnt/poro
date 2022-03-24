import boto3
import botocore

# returns a list of publicly Redshift databases
# return [ClusterIdentifier,[region,DBName,Endpoint,Public Security Group]]

def listPublicCluster(log,session):
    log.info("[listPublicCluster] Start")
    publicInbound=['0.0.0.0/0','0.0.0.0/8','0.0.0.0/16','0.0.0.0/24','0.0.0.0/32','::/0','::/16','::/32','::/48','::/64']

    # Initializate public clusters list
    publicClusters=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('redshift')

    for region in available_regions:
        try:
            # get redshift clusters in every region
            client=session.client('redshift',region_name=region)
            clusters=client.describe_clusters()['Clusters']
            for cluster in clusters:
                # check if the cluster is publicly accessible
                if cluster['PubliclyAccessible']:
                    # check if the VPC sg or the Cluster SG allows public connections
                    resource=session.resource('ec2',region_name=region)
                    for securitygroup in cluster['ClusterSecurityGroups']:
                        SG=resource.SecurityGroup(securitygroup['DBSecurityGroupId'])
                        sgIsPublic=False
                        for inbound in SG.ip_permissions:
                            for authorizedIps in inbound['IpRanges']:
                                if(authorizedIps['CidrIp'] in publicInbound):
                                    sgIsPublic=securitygroup['DBSecurityGroupId']
                        if sgIsPublic:
                            publicClusters.append([cluster['ClusterIdentifier'],[region,cluster['DBName'],cluster['Endpoint'],sgIsPublic]])
                    for securitygroup in cluster['VpcSecurityGroups']:
                        SG=resource.SecurityGroup(securitygroup['VpcSecurityGroupId'])
                        sgIsPublic=False
                        for inbound in SG.ip_permissions:
                            for authorizedIps in inbound['IpRanges']:
                                if(authorizedIps['CidrIp'] in publicInbound):
                                    sgIsPublic=securitygroup['VpcSecurityGroupId']
                        if sgIsPublic:
                            publicClusters.append([cluster['ClusterIdentifier'],[region,cluster['DBName'],cluster['Endpoint'],sgIsPublic]])

        except botocore.exceptions.ClientError as e:
            log.error("[listPublicCluster] Unexpected error when scanning Redshift in the region %s: %s" %(region, e.response['Error']['Message']))

    log.info("[listPublicCluster] End")
    return publicClusters
