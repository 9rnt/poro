# poro
![Poro art](https://i.ibb.co/4K4vq3G/poro-small.png)

## Description
Scan for publicly accessible assets on your AWS environment
Services covered by this tool:
- AWS ELB
- API Gateway
- S3 Buckets
- RDS Databases
- EC2 instances
- Redshift Databases

## Prequisities
- AWS account with Read Only Access to services listed above.
- Python 3.X
- Boto3 > 1.2X
- Botocore > 1.2X
- Requests > 2.2X

## How to use
- Clone this repository
- Configure your envionment with active credentials -> aws configure
- Run python poro.py
Poro will print all exception raised when querying AWS APIs, the scanning result will be printed at the end of the output.
Example of Poro output:
```
o ||    o ||
  _||    __||     
 ||     \\       Let the hunt begin.
_||  _)  \\  _) 


°° Searching for public buckets °°
Unexpected error whith bucket XXX: NoSuchBucketPolicy

°° Searching for exposed APIs °°

°° Searching for internet facing EC2 °°
Unexpected error when scanning ec2 in the region af-south-1: AWS was not able to validate the provided access credentials
Unexpected error when scanning ec2 in the region ap-east-1: AWS was not able to validate the provided access credentials

°° Searching for exposed ELBs °°

°° Searching for public RDS DB °°
Unexpected error when scanning RDS in the region af-south-1: The security token included in the request is invalid.

°° Searching for exposed redshift clusters °°
Unexpected error when scanning Redshift in the region af-south-1: The security token included in the request is invalid.
Unexpected error when scanning Redshift in the region ap-east-1: The security token included in the request is invalid.

Hunting results:
======================================================
================= Public Buckets =====================
1: Bucket name: XXX -> Public Policy

======================================================
================== Exposed APIs ======================
No public APIs

======================================================
================ Internet facing EC2 =================
No internet facing EC2s

======================================================
==================== Exposed ELB =====================
1: ELB ARN: arn:aws:elasticloadbalancing:us-west-2:XXX:XXX/XXX/XXX/XXX -> DNS: XXX.us-west-2.elb.amazonaws.com -> attached security groups:
------------- sg-XXX

======================================================
=================== Public RDS DB ====================
No public RDS DBs

======================================================
============= Public Redshift clusters ===============
No public Redshift clusters
```
