import base64
import json
import os
import typing as t
from datetime import datetime
from functools import wraps
from typing import List

import requests

from . import schema
from .utils import compact_mapping, to_iso8601, decode_base64_string
from .exceptions import (
    EloqAPIError,
    EloqAuthenticationError,
    EloqPermissionError,
    EloqNotFoundError,
    EloqRateLimitError,
    EloqServerError,
    EloqValidationError,
)


__VERSION__ = "0.1.2"

ELOQ_API_KEY_ENVIRON = "ELOQ_API_KEY"
ELOQ_API_BASE_URL = "https://api-prod.eloqdata.com/api/v1/"
ENABLE_PYDANTIC = True


def returns_model(model, is_array=False):
    """Decorator that returns a Pydantic dataclass.

    :param model: The Pydantic dataclass to return.
    :param is_array: Whether the return value is an array (default is False).
    :return: A Pydantic dataclass.

    If Pydantic is not enabled, the original return value is returned.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not ENABLE_PYDANTIC:
                return func(*args, **kwargs)

            result = func(*args, **kwargs)

            if is_array:
                return [
                    model(**item) if isinstance(item, dict) else item for item in result
                ]
            else:
                return model(**result) if isinstance(result, dict) else result

        return wrapper

    return decorator


def returns_subkey(key):
    """Decorator that returns a subkey.

    :param key: The key to return.
    :return: The value of the key in the return value.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                try:
                    return getattr(result, key)
                except AttributeError:
                    return result[key]
            except EloqAPIError:
                # Re-raise EloqAPIError without modification to avoid duplicate error messages
                raise

        return wrapper

    return decorator


class EloqAPI:
    def __init__(self, api_key: str, *, base_url: str = None):
        """A Eloq API client.

        :param api_key: The API key to use for authentication.
        :param base_url: The base URL of the Eloq API (default is https://api.eloq.com/api/v1/).
        """

        # Set the base URL.
        if not base_url:
            base_url = ELOQ_API_BASE_URL

        # Private attributes.
        self._api_key = api_key
        self._session = requests.Session()

        # Public attributes.
        self.base_url = base_url
        self.user_agent = f"eloq-client/python version=({__VERSION__})"

    def __repr__(self):
        return f"<EloqAPI base_url={self.base_url!r}>"

    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ):
        """Send an HTTP request to the specified API path using the specified method.

        :param method: The HTTP method to use (e.g., "GET", "POST", "PUT", "DELETE").
        :param path: The API path to send the request to.
        :param kwargs: Additional keyword arguments to pass to the requests.Session.request method.
        :return: The JSON response from the server.
        """

        # Set HTTP headers for outgoing requests.
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"{self._api_key}"
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent

        # Send the request.
        r = self._session.request(
            method, self.base_url + path, headers=headers, **kwargs
        )

        # Check the response status code.
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Parse the error response
            try:
                error_data = r.json()
            except (ValueError, json.JSONDecodeError):
                error_data = {"message": r.text, "code": r.status_code}

            # Create appropriate exception based on status code
            if r.status_code == 401:
                raise EloqAuthenticationError(r.text, r.status_code, error_data)
            elif r.status_code == 403:
                raise EloqPermissionError(r.text, r.status_code, error_data)
            elif r.status_code == 404:
                raise EloqNotFoundError(r.text, r.status_code, error_data)
            elif r.status_code == 429:
                raise EloqRateLimitError(r.text, r.status_code, error_data)
            elif r.status_code >= 500:
                raise EloqServerError(r.text, r.status_code, error_data)
            elif r.status_code == 400:
                raise EloqValidationError(r.text, r.status_code, error_data)
            else:
                raise EloqAPIError(r.text, r.status_code, error_data)

        return r.json()

    def _url_join(self, *args):
        """Join a list of URL components into a single URL."""

        return "/".join(args)

    @classmethod
    def from_environ(cls):
        """Create a new Eloq API client from the `ELOQ_API_KEY` environment variable."""

        return cls(os.environ[ELOQ_API_KEY_ENVIRON])

    @classmethod
    def from_key(cls, key: str):
        """Create a new Eloq API client from a key."""

        return cls(key)

    @classmethod
    def from_key_and_url(cls, key: str, url: str):
        """Create a new Eloq API client from a key and URL."""

        return cls(key, base_url=url)

    # Organization and Project Management
    @returns_model(schema.UserOrgInfoDTO)
    @returns_subkey("data")
    def info(self) -> schema.UserOrgInfoDTO:
        """Get organization and related project info.

        Returns a structured UserOrgInfoDTO object containing:
        - auth_provider: Authentication provider (e.g., "github")
        - create_at: User account creation timestamp
        - email: User email address
        - org_info: Organization information object
        - user_name: Username

        More info: Get current user's organization information
        """

        return self._request("GET", "org-info")

    @returns_model(schema.SimpleOrgInfo)
    def org(self) -> schema.SimpleOrgInfo:
        """Get simplified organization information.

        This function calls the org_info() method and extracts only the basic
        organization details for simplified access.

        :return: A SimpleOrgInfo object containing basic organization information.

        Example usage:

            >>> org = client.org()
            >>> print(f"Organization: {org.org_name}")
            >>> print(f"ID: {org.org_id}")
            >>> print(f"Created: {org.org_create_at}")

        More info: Get simplified organization info
        """

        org_info = self.org_info()

        # Return SimpleOrgInfo object
        return {
            "org_name": org_info.org_info.org_name,
            "org_id": org_info.org_info.org_id,
            "org_create_at": org_info.org_info.org_create_at,
        }

    # Cluster Management
    @returns_model(schema.ClusterList)
    @returns_subkey("data")
    def clusters(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> schema.ClusterList:
        """Get a list of clusters in a project.

        :param org_id: The organization ID.
        :param project_id: The project ID.
        :param page: The page number for pagination (default is 1).
        :param per_page: The number of items per page (default is 20).
        :return: A list of dataclasses representing the clusters.

        More info: List clusters in a project
        """
        org = self.info()
        org_id = org.org_info.org_id
        project_id = org.org_info.projects[0].project_id
        r_path = f"orgs/{org_id}/projects/{project_id}/clusters"
        r_params = compact_mapping({"page": page, "perPage": per_page})

        return self._request("GET", r_path, params=r_params)

    @returns_model(schema.DescClusterDTO)
    @returns_subkey("data")
    def cluster(
        self,
        cluster_name: str,
    ) -> schema.DescClusterDTO:
        """Get detailed information about a cluster.

        :param cluster_name: The name of the cluster.
        :return: A dataclass representing the cluster details.

        More info: Describe cluster
        """

        org_info = self.info()
        org_id = org_info.org_info.org_id
        project_id = org_info.org_info.projects[0].project_id
        r_path = f"orgs/{org_id}/projects/{project_id}/clusters/{cluster_name}"

        return self._request("GET", r_path)

    def cluster_create(
        self,
        cluster_name: str,
        region: str,
        sku_id: int,
    ) -> schema.OperationResult:
        """Create a new cluster in a project.

        This method creates a new cluster using direct parameters.
        The organization ID and project ID are automatically retrieved from
        the current user's context.

        :param cluster_name: Cluster display name (required).
        :param region: Region where the cluster will be created, e.g., "ap-northeast-1" (required).
        :param sku_id: SKU ID for the cluster (required). Use get_skus() to find available SKU IDs.
        :return: An OperationResult object with success (bool) and message (str).

        Example usage:

            >>> from eloq_sdk import schema
            >>> client = EloqAPI.from_environ()
            >>>
            >>> # First, get available SKUs
            >>> skus = client.get_skus(
            ...     sku_type=schema.SKUType.SERVERLESS,
            ...     eloq_module=schema.EloqModule.ELOQKV,
            ...     cloud_provider=schema.CloudProvider.AWS
            ... )
            >>>
            >>> # Create the cluster with direct parameters
            >>> result = client.cluster_create(
            ...     cluster_name="my-cluster",
            ...     region="ap-northeast-1",
            ...     sku_id=skus[0].sku_id
            ... )
            >>>
            >>> if result.success:
            ...     print(f"✅ {result.message}")
            ... else:
            ...     print(f"❌ {result.message}")

        More info: Create cluster in a project
        """
        try:
            # Create request object internally
            request = schema.CreateClusterRequest(
                cluster_name=cluster_name,
                region=region,
                sku_id=sku_id,
                required_zone="us-west-1a",  # Now we provide us service first
            )

            org_info = self.info()
            org_id = org_info.org_info.org_id
            project_id = org_info.org_info.projects[0].project_id
            r_path = f"orgs/{org_id}/projects/{project_id}/clusters"

            response = self._request("POST", r_path, json=request.to_dict())

            # Check if operation was successful (code 0 means success)
            if response.get("code") == 200:
                return schema.OperationResult(
                    success=True,
                    message=response.get("message", "Cluster created successfully"),
                )
            else:
                return schema.OperationResult(
                    success=False,
                    message=response.get("message", "Failed to create cluster"),
                )

        except EloqAPIError as e:
            return schema.OperationResult(
                success=False, message=f"Failed to create cluster: {str(e)}"
            )
        except Exception as e:
            return schema.OperationResult(
                success=False, message=f"Unexpected error: {str(e)}"
            )

    def cluster_delete(
        self,
        cluster_name: str,
    ) -> schema.OperationResult:
        """Delete a cluster.

        This method deletes a specified cluster. The cluster must be in
        'available' status to be deleted. The organization ID and project ID
        are automatically retrieved from the current user's context.

        :param cluster_name: Cluster display name (required).
        :return: An OperationResult object with success (bool) and message (str).

        Example usage:

            >>> client = EloqAPI.from_environ()
            >>>
            >>> # Delete the cluster
            >>> result = client.cluster_delete("my-cluster")
            >>>
            >>> if result.success:
            ...     print(f"✅ {result.message}")
            ... else:
            ...     print(f"❌ {result.message}")

        Note: The cluster must be in 'available' status to be deleted.

        More info: Delete cluster
        """
        try:
            org_info = self.info()
            org_id = org_info.org_info.org_id
            project_id = org_info.org_info.projects[0].project_id
            r_path = (
                f"orgs/{org_id}/projects/{project_id}/clusters/{cluster_name}/delete"
            )

            response = self._request("DELETE", r_path)

            # Check if operation was successful (code 0 means success)
            if response.get("code") == 200:
                return schema.OperationResult(
                    success=True,
                    message=response.get("message", "Cluster deleted successfully"),
                )
            else:
                return schema.OperationResult(
                    success=False,
                    message=response.get("message", "Failed to delete cluster"),
                )

        except EloqAPIError as e:
            # Handle specific error cases
            if e.status_code == 403:
                return schema.OperationResult(
                    success=False,
                    message=f"Permission denied or cluster not in available status: {str(e)}",
                )
            elif e.status_code == 404:
                return schema.OperationResult(
                    success=False, message=f"Cluster not found: {str(e)}"
                )
            elif e.status_code == 400:
                return schema.OperationResult(
                    success=False, message=f"Invalid request: {str(e)}"
                )
            else:
                return schema.OperationResult(
                    success=False, message=f"Failed to delete cluster: {str(e)}"
                )
        except Exception as e:
            return schema.OperationResult(
                success=False, message=f"Unexpected error: {str(e)}"
            )

    @returns_model(schema.ClusterCredentials)
    def cluster_credentials(
        self,
        cluster_name: str,
    ) -> schema.ClusterCredentials:
        """Get cluster credentials (username and password) for database connection.

        This function calls the cluster() method and extracts the admin credentials
        for easy access to database connection information. The admin user ID and
        password are automatically decoded from base64 encoding.

        :param cluster_name: The name of the cluster.
        :return: A ClusterCredentials object containing cluster credentials and connection info.

        Example usage:

            >>> credentials = client.cluster_credentials("my-cluster")
            >>> print(f"Username: {credentials.username}")
            >>> print(f"Password: {credentials.password}")
            >>> print(f"Host: {credentials.host}")
            >>> print(f"Port: {credentials.port}")

        More info: Get cluster credentials for database connection
        """
        cluster_info = self.cluster(cluster_name)

        # Decode base64 encoded admin user ID and password
        try:
            decoded_user_id = decode_base64_string(
                cluster_info.admin_user, "Failed to decode admin user ID"
            )
            decoded_password = decode_base64_string(
                cluster_info.admin_password, "Failed to decode admin password"
            )
        except ValueError as e:
            raise EloqAPIError(str(e))

        # Return ClusterCredentials object with decoded values
        return {
            "username": decoded_user_id,
            "password": decoded_password,
            "host": cluster_info.elb_addr,
            "port": cluster_info.elb_port,
            "status": cluster_info.status,
        }

    # SKU Management
    @returns_model(schema.SKUInfo, is_array=True)
    @returns_subkey("data")
    def get_skus(
        self,
        sku_type: schema.SKUType,
        eloq_module: schema.EloqModule,
        cloud_provider: schema.CloudProvider,
    ) -> t.List[schema.SKUInfo]:
        """Get SKU list based on filters.

        This method retrieves a list of SKUs filtered by SKU type, EloqDB module type,
        and cloud provider. Only SKUs available in the user's subscription plan are returned.

        :param sku_type: SKU type filter (SERVERLESS or DEDICATED).
        :param eloq_module: EloqDB module type filter (ELOQKV or ELOQDOC).
        :param cloud_provider: Cloud provider filter (AWS or GCP).
        :return: A list of SKUInfo objects containing SKU details.

        Example usage:

            >>> from eloq_sdk import schema
            >>> client = EloqAPI.from_environ()
            >>> skus = client.get_skus(
            ...     sku_type=schema.SKUType.SERVERLESS,
            ...     eloq_module=schema.EloqModule.ELOQKV,
            ...     cloud_provider=schema.CloudProvider.AWS
            ... )
            >>> for sku in skus:
            ...     print(f"SKU: {sku.sku_name}, Type: {sku.sku_type}")
            ...     print(f"CPU Limit: {sku.tx_cpu_limit}, Memory: {sku.tx_memory_mi_limit}")

        More info: List SKUs by filters
        """
        request = schema.SKUListRequest(
            type=sku_type,
            eloq_module=eloq_module,
            cloud_provider=cloud_provider,
        )
        params = request.to_query_params()

        return self._request("GET", "skus-by-args", params=params)
