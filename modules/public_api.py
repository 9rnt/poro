from importlib import resources
import resource
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
            domains=client.get_domain_names(limit=500).get("items")

            for api in APIs:
                if not('PRIVATE' in api.get("endpointConfiguration").get("types")):
                    stages=client.get_stages(restApiId=api.get("id")).get("item")
                    api_resources=client.get_resources(restApiId=api.get("id")).get('items')
                    log.debug(f'[listAPI] List of resources for restAPI {api.get("id")}: {api_resources}')
                    endpoints=[]
                    for stage in stages:
                        endpoint="https://"+api.get("id")+".execute-api."+region+".amazonaws.com/"+stage.get("stageName")+"/"
                        if isEndPointUp(log,endpoint):
                            if api_resources:
                                for api_resource in api_resources:
                                    if 'resourceMethods' in api_resource:
                                        for k in api_resource.get('resourceMethods'):
                                            integration=client.get_integration(restApiId=api.get("id"),resourceId=api_resource.get('id'),httpMethod=k)
                                            endpoints.append({
                                                "endpoint":k+" https://"+api.get("id")+".execute-api."+region+".amazonaws.com/"+stage.get("stageName")+api_resource.get('path'),
                                                "integration type":integration.get('type'),
                                                "integration uri":integration.get('uri')
                                            })
                            
                            public_API.append([api.get("id"),region,endpoints,api.get("name")])
 
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
            domains=client.get_domain_names(MaxResults=500).get("Items")

            for api in APIs:
                endpoints=[]
                endpoint=api.get('ApiEndpoint')
                routes=client.get_routes(ApiId=api.get("ApiId")).get('Items')
                for route in routes:
                    integration=client.get_integration(ApiId=api.get("ApiId"),IntegrationId=route.get('Target').split("/")[1]).get('IntegrationUri')
                    endpoints.append({
                                        "endpoint":api.get('ApiEndpoint'),
                                        "routes":{
                                            "routeKey":route.get('RouteKey'),
                                            "integration":integration,
                                        }
                                    })
                public_API.append([api.get("ApiId"),region,endpoints,api.get("Name")])
        except botocore.exceptions.ClientError as e :
            log.info("[listAPI] Unexpected error when scanning apigatewayv2 in the region %s: %s" %(region, e.response['Error']['Message']))

    log.info('[listAPI] End')
    return public_API
