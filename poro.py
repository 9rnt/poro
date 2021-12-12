from modules.public_buckets import listPublicBuckets
from modules.public_api import listAPI
from modules.public_ec2 import listPublicEC2
from modules.elb import getELB
from modules.public_db import listPublicDB
from modules.public_redshift import listPublicCluster


print("""
 o ||    o ||
  _||    __||     
 ||     \\\       Let the hunt begin.
_||  _)  \\\  _) 

""")

print("\n°° Searching for public buckets °°")
buckets=listPublicBuckets()
print("\n°° Searching for exposed APIs °°")
apis=listAPI()
print("\n°° Searching for internet facing EC2 °°")
ec2s=listPublicEC2()
print("\n°° Searching for exposed ELBs °°")
elbs=getELB()
print("\n°° Searching for public RDS DB °°")
dbs=listPublicDB()
print("\n°° Searching for exposed redshift clusters °°")
clusters=listPublicCluster()

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
        print(str(i)+": ELB ARN: "+elb[0]+" -> DNS: "+elb[1][0]+" -> attached security groups: ")
        for sg in elb[1][1]:
            print("------------- "+sg)
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