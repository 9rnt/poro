import boto3
import botocore

# Returns a list of public APIs
# Takes a region as an argument
# Return [{API gateway id:[endpoints]}]

def listAPI():
    # Initializate API list
    public_API=[]

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('apigateway')

    for region in available_regions:    
        try: 
            # Get classic API gateway list
            client = boto3.client('apigateway')
            APIs=client.get_rest_apis().get("items")
            for api in APIs:
                if not('PRIVATE' in api.get("endpointConfiguration").get("types")):
                    stages=client.get_stages(restApiId=api.get("id")).get("item")
                    endpoints=[]
                    for stage in stages:
                        endpoints.append("https://"+api.get("id")+".execute-api."+region+".amazonaws.com/"+stage.get("stageName")+"/")
                    public_API.append([api.get("id"),region,endpoints])
        except botocore.exceptions.ClientError as e :
            print("Unexpected error when scanning apigateway in the region %s: %s" %(region, e.response['Error']['Message']))

    # Get available regions list 
    available_regions = boto3.Session().get_available_regions('apigatewayv2')

    for region in available_regions:    
        try:
            # Get API v2 list
            client = boto3.client('apigatewayv2')
            APIs=client.get_apis().get("Items")
            for api in APIs:
                public_API.append([api.get("ApiId"),region,[api.get('ApiEndpoint')]])
        except botocore.exceptions.ClientError as e :
            print("Unexpected error when scanning apigatewayv2 in the region %s: %s" %(region, e.response['Error']['Message']))

    return public_API
