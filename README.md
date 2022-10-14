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

Poro also check if a tag you specify is applied to identified public resources using --tag-key and --tag-value arguments.

## Prequisites
- AWS account with Read Only Access to services listed above.
- Python 3.X
- requests>=2.22.0
- boto3>=1.20
- botocore>= 1.20
- enlighten>=1

## Usage
- Clone this repository
- Configure your envionment with active credentials -> aws configure [sso]
- pip install -r requirements.txt
- Run python poro.py [-h] [--profile PROFILE] [--export FILE_NAME] [--verbose] [--tag-key KEY] [--tag-value VALUE]

      optional arguments:
      -h, --help          show this help message and exit
      --profile PROFILE   Specify the aws profile (default is default)
      --export FILE_NAME  Specify the file name if you want to expport the results
      --verbose, -v
      --tag-key KEY       Specify the tag key that you want to check if it exists in public resources
      --tag-value VALUE   Specify the tag value that you want to check if it exists in public resources

Poro prints the scanning results at the end of it's execution in a json file if export option is not specified.
