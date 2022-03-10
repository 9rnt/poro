import boto3
import botocore
from modules.test_endpoint import isEndPointUp

# Returns a list of public APIs
# Takes a region as an argument
# Return [{API gateway id:[endpoints]}]

def listAPI(log,session):
    log.info('[listAPI] Start')
    # Initializate API list
    public_API=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('apigateway')

    for region in available_regions:    
        try: 
            # Get classic API gateway list
            client = session.client('apigateway')
            APIs=client.get_rest_apis().get("items")
            for api in APIs:
                if not('PRIVATE' in api.get("endpointConfiguration").get("types")):
                    stages=client.get_stages(restApiId=api.get("id")).get("item")
                    endpoints=[]
                    for stage in stages:
                        endpoint="https://"+api.get("id")+".execute-api."+region+".amazonaws.com/"+stage.get("stageName")+"/"
                        if isEndPointUp(log,endpoint):
                            endpoints.append("https://"+api.get("id")+".execute-api."+region+".amazonaws.com/"+stage.get("stageName")+"/")
                            public_API.append([api.get("id"),region,endpoints])
        except botocore.exceptions.ClientError as e :
            log.error("[listAPI] Unexpected error when scanning apigateway in the region %s: %s" %(region, e.response['Error']['Message']))

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('apigatewayv2')

    for region in available_regions:    
        try:
            # Get API v2 list
            client = session.client('apigatewayv2')
            APIs=client.get_apis().get("Items")
            for api in APIs:
                public_API.append([api.get("ApiId"),region,[api.get('ApiEndpoint')]])
        except botocore.exceptions.ClientError as e :
            log.error("[listAPI] Unexpected error when scanning apigatewayv2 in the region %s: %s" %(region, e.response['Error']['Message']))

    log.info('[listAPI] End')
    return public_API
