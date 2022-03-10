from modules.public_buckets import listPublicBuckets
from modules.public_api import listAPI
from modules.public_ec2 import listPublicEC2
from modules.elb import getELB
from modules.public_db import listPublicDB
from modules.public_redshift import listPublicCluster
import logging
import argparse
import boto3

def printForHuman(buckets,apis,ec2s,elbs,dbs,clusters):
    print("\n\nHunting results:")
    print("======================================================")
    print("================= Public Buckets =====================")
    i=1
    if buckets:
        for bucket in buckets:
            print(str(i)+": Bucket name: "+bucket[0]+" -> "+bucket[1])
            i+=1
    else:
        print("No public buckets")
    print("\n======================================================")
    print("================== Exposed APIs ======================")
    i=1
    if apis:
        for api in apis:
            print(str(i)+": API id: "+api[0]+" -> region: "+api[1]+" -> endpoints: ")
            for endpoint in api[2]:
                print("------------- "+endpoint)
            i+=1
    else:
        print("No public APIs")
    print("\n======================================================")
    print("================ Internet facing EC2 =================")
    i=1
    if ec2s:
        for ec2 in ec2s:
            print(str(i)+": Instance id: "+ec2[0]+" -> region: "+ec2[1][0]+" -> public IP: "+ec2[1][1]+" -> security group: "+ec2[1][2])
            i+=1
    else:
        print("No internet facing EC2s")
    print("\n======================================================")
    print("==================== Exposed ELB =====================")
    i=1
    if elbs:
        for elb in elbs:
            print(str(i)+": ELB ARN: "+elb[0]+" -> DNS: "+elb[1][0]+" -> attached security groups:")
            for sg in elb[1][1]:
                print("\n\t"+sg)
            i+=1
    else:
        print("No exposed ELBs")
    print("\n======================================================")
    print("=================== Public RDS DB ====================")
    i=1
    if dbs:
        for db in dbs:
            print(str(i)+": RDS id: "+db[0]+" -> region: "+db[1][0]+" -> public IP: "+"to specify"+" -> security group: "+db[1][1])
            i+=1
    else:
        print("No public RDS DBs")
    print("\n======================================================")
    print("============= Public Redshift clusters ===============")
    i=1
    if clusters:
        for cluster in clusters:
            print(str(i)+": Cluster id: "+cluster[0]+" -> region: "+cluster[1][0]+" -> DB Name: "+cluster[1][1]+" -> Endpoint: "+cluster[1][2]+" -> Public SG: "+cluster[1][3])
            i+=1
    else:
        print("No public Redshift clusters")

    return 1

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

    print(export)
    return 1

def main():

    logging.basicConfig(format="%(levelname)s: %(message)s")
    log = logging.getLogger()
    
    parser = argparse.ArgumentParser(description="Scans publicly exposed assets in AWS environment.")
    # parse arguments
    parser.add_argument('--profile', dest='profile',default='default', help='Specify the aws profile (default is default)')
    parser.add_argument('--export', dest='file_name', help='Specify the file name if you want to expport the results')
    parser.add_argument('--format', dest='format',default='human', choices=['human', 'json'], help='Specify the formatting option (default is human)')

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

    print("\n°° Searching for public buckets °°")
    buckets=listPublicBuckets(log,session)
    print("\n°° Searching for exposed APIs °°")
    apis=listAPI(log,session)
    print("\n°° Searching for internet facing EC2 °°")
    ec2s=listPublicEC2(log,session)
    print("\n°° Searching for exposed ELBs °°")
    elbs=getELB(log,session)
    print("\n°° Searching for public RDS DB °°")
    dbs=listPublicDB(log,session)
    print("\n°° Searching for exposed redshift clusters °°")
    clusters=listPublicCluster(log,session)

    if not args.file_name:
        if args.format == "human":
            printForHuman(buckets,apis,ec2s,elbs,dbs,clusters)
        if args.format == "json":
            printForRobots(buckets,apis,ec2s,elbs,dbs,clusters)
    else:
        f = open(args.file_name, "w")
        if args.format == "human":
            f.write(printForHuman(buckets,apis,ec2s,elbs,dbs,clusters))
            f.close()
        if args.format == "json":
            f.write(printForRobots(buckets,apis,ec2s,elbs,dbs,clusters))
            f.close()
        
    return 1


if __name__ == "__main__":
    main()