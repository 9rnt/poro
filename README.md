# poro
![Poro art](https://i.ibb.co/4K4vq3G/poro-small.png)

## Description
Scans for publicly accessible assets on your AWS environment and return information about the resources including tags

Services covered by this tool:
- AWS ELB
- API Gateway
- S3 Buckets
- RDS Databases
- EC2 instances
- Redshift Databases

## Env variables description
log_level = os.environ['LOG_LEVEL'].upper()
    role_name = os.environ['ROLE_NAME']
    accounts_configuration = list(eval(os.environ['ACCOUNTS_CONFIGURATION']))
    db_url = os.environ['DB_URL']
    db_username = os.environ['DB_USERNAME']
    db_password = os.environ['DB_PASSWORD']
    db_name = os.environ['DB_NAME']

| Variable | Description |
|----------|-------------|
| LOG_LEVEL | Log level required by the app |
| ROLE_NAME | The role name for the app to assume. Must have read only permissions to the services covered by the tool |
| ACCOUNTS_CONFIGURATION | A list of dicts (passed as string) of the accounts id and external ids used by to assume the role (consider passing it with a secret manager tool). When no external Id is configured in the assume role do not pass it. Example: [{'accountId':'18976838763','externalId':'lkjdalkj/9871lklazdlkKLJldn'},{'accountId':'198719871379'}] |
| DB_URL | The Arangodb url. Example http://localhost:8529 |
| DB_NAME | ArangoDB name |
| DB_USERNAME | Arangodb user name |
| DB_PASSWORD | Arangodb password (consider passing it with a secret manager tool) |