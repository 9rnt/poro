from glob import glob
from modules.public_buckets import listPublicBuckets
from modules.public_api import listAPI
from modules.public_ec2 import listPublicEC2
from modules.elb import getELB
from modules.public_db import listPublicDB
from modules.public_redshift import listPublicCluster
import logging
import argparse
import boto3
import sys
import datetime

def animate(message):
    global done
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\r' + message + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')


def printForRobots(buckets,apis,ec2s,elbs,dbs,clusters):
    export={
        "Public buckets":[],
        "Public API":[],
        "Public EC2":[],
        "Public ELB":[],
        "Public RDS":[],
        "Public Redshift clusters":[]
    }
    if buckets:
        for bucket in buckets:
            export["Public buckets"].append({
                "Name":bucket[0],
                "Rational":bucket[1]
            })
    if apis:
        for api in apis:
            export["Public API"].append({
                "ID":api[0],
                "Region":api[1],
                "Endpoints":api[2]
            })
    if ec2s:
        for ec2 in ec2s:
            export["Public EC2"].append({
                "ID":ec2[0],
                "Region":ec2[1][0],
                "Public IP":ec2[1][1],
                "Security group":ec2[1][2]
            })
    if elbs:
        for elb in elbs:
            export["Public ELB"].append({
                "ARN":elb[0],
                "DNS":elb[1][0],
                "Security groups":elb[1][1]
            })
    if dbs:
        for db in dbs:
            export["Public RDS"].append({
                "ID":db[0],
                "Region":db[1][0],
                "Security groups":elb[1][1]
            })
    if clusters:
        for cluster in clusters:
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
    log.info(f'[main] Session created for profile {args.profile}')

    print("""
    o ||    o ||
    _||    __||     
    ||     \\\       Let the hunt begin.
    _||  _)  \\\  _) 

    """)
    print(str(datetime.datetime.now().strftime("%X"))+' --- S3 buckets scan is starting')
    buckets=listPublicBuckets(log,session)

    print(str(datetime.datetime.now().strftime("%X"))+' --- API Gateways scan is starting')
    apis=listAPI(log,session)

    print(str(datetime.datetime.now().strftime("%X"))+' --- EC2 instances scan is starting')
    ec2s=listPublicEC2(log,session)

    print(str(datetime.datetime.now().strftime("%X"))+' --- ELB scan is starting')
    elbs=getELB(log,session)

    print(str(datetime.datetime.now().strftime("%X"))+' --- RDS scan is starting')
    dbs=listPublicDB(log,session)

    print(str(datetime.datetime.now().strftime("%X"))+' --- Redshift clusters scan is starting')
    clusters=listPublicCluster(log,session)


    if not args.file_name:        
        print(printForRobots(buckets,apis,ec2s,elbs,dbs,clusters))

    else:
        f = open(args.file_name, "w")
        f.write(str(printForRobots(buckets,apis,ec2s,elbs,dbs,clusters)))
        f.close()
    return 1


if __name__ == "__main__":
    main()