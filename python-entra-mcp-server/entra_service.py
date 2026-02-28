from msgraph.generated.models.group import Group
from msgraph.generated.models.team import Team
from msgraph.generated.users.users_request_builder import UsersRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.reference_create import ReferenceCreate

class EntraService:
    def __init__(self, graph_client):
        self.client = graph_client

    async def get_user(self, identifier: str):
        """
        Look up a user and retrieve extended properties + group memberships.
        """
        # 1. Define which specific properties we want to retrieve
        # By default, Graph only returns about 10. We're adding more here.
        select_properties = [
            "id", "displayName", "userPrincipalName", "mail", 
            "jobTitle", "department", "officeLocation", "accountEnabled"
        ]

        # 2. Configure the query to include 'memberOf' (Group memberships)
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            filter = f"userPrincipalName eq '{identifier}' or displayName eq '{identifier}'",
            select = select_properties,
            expand = ["memberOf"]
        )

        request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters = query_params
        )

        try:
            res = await self.client.users.get(request_configuration=request_config)
            
            if not res or not res.value:
                return None

            user = res.value[0]
            
            # Format the membership data for the MCP response
            groups = []
            if hasattr(user, "member_of") and user.member_of:
                for item in user.member_of:
                    if hasattr(item, "display_name"):
                        groups.append({"id": item.id, "name": item.display_name})

            return {
                "id": user.id,
                "displayName": user.display_name,
                "upn": user.user_principal_name,
                "email": user.mail,
                "jobTitle": user.job_title,
                "department": user.department,
                "office": user.office_location,
                "enabled": user.account_enabled,
                "groups": groups
            }
        except Exception as e:
            return f"Error retrieving user details: {str(e)}"

    async def list_user_groups(self, user_id: str):
        """List all groups for a specific user ID."""
        try:
            # We use .member_of to get direct memberships
            # Note: This returns 'DirectoryObjects', so we filter for Groups
            result = await self.client.users.by_user_id(user_id).member_of.get()
            
            groups = []
            if result and result.value:
                for item in result.value:
                    # Check if the object is actually a group (could be a directory role)
                    if hasattr(item, "display_name") and item.display_name:
                        groups.append({
                            "id": item.id,
                            "name": item.display_name,
                            "type": item.odata_type
                        })
            return groups
        except Exception as e:
            return f"Error fetching groups: {str(e)}"

    async def add_member(self, group_id: str, user_id: str):
        """Adds a user to a group using the $ref endpoint."""
        try:
            request_body = ReferenceCreate(
                odata_id = f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
            )
            
            await self.client.groups.by_group_id(group_id).members.ref.post(request_body)
            return f"User {user_id} added to group {group_id} successfully."
        except Exception as e:
            return f"Error adding member: {str(e)}"


    async def create_group(self, name: str, nickname: str, is_m365: bool):
        group_body = Group(
            display_name=name,
            mail_nickname=nickname,
            group_types=["Unified"] if is_m365 else [],
            mail_enabled=is_m365,
            security_enabled=True
        )
        return await self.client.groups.post(group_body)

    async def add_user_to_group(self, group_id: str, user_id: str):
        request_body = {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"}
        return await self.client.groups.by_group_id(group_id).members.ref.post(request_body)

    async def enable_teams(self, group_id: str):
        team_body = Team(additional_data={"template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')"})
        return await self.client.groups.by_group_id(group_id).team.put(team_body)