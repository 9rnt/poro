import boto3
import botocore
from modules.test_endpoint import isEndPointUp
import enlighten

# Returns a list of public APIs
# Takes a region as an argument
# Return [{API gateway id:[endpoints]}]

def listAPI(log,session):
    log.info('[listAPI] Start')
    # Initializate API list
    public_API=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('apigateway')
    log.debug(f'[listAPI] available regions: {available_regions}')
    bar_format = '{desc}{desc_pad}{percentage:3.0f}%|{bar}| ' 
    manager = enlighten.get_manager()
    pbar = manager.counter(total=len(available_regions), desc=f'Scanning APIGW: ', bar_format=bar_format) 
    
    for region in available_regions:    
        try: 
            # Get classic API gateway list
            client = session.client('apigateway',region_name=region)
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
            log.info("[listAPI] Unexpected error when scanning apigateway in the region %s: %s" %(region, e.response['Error']['Message']))
        pbar.update(1)

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('apigatewayv2')

    for region in available_regions:    
        try:
            # Get API v2 list
            client = session.client('apigatewayv2',region_name=region)
            APIs=client.get_apis().get("Items")
            for api in APIs:
                public_API.append([api.get("ApiId"),region,[api.get('ApiEndpoint')]])
        except botocore.exceptions.ClientError as e :
            log.info("[listAPI] Unexpected error when scanning apigatewayv2 in the region %s: %s" %(region, e.response['Error']['Message']))

    log.info('[listAPI] End')
    return public_API
