from modules.public_buckets import *
from modules.public_api import *
from modules.public_ec2 import *
from modules.elb import *
from modules.public_db import *
from modules.public_redshift import *
import logging
import os
import boto3
from pyArango.connection import *

def aws_session(log, role_arn=None, external_id=None, session_name='my_session'):
    """
    If role_arn is given assumes a role and returns boto3 session
    otherwise return a regular session with the current IAM user/role
    """
    log.info(f'[aws_session] Start')

    if role_arn and len(external_id)>1:
        client = boto3.client('sts')
        response = client.assume_role(RoleArn=role_arn, ExternalId= external_id, RoleSessionName=session_name)
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'])
        log.info(f'[awsSession] Successfully assumed the role {role_arn}')
        return session
    elif role_arn:
        client = boto3.client('sts')
        response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'])
        log.info(f'[awsSession] Successfully assumed the role {role_arn}')
        return session
    else:
        log.info(f'[aws_session] No new role was detected. Continue with Service IAM role')
        return boto3.Session()

def write_to_db(log,db_url,username,password,db_name,collection,list):
    log.info(f'[write_to_db] Start')
    conn = Connection(arangoURL=db_url,username=username, password=password)
    db = conn[db_name]
    if not db.hasCollection(collection):
        coll = db.createCollection(name=collection)
    else:
        coll = db[collection]
        
    for i in list:
        doc = coll.createDocument()
        for k in i:
            if k == "arn":
                doc._key = i[k].replace("/",":")
            else:            
                doc[k]=i[k]
        doc.save()

    log.info(f'[write_to_db] End')

    return 1

def main():
    logging.basicConfig(format="%(levelname)s: %(message)s")
    log = logging.getLogger()
    log_level = os.environ['LOG_LEVEL'].upper()
    role_name = os.environ['ROLE_NAME']
    accounts_configuration = list(eval(os.environ['ACCOUNTS_CONFIGURATION']))
    db_url = os.environ['DB_URL']
    db_username = os.environ['DB_USERNAME']
    db_password = os.environ['DB_PASSWORD']
    db_name = os.environ['DB_NAME']
    log.setLevel(log_level)

    resource_tags=[]
    buckets=[]
    apis=[]
    ec2s=[]
    dbs=[]
    clusters=[]
    elbs=[]

    for a_c in accounts_configuration:
        role_arn=f"arn:aws:iam::{a_c['accountId']}:role/{role_name}"
        session = aws_session(log,role_arn=role_arn, external_id=a_c['externalId'], session_name='poro_session')

        buckets=listPublicBuckets(log,session)
        for resource in buckets:
            resource_tags.append(
                {
                    "arn":f"{a_c['accountId']}/tags/{resource['arn']}",
                    "service":resource["service"],
                    "resourceType":resource["resourceType"],
                    "tags":getBucketTags(log,session,resource)
                })
        apis=listAPI(log,session)
        for resource in apis:
            resource_tags.append(
                {
                    "arn":f"{a_c['accountId']}/tags/{resource['arn']}",
                    "service":resource["service"],
                    "resourceType":resource["resourceType"],
                    "tags":getAPITags(log,session,resource)
                })
        ec2s=listPublicEC2(log,session)
        for resource in ec2s:
            resource_tags.append(
                {
                    "arn":f"{a_c['accountId']}/tags/{resource['arn']}",
                    "service":resource["service"],
                    "resourceType":resource["resourceType"],
                    "tags":getEC2Tags(log,session,resource)
                })
        elbs=getELB(log,session)
        for resource in elbs:
            resource_tags.append(
                {
                    "arn":f"{a_c['accountId']}/tags/{resource['arn']}",
                    "service":resource["service"],
                    "resourceType":resource["resourceType"],
                    "tags":getELBTags(log,session,resource)
                })
        dbs=listPublicDB(log,session)
        for resource in dbs:
            resource_tags.append(
                {
                    "arn":f"{a_c['accountId']}/tags/{resource['arn']}",
                    "service":resource["service"],
                    "resourceType":resource["resourceType"],
                    "tags":getRdsInstanceTags(log,session,resource)
                })
        clusters=listPublicCluster(log,session)
        for resource in clusters:
            resource_tags.append(
                {
                    "id":f"{a_c['accountId']}/tags/{resource['arn']}",
                    "service":resource["service"],
                    "resourceType":resource["resourceType"],
                    "tags":getClusterTags(log,session,resource)
                })

        write_to_db(log,db_url,db_username,db_password,db_name,"public_resources",buckets)
        write_to_db(log,db_url,db_username,db_password,db_name,"public_resources",apis)
        write_to_db(log,db_url,db_username,db_password,db_name,"public_resources",ec2s)
        write_to_db(log,db_url,db_username,db_password,db_name,"public_resources",elbs)
        write_to_db(log,db_url,db_username,db_password,db_name,"public_resources",clusters)
        write_to_db(log,db_url,db_username,db_password,db_name,"public_resources",dbs)
        write_to_db(log,db_url,db_username,db_password,db_name,"resource_tags",resource_tags)

    return 1

if __name__ == "__main__":
    main()