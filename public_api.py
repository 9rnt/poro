import boto3
import botocore

# Returns a list of public APIs
# Takes a region as an argument
# Return [{API gateway id:[endpoints]}]

def listAPI(region):
    # Initializate API list
    public_API=[]

    # Get classic API gateway list
    client = boto3.client('apigateway')
    APIs=client.get_rest_apis().get("items")
    for api in APIs:
        if not('PRIVATE' in api.get("endpointConfiguration").get("types")):
            stages=client.get_stages(restApiId=api.get("id")).get("item")
            endpoints=[]
            for stage in stages:
                endpoints.append("https://"+api.get("id")+".execute-api."+region+".amazonaws.com/"+stage.get("stageName")+"/")
            public_API.append({api.get("id"):endpoints})

    # Get API v2 list
    client = boto3.client('apigatewayv2')
    APIs=client.get_apis().get("Items")
    for api in APIs:
        public_API.append({api.get("ApiId"):[api.get('ApiEndpoint')]})

    return public_API
