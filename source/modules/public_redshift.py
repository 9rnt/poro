import boto3
import botocore

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
                            publicClusters.append({
                                    "clusterId":cluster['ClusterIdentifier'],
                                    "region":region,
                                    "clusterEndpoint":cluster['Endpoint'],
                                    "service":"redshift",
                                    "resourceType":"cluster",
                                    "clusterArn":cluster['clusterArn']
                                })
    
                    for securitygroup in cluster['VpcSecurityGroups']:
                        SG=resource.SecurityGroup(securitygroup['VpcSecurityGroupId'])
                        sgIsPublic=False
                        for inbound in SG.ip_permissions:
                            for authorizedIps in inbound['IpRanges']:
                                if(authorizedIps['CidrIp'] in publicInbound):
                                    sgIsPublic=securitygroup['VpcSecurityGroupId']
                        if sgIsPublic:
                            publicClusters.append(
                                {
                                    "clusterId":cluster['ClusterIdentifier'],
                                    "region":region,
                                    "clusterEndpoint":cluster['Endpoint'],
                                    "service":"redshift",
                                    "resourceType":"cluster",
                                    "arn":cluster['clusterArn']
                                }
                            )

        except botocore.exceptions.ClientError as e:
            log.info("[listPublicCluster] Unexpected error when scanning Redshift in the region %s: %s" %(region, e.response['Error']['Message']))

    log.info("[listPublicCluster] End")
    return publicClusters

def getClusterTags(log,session,cluster):
    log.info('[getCLusterTags] Start')
    client=session.client('redshift',region_name=cluster["region"])
    try:
        response=client.describe_tags(ResourceName=cluster["arn"])
        return response['TaggedResources']
    except botocore.exceptions.ClientError as e :
        log.info(f'[list2Json] unexpected error when looking for tag {e.response.get("Error")}')
        return None