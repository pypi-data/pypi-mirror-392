from pyteamtv.infra.requester import Requester


class TeamTVObject(object):
    def __init__(self, requester: Requester, attributes: dict):
        self._requester = requester
        self.__attributes = attributes

        self._use_attributes(attributes)

    @property
    def raw_attributes(self):
        return self.__attributes

    @property
    def metadata(self):
        return self._metadata

    @property
    def is_local(self):
        return self._is_local

    @property
    def shared_resource_group(self):
        """
        Get the shared resource group information if this object comes from a shared resource group.

        Returns:
            dict or None: Dictionary with 'name' and 'id' keys if from shared resource group, None otherwise.
            Example: {'name': 'HHK 2025-2026', 'id': 'fd762628-932b-11f0-b457-914324141087'}
        """
        return self._shared_resource_group

    def _use_attributes(self, attributes: dict):
        self._metadata = attributes.get("_metadata", {})

        shared_type = self._metadata.get("source", {}).get("type", {})
        self._is_local = (shared_type is None) or (shared_type == "ResourceGroup")

        # Extract shared resource group info
        self._shared_resource_group = None
        if shared_type == "SharedResourceGroup":
            share = self._metadata.get("source", {}).get("share", {})
            resource_group = share.get("resourceGroup", {})
            if resource_group:
                self._shared_resource_group = {
                    "name": resource_group.get("targetResourceName"),
                    "id": resource_group.get("resourceGroupId"),
                    "tenant_id": resource_group.get("tenantId"),
                }

    def has_privilege(self, action: str) -> bool:
        for privilege, status in self.metadata.get("privilegesV2", {}).items():
            if privilege.endswith(":" + action):
                return status["ok"]
        return False
