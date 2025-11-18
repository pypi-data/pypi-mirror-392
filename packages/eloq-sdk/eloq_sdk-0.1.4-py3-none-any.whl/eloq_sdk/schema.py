# Generated from Eloq API swagger definitions
# Based on swagger.yaml structure

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Dict, Any

try:
    from pydantic.dataclasses import dataclass
except ImportError:
    from dataclasses import dataclass


@dataclass
class ShelfResponse:
    """Base API response structure."""

    code: int
    data: Any
    message: str


@dataclass
class Pagination:
    """Pagination information."""

    cursor: str


@dataclass
class EmptyResponse:
    """Empty response."""

    pass


@dataclass
class ClusterList:
    """Cluster list information."""

    cluster_list: List[ClusterListItem]
    total: int


# Cluster related models
@dataclass
class ClusterListItem:
    """Cluster list item information."""

    cloud_provider: str
    cluster_name: str
    create_at: str
    module_type: str
    region: str
    status: str
    version: str
    zone: str


@dataclass
class DescClusterDTO:
    """Detailed cluster information."""

    admin_password: str
    admin_user: str
    cloud_provider: str
    cluster_deploy_mode: str
    create_at: str
    display_cluster_name: str
    elb_addr: str
    elb_port: int
    elb_state: str
    log_cpu_limit: float
    log_memory_mi_limit: float
    log_replica: int
    module_type: str
    org_name: str
    project_name: str
    region: str
    status: str
    tx_cpu_limit: float
    tx_memory_mi_limit: float
    tx_replica: int
    version: str
    zone: str


class ServiceType(Enum):
    """Service type enumeration."""

    LOG = "log"
    TX = "tx"
    ALL = "all"


# Organization related models - Updated based on swagger.yaml
@dataclass
class SimpleProjectInfo:
    """Simple project information."""

    create_at: str
    project_id: int
    project_name: str


@dataclass
class OrgInfo:
    """Organization information."""

    org_create_at: str
    org_id: int
    org_name: str
    projects: List[SimpleProjectInfo]
    roles: List[str]


@dataclass
class UserOrgInfoDTO:
    """User organization information - Updated based on swagger.yaml."""

    auth_provider: str
    create_at: str
    email: str
    org_info: OrgInfo
    user_name: str


# Simplified organization model
@dataclass
class SimpleOrgInfo:
    """Simplified organization information."""

    org_name: str
    org_id: int
    org_create_at: str


# Cluster credentials model
@dataclass
class ClusterCredentials:
    """Cluster credentials for database connection."""

    username: str
    password: str
    host: str
    port: int
    status: str


# SKU related models
class SKUType(Enum):
    """SKU type enumeration."""

    SERVERLESS = "serverless"
    DEDICATED = "dedicated"


class EloqModule(Enum):
    """EloqDB module type enumeration."""

    ELOQKV = "eloqkv"
    ELOQDOC = "eloqdoc"


class CloudProvider(Enum):
    """Cloud provider enumeration."""

    AWS = "aws"
    GCP = "gcp"


@dataclass
class SKUInfo:
    """SKU information."""

    sku_id: int
    sku_name: str
    sku_type: str  # "serverless", "dedicated", "unspecified"
    module_type: str  # "EloqSQL", "EloqKV", "EloqDoc"
    version: str
    tx_cpu_limit: float
    tx_memory_mi_limit: float
    tx_ev_gi_limit: float
    tx_pv_gi_limit: float
    log_cpu_limit: float
    log_memory_mi_limit: float
    log_pv_gi_limit: float
    cloud_provider: str  # "AWS", "GCP"
    tx_replica: int
    log_replica: int


@dataclass
class SKUListRequest:
    """Request parameters for listing SKUs."""

    type: SKUType
    eloq_module: EloqModule
    cloud_provider: CloudProvider

    def to_query_params(self) -> Dict[str, str]:
        """Convert request to query parameters."""
        return {
            "type": self.type.value,
            "eloqModule": self.eloq_module.value,
            "cloudProvider": self.cloud_provider.value,
        }


# Cluster creation models
@dataclass
class CreateClusterRequest:
    """Request body for creating a cluster."""

    cluster_name: str  # Required: Cluster display name
    region: str  # Required: Region (e.g., "ap-northeast-1")
    sku_id: int  # Required: SKU ID
    required_zone: Optional[str] = None  # Optional: Availability zone

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for JSON serialization."""
        result = {
            "clusterName": self.cluster_name,
            "region": self.region,
            "skuId": self.sku_id,
        }
        if self.required_zone is not None:
            result["requiredZone"] = self.required_zone
        return result


@dataclass
class OperationResult:
    """Result of an operation (create, delete, etc.)."""

    success: bool  # True if operation succeeded, False otherwise
    message: str  # Human-readable message describing the result
