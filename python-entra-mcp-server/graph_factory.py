import os
from azure.identity import DefaultAzureCredential
from msgraph import GraphServiceClient
from dotenv import load_dotenv

load_dotenv()

class GraphFactory:
    def __init__(self):
        # Locally uses environment variables; in Azure uses Managed Identity
        self.credential = DefaultAzureCredential()
        self.client = GraphServiceClient(self.credential)

    def get_client(self) -> GraphServiceClient:
        return self.client