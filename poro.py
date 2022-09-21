from modules.public_buckets import listPublicBuckets
from modules.public_api import *
from modules.public_ec2 import listPublicEC2
from modules.elb import *
from modules.public_db import listPublicDB
from modules.public_redshift import listPublicCluster
import logging
import argparse
import boto3
import datetime
import botocore


def list2Json(log,session,buckets,apis,ec2s,elbs,dbs,clusters,**kwarg):
    log.info(f'[list2Json] Start')
    key=kwarg.get('key',None)
    value=kwarg.get('value',None)
    log.info(f'[list2Json] tag is {key}:{value}')
    export={
        "Public buckets":[],
        "Public API":[],
        "Public EC2":[],
        "Public ELB":[],
        "Public RDS":[],
        "Public Redshift clusters":[]
    }
    try:
        account_id=session.client('sts').get_caller_identity().get('Account')
    except botocore.exceptions.ClientError as e :
        log.info(f'[list2Json] unexpected error when getting accoun id {e.response.get("Error")}')
                
    if buckets:
        for bucket in buckets:
            if key:
                client = session.client('s3')
                bucket_tag=False
                try:
                    response = client.get_bucket_tagging(Bucket=bucket[0])
                    for tag in response['TagSet']:
                        if tag['Key']==key:
                            if tag['Value']==value:
                                bucket_tag=True
                except botocore.exceptions.ClientError as e :
                    log.info(f'[list2Json] unexpected error when looking for tag {e.response.get("Error")}')
                export["Public buckets"].append({
                    "Name":bucket[0],
                    "is Tagged":bucket_tag,
                    "Rational":bucket[1]
                })
            else:
                export["Public buckets"].append({
                    "Name":bucket[0],
                    "Rational":bucket[1]
                })
    if apis:
        for api in apis:
            if key:
                client=session.client('resourcegroupstaggingapi',region_name=api[1])
                api_tag=False
                try:
                    api_arn='arn:aws:apigateway:us-west-2::/apis/'+api[0]
                    response=client.get_resources(ResourceARNList=[api_arn])
                    log.info(f"[list2Json] tag response for {api_arn} is {response}")
                    if response['ResourceTagMappingList']:
                        for tag in response['ResourceTagMappingList'][0]['Tags']:
                            if tag['Key']==key:
                                if tag['Value']==value:
                                    api_tag=True
                except botocore.exceptions.ClientError as e :
                    log.info(f'[list2Json] unexpected error when looking for tag {e.response.get("Error")}')
                export["Public API"].append({
                    "ID":api[0],
                    "Name":api[3],
                    "Region":api[1],
                    "is Tagged":api_tag,
                    "Endpoints":api[2]
                })
            else:
                export["Public API"].append({
                    "ID":api[0],
                    "Region":api[1],
                    "Endpoints":api[2]
                })
    if ec2s:
        for ec2 in ec2s:
            if key:
                ec2_tag=False
                client=session.client('ec2',region_name=ec2[1][0])
                try:
                    response=client.describe_tags(Filters=[
                        {
                            'Name': 'resource-id',
                            'Values': [
                                ec2[0],
                            ]
                        },
                    ])
                    log.info(f"[list2Json] tags for {ec2[0]} are {response['Tags']}")
                    for tag in response['Tags']:
                            if tag['Key']==key:
                                if tag['Value']==value:
                                    ec2_tag=True
                except botocore.exceptions.ClientError as e :
                    log.info(f'[list2Json] unexpected error when looking for tag {e.response.get("Error")}')
                export["Public EC2"].append({
                    "ID":ec2[0],
                    "Region":ec2[1][0],
                    "Public IP":ec2[1][1],
                    "is Tagged":ec2_tag,
                    "Security group":ec2[1][2]
                })
            else:
                export["Public EC2"].append({
                    "ID":ec2[0],
                    "Region":ec2[1][0],
                    "Public IP":ec2[1][1],
                    "Security group":ec2[1][2]
                })
    if elbs:
        for elb in elbs:
            if key:
                client=session.client('elbv2',region_name=elb[1][3])
                elb_tag=False
                try:
                    response=client.describe_tags(ResourceArns=[elb[0]])
                    log.info(f"[list2Json] tag response for {elb[0]} is {response}")
                    if response['TagDescriptions']:
                        for tag in response['TagDescriptions'][0]['Tags']:
                            if tag['Key']==key:
                                if tag['Value']==value:
                                    elb_tag=True
                except botocore.exceptions.ClientError as e :
                    log.info(f'[list2Json] unexpected error when looking for tag {e.response.get("Error")}')
                export["Public ELB"].append({
                    "ARN":elb[0],
                    "DNS":elb[1][0],
                    "Region":elb[1][3],
                    "Security groups":elb[1][1],
                    "Target Groups":elb[1][2],
                    "is tagged":elb_tag
                })
            else:
                export["Public ELB"].append({
                    "ARN":elb[0],
                    "DNS":elb[1][0],
                    "Region":elb[1][2],
                    "Security groups":elb[1][1]
                })
    if dbs:
        for db in dbs:
            if key:
                client=session.client('rds',region_name=db[1][0])
                rds_tag=False
                try:
                    db_arn=f'arn:aws:rds:{db[1][0]}:{account_id}:db:{db[0]}'
                    response=client.list_tags_for_resource(ResourceName=db_arn)
                    log.info(f"[list2Json] tag response for {db[0]} is {response}")
                    if response['TagList']:
                        for tag in response['TagList']:
                            if tag['Key']==key:
                                if tag['Value']==value:
                                    rds_tag=True
                except botocore.exceptions.ClientError as e :
                    log.info(f'[list2Json] unexpected error when looking for tag {e.response.get("Error")}')
                export["Public RDS"].append({
                "ID":db[0],
                "Region":db[1][0],
                "Security groups":elb[1][1],
                "is tagged":rds_tag
            })
            else:
                export["Public RDS"].append({
                "ID":db[0],
                "Region":db[1][0],
                "Security groups":elb[1][1]
            })
            
    if clusters:
        for cluster in clusters:
            if key:
                rs_tag=False
                client=session.client('redshift',region_name=ec2[1][0])
                try:
                    rs_arn=f'arn:aws:redshift:{cluster[1][0]}:{account_id}:cluster:{cluster[0]}'
                    response=client.describe_tags(ResourceName=rs_arn)
                    log.info(f"[list2Json] tags for {cluster[0]} are {response['TaggedResources']}")
                    if response['TaggedResources']:
                        for tag in response['TaggedResources']['Tag']:
                            if tag['Key']==key:
                                if tag['Value']==value:
                                    rs_tag=True
                except botocore.exceptions.ClientError as e :
                    log.info(f'[list2Json] unexpected error when looking for tag {e.response.get("Error")}')
                export["Public Redshift clusters"].append({
                    "ID":cluster[0],
                    "Region":cluster[1][0],
                    "DB Name":cluster[1][1],
                    "Endpoint":cluster[1][2],
                    "Security group":cluster[1][3],
                    "is tagged":rs_tag
                })
            else:                
                export["Public Redshift clusters"].append({
                    "ID":cluster[0],
                    "Region":cluster[1][0],
                    "DB Name":cluster[1][1],
                    "Endpoint":cluster[1][2],
                    "Security group":cluster[1][3]
                })

    return export

def main():
    global done
    logging.basicConfig(format="%(levelname)s: %(message)s")
    log = logging.getLogger()
    
    parser = argparse.ArgumentParser(description="Scans publicly exposed assets in AWS environment.")
    # parse arguments
    parser.add_argument('--profile', dest='profile',default='default', help='Specify the aws profile (default is default)')
    parser.add_argument('--export', dest='file_name', help='Specify the file name if you want to expport the results')
    parser.add_argument('--verbose', '-v', dest='verbose', action='count', default=0)
    parser.add_argument('--tag-key', dest='key', help='Specify the tag key that you want to check if it exists in public resources')
    parser.add_argument('--tag-value', dest='value', help='Specify the tag value that you want to check if it exists in public resources')
    args = parser.parse_args()

    # set verbose level
    log_level=[
        'ERROR',
        'WARNING',
        'INFO',
        'DEBUG'
    ]
    if args.verbose>3:
        verbose=3
    else:
        verbose=args.verbose
    log.setLevel(log_level[verbose])

    # create profile session
    session=boto3.Session(profile_name=args.profile)
    key=args.key
    value=args.value
    log.info(f'[main] Session created for profile {args.profile}')

    print("""
    o ||    o ||
    _||    __||     
    ||     \\\       Let the hunt begin.
    _||  _)  \\\  _) 

    """)
    # print(str(datetime.datetime.now().strftime("%X"))+' --- S3 buckets scan is starting')
    # buckets=listPublicBuckets(log,session)

    # print(str(datetime.datetime.now().strftime("%X"))+' --- API Gateways scan is starting')
    # apis=listAPI(log,session)

    # print(str(datetime.datetime.now().strftime("%X"))+' --- EC2 instances scan is starting')
    # ec2s=listPublicEC2(log,session)

    # print(str(datetime.datetime.now().strftime("%X"))+' --- ELB scan is starting')
    # elbs=getELB(log,session)

    # print(str(datetime.datetime.now().strftime("%X"))+' --- RDS scan is starting')
    # dbs=listPublicDB(log,session)

    # print(str(datetime.datetime.now().strftime("%X"))+' --- Redshift clusters scan is starting')
    # clusters=listPublicCluster(log,session)

    api={
    'apiId': '8acsazdleg',
    'region': 'us-west-2',
    'endpoint': 'https://8acsazdleg.execute-api.us-west-2.amazonaws.com',
    'routes': [{
        'routeKey': 'POST /call_recording',
        'integrationUri': 'arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:555773567328:function:production-call-service-call-recording:latest/invocations',
        'integrationType': 'AWS_PROXY'
    }],
    'apiName': 'production-call-service-CallAssets-1O4NUDQ8GJVVD',
    'service': 'apigatewayv2',
    'arn': 'arn:aws:apigateway:us-west-2::/apis/8acsazdleg'
}
    print(getAPITags(log,session,api))

    return 1

if __name__ == "__main__":
    main()