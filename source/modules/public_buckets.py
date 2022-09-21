import botocore

def listPublicBuckets(log,session):
    # Initializate publicBuckets list
    log.info('[listPublicBucket] Start')
    publicBuckets=[]

    # Get bucket list
    client = session.client('s3')
    response = client.list_buckets()
    buckets = response['Buckets']
    log.debug(f'[listPublicBucket] number of buckets: {len(buckets)}')
    for bucket in buckets :
        # Check if PublicAccessBlockConfiguration allows public ACLs or policies
        try :
            publicAccessBlock=client.get_public_access_block(Bucket=bucket['Name'])
            if (not(publicAccessBlock['PublicAccessBlockConfiguration']['BlockPublicAcls'] and publicAccessBlock['PublicAccessBlockConfiguration']['IgnorePublicAcls'])):
                publicAcl=True
            else: 
                publicAcl=False
            if (not(publicAccessBlock['PublicAccessBlockConfiguration']['RestrictPublicBuckets'] and publicAccessBlock['PublicAccessBlockConfiguration']['BlockPublicPolicy'])):
                publicPolicy=True
            else:
                publicPolicy=False

        except botocore.exceptions.ClientError as e :
            if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                publicAcl=True
                publicPolicy=True
            else :
                code=e.response.get("Error").get("Code")
                log.info(f"[listPublicBucket] Unexpected error with bucket {bucket['Name']}: {code}")

        # Check if the bucket ACL allows public access
        if (publicAcl):
            try:
                acl=client.get_bucket_acl(Bucket=bucket['Name'])
                isACLPublic=False
                for grants in acl['Grants']:
                    grantee=grants['Grantee'].get('URI')
                    if(grantee=='http://acs.amazonaws.com/groups/global/AllUsers' or grantee=='http://acs.amazonaws.com/groups/global/AuthenticatedUsers'):
                        isACLPublic=True
                if (isACLPublic):
                    publicBuckets.append({
                        "name":bucket['Name'],
                        "rational":"Public ACL",
                        "service":"s3",
                        "resourceType":"bucket",
                        "arn":f"arn:aws:s3:::{bucket['Name']}"
                        })
            except botocore.exceptions.ClientError as e :
                code=e.response.get("Error").get("Code")
                log.info(f"unexpected error with bucket {bucket['Name']}: {code}")

        # Check if the Bucket policy allows public access
        if(publicPolicy):
            try:
                policy=client.get_bucket_policy_status(Bucket=bucket['Name'])
                if(policy['PolicyStatus']['IsPublic']):
                    publicBuckets.append({
                        "name":bucket['Name'],
                        "rational":"Public Policy",
                        "service":"s3",
                        "resourceType":"bucket",
                        "arn":f"arn:aws:s3:::{bucket['Name']}"
                        })
            except botocore.exceptions.ClientError as e :
                code=e.response.get("Error").get("Code")
                log.info(f"[listPublicBucket] Unexpected error with bucket {bucket['Name']}: {code}")

    log.info('[listPublicBucket] End')
    return publicBuckets


def getBucketTags(log,session,bucket):
    log.info("[getBucketTags] Start")
    client = session.client('s3')
    try:
        response = client.get_bucket_tagging(Bucket=bucket["name"])
        return response['TagSet']
    except botocore.exceptions.ClientError as e :
        log.info(f'[getBucketTags] unexpected error when looking for tag {e.response.get("Error")}')
        return None