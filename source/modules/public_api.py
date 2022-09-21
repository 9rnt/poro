import boto3
import botocore
from modules.test_endpoint import isEndPointUp

def listAPI(log,session):
    log.info('[listAPI] Start')
    # Initializate API list
    public_API=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('apigateway')
    log.debug(f'[listAPI] available regions: {available_regions}')    
    for region in available_regions:    
        try: 
            # Get classic API gateway list
            client = session.client('apigateway',region_name=region)
            APIs=client.get_rest_apis().get("items")
            for api in APIs:
                if not('PRIVATE' in api.get("endpointConfiguration").get("types")):
                    stages=client.get_stages(restApiId=api.get("id")).get("item")
                    api_resources=client.get_resources(restApiId=api.get("id")).get('items')
                    log.debug(f'[listAPI] List of resources for restAPI {api.get("id")}: {api_resources}')
                    routes=[]
                    for stage in stages:
                        endpoint="https://"+api.get("id")+".execute-api."+region+".amazonaws.com/"+stage.get("stageName")+"/"
                        if isEndPointUp(log,endpoint):
                            if api_resources:
                                for api_resource in api_resources:
                                    if 'resourceMethods' in api_resource:
                                        for k in api_resource.get('resourceMethods'):
                                            integration=client.get_integration(restApiId=api.get("id"),resourceId=api_resource.get('id'),httpMethod=k)
                                            routes.append({
                                                "routeKey":k+" /"+stage.get("stageName")+api_resource.get('path'),
                                                "integrationUri":integration.get('uri'),
                                                "integrationType":integration.get('type')
                                            })
                            
                            public_API.append(
                                {
                                    "apiId":api.get("id"),
                                    "region":region,
                                    "apiName":api.get("name"),
                                    "endpoint":"https://"+api.get("id")+".execute-api."+region+".amazonaws.com/",
                                    "routes":routes,
                                    "service":"apigateway",
                                    "resourceType":"restapi",
                                    "arn":f"arn:aws:apigateway:{region}::/restapis/{api.get('id')}"
                                }
                            )
 
        except botocore.exceptions.ClientError as e :
            log.info("[listAPI] Unexpected error when scanning apigateway in the region %s: %s" %(region, e.response['Error']['Message']))

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('apigatewayv2')

    for region in available_regions:    
        try:
            # Get API v2 list
            client = session.client('apigatewayv2',region_name=region)
            APIs=client.get_apis().get("Items")
            log.debug(f"[listAPI] List APIs is: {APIs}")
            for api in APIs:
                routes=[]
                #---------
                endpoint=api.get('ApiEndpoint')
                routesItems=client.get_routes(ApiId=api.get("ApiId")).get('Items')
                for route in routesItems:
                    integration=client.get_integration(ApiId=api.get("ApiId"),IntegrationId=route.get('Target').split("/")[1])
                    routes.append({
                                        "routeKey":route.get('RouteKey'),
                                        "integrationUri":integration.get('IntegrationUri'),
                                        "integrationType":integration.get('IntegrationType')
                                    })
                public_API.append(
                    {
                        "apiId":api.get("ApiId"),
                        "region":region,
                        "endpoint":api.get('ApiEndpoint'),
                        "routes":routes,
                        "apiName":api.get("Name"),
                        "service":"apigatewayv2",
                        "resourceType":"api",
                        "arn":f"arn:aws:apigateway:{region}::/apis/{api.get('ApiId')}"
                    }
                )
        except botocore.exceptions.ClientError as e :
            log.info("[listAPI] Unexpected error when scanning apigatewayv2 in the region %s: %s" %(region, e.response['Error']['Message']))

    log.info('[listAPI] End')
    return public_API


def getAPITags(log,session,api):
    log.info("[getAPITags] Start")
    if api["service"]=="apigateway":
        client=session.client('resourcegroupstaggingapi',region_name=api["region"])
        try:
            response=client.get_resources(ResourceARNList=[api["arn"]])
            log.debug(f"[getAPITags] tag response for {api['arn']} is {response}")
            if response['ResourceTagMappingList']:
                return response['ResourceTagMappingList'][0]['Tags']
        except botocore.exceptions.ClientError as e :
            log.info(f'[getAPITags] unexpected error when looking for tag {e.response.get("Error")}')
            return None
    elif api["service"]=="apigatewayv2":
        client = session.client('apigatewayv2',region_name=api["region"])
        try:
            response=client.get_tags(ResourceArn=api["arn"])
            log.debug(f"[getAPITags] tag response for {api['arn']} is {response}")
            return response['Tags']
        except botocore.exceptions.ClientError as e :
            log.info(f'[getAPITags] unexpected error when looking for tag {e.response.get("Error")}')
            return None
    else:
        return None