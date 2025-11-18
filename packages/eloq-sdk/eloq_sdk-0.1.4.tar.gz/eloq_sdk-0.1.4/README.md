# Eloq SDK Python

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.2-blue.svg)](https://github.com/monographdb/eloq-sdk-python)

Python SDK for interacting with the Eloq API. This SDK provides a simple and intuitive interface for managing Eloq clusters, SKUs, and organizations.

## Features

- **Type-safe API**: Uses Pydantic dataclasses for structured input/output
- **Enum-based parameters**: No need to guess parameter values - use enums for type safety
- **Automatic error handling**: Comprehensive exception handling with clear error messages
- **Simple result objects**: Operations return clear success/failure results
- **Auto-detection**: Automatically retrieves organization and project IDs from user context

## Installation

### Using pip

```bash
pip install eloq-sdk
```

### Development Installation

```bash
git clone https://github.com/monographdb/eloq-sdk-python.git
cd eloq-sdk-python
pip install -e ".[dev]"
```

### Requirements

- Python 3.7 or higher
- `requests>=2.25.0`
- `pydantic>=1.8.0`

## Quick Start

```python
from eloq_sdk import EloqAPI
from eloq_sdk import schema

# Initialize client from environment variable
client = EloqAPI.from_environ()

# Get organization information
org_info = client.info()
print(f"Organization: {org_info.org_info.org_name}")

# List clusters
clusters = client.clusters()
print(f"Found {clusters.total} clusters")
```

### Environment Setup

Set the `ELOQ_API_KEY` environment variable:

```bash
export ELOQ_API_KEY="your-api-key-here"
```

## Authentication & Client Initialization

The SDK provides three ways to initialize the client:

### 1. From Environment Variable

```python
from eloq_sdk import EloqAPI

client = EloqAPI.from_environ()
```

This reads the API key from the `ELOQ_API_KEY` environment variable.

### 2. From API Key

```python
from eloq_sdk import EloqAPI

client = EloqAPI.from_key("your-api-key-here")
```

### 3. From API Key and Custom URL

```python
from eloq_sdk import EloqAPI

client = EloqAPI.from_key_and_url(
    "your-api-key-here",
    "https://api-prod.eloqdata.com/api/v1/"
)
```

## API Reference

### Organization Management

#### `info()`

Get detailed organization and project information for the current user.

**Input**: None (automatically detected from user context)

**Output**: `UserOrgInfoDTO` object containing:
- `auth_provider` (str): Authentication provider (e.g., "github")
- `create_at` (str): User account creation timestamp
- `email` (str): User email address
- `org_info` (OrgInfo): Organization information object
  - `org_id` (int): Organization ID
  - `org_name` (str): Organization name
  - `org_create_at` (str): Organization creation timestamp
  - `projects` (List[SimpleProjectInfo]): List of projects
  - `roles` (List[str]): User roles
- `user_name` (str): Username

**Example**:

```python
org_info = client.info()
print(f"User: {org_info.user_name}")
print(f"Organization: {org_info.org_info.org_name}")
print(f"Projects: {len(org_info.org_info.projects)}")
```

#### `org()`

Get simplified organization information.

**Input**: None

**Output**: `SimpleOrgInfo` object containing:
- `org_name` (str): Organization name
- `org_id` (int): Organization ID
- `org_create_at` (str): Organization creation timestamp

**Example**:

```python
org = client.org()
print(f"Organization: {org.org_name}")
print(f"ID: {org.org_id}")
```

### Cluster Management

#### `clusters(page=1, per_page=20)`

List all clusters in the current project.

**Input**:
- `page` (int, optional): Page number for pagination (default: 1)
- `per_page` (int, optional): Number of items per page (default: 20)

**Output**: `ClusterList` object containing:
- `cluster_list` (List[ClusterListItem]): List of cluster items
- `total` (int): Total number of clusters

**ClusterListItem** fields:
- `cloud_provider` (str): Cloud provider (e.g., "AWS", "GCP")
- `cluster_name` (str): Cluster name
- `create_at` (str): Creation timestamp
- `module_type` (str): Module type (e.g., "eloqkv", "eloqdoc")
- `region` (str): Region
- `status` (str): Cluster status
- `version` (str): Version
- `zone` (str): Availability zone

**Example**:

```python
clusters = client.clusters(page=1, per_page=10)
print(f"Total clusters: {clusters.total}")
for cluster in clusters.cluster_list:
    print(f"- {cluster.cluster_name} ({cluster.status})")
```

#### `cluster(cluster_name)`

Get detailed information about a specific cluster.

**Input**:
- `cluster_name` (str): Cluster display name

**Output**: `DescClusterDTO` object containing:
- `admin_password` (str): Base64-encoded admin password
- `admin_user` (str): Base64-encoded admin username
- `cloud_provider` (str): Cloud provider
- `cluster_deploy_mode` (str): Deployment mode
- `create_at` (str): Creation timestamp
- `display_cluster_name` (str): Display name
- `elb_addr` (str): Load balancer address
- `elb_port` (int): Load balancer port
- `elb_state` (str): Load balancer state
- `log_cpu_limit` (float): Log CPU limit
- `log_memory_mi_limit` (float): Log memory limit (Mi)
- `log_replica` (int): Log replica count
- `module_type` (str): Module type
- `org_name` (str): Organization name
- `project_name` (str): Project name
- `region` (str): Region
- `status` (str): Cluster status
- `tx_cpu_limit` (float): Transaction CPU limit
- `tx_memory_mi_limit` (float): Transaction memory limit (Mi)
- `tx_replica` (int): Transaction replica count
- `version` (str): Version
- `zone` (str): Availability zone

**Example**:

```python
cluster_info = client.cluster("my-cluster")
print(f"Status: {cluster_info.status}")
print(f"Region: {cluster_info.region}")
print(f"Module: {cluster_info.module_type}")
```

#### `cluster_create(cluster_name, region, sku_id)`

Create a new cluster.

**Input**:
- `cluster_name` (str): Cluster display name (required)
- `region` (str): Region where the cluster will be created, e.g., "us-west-1" (required)
- `sku_id` (int): SKU ID for the cluster (required). Use `get_skus()` to find available SKU IDs

**Output**: `OperationResult` object containing:
- `success` (bool): True if operation succeeded, False otherwise
- `message` (str): Human-readable message describing the result

**Example**:

```python
from eloq_sdk import schema

# First, get available SKUs
skus = client.get_skus(
    sku_type=schema.SKUType.SERVERLESS,
    eloq_module=schema.EloqModule.ELOQKV,
    cloud_provider=schema.CloudProvider.AWS
)

# Create the cluster
result = client.cluster_create(
    cluster_name="my-cluster",
    region="us-west-1",
    sku_id=skus[0].sku_id
)

if result.success:
    print(f"✅ {result.message}")
else:
    print(f"❌ {result.message}")
```

#### `cluster_delete(cluster_name)`

Delete a cluster. The cluster must be in 'available' status to be deleted.

**Input**:
- `cluster_name` (str): Cluster display name (required)

**Output**: `OperationResult` object containing:
- `success` (bool): True if operation succeeded, False otherwise
- `message` (str): Human-readable message describing the result

**Example**:

```python
result = client.cluster_delete("my-cluster")

if result.success:
    print(f"✅ {result.message}")
else:
    print(f"❌ {result.message}")
```

**Note**: The cluster must be in 'available' status to be deleted.

#### `cluster_credentials(cluster_name)`

Get cluster credentials (username and password) for database connection. The admin user ID and password are automatically decoded from base64 encoding.

**Input**:
- `cluster_name` (str): Cluster display name (required)

**Output**: `ClusterCredentials` object containing:
- `username` (str): Decoded admin username
- `password` (str): Decoded admin password
- `host` (str): Load balancer address
- `port` (int): Load balancer port
- `status` (str): Cluster status

**Example**:

```python
credentials = client.cluster_credentials("my-cluster")
print(f"Username: {credentials.username}")
print(f"Password: {credentials.password}")
print(f"Host: {credentials.host}:{credentials.port}")
```

### SKU Management

#### `get_skus(sku_type, eloq_module, cloud_provider)`

Get available SKUs filtered by SKU type, EloqDB module type, and cloud provider. Only SKUs available in the user's subscription plan are returned.

**Input**:
- `sku_type` (SKUType enum): SKU type filter
  - `SKUType.SERVERLESS`: Serverless SKU
  - `SKUType.DEDICATED`: Dedicated SKU
- `eloq_module` (EloqModule enum): EloqDB module type filter
  - `EloqModule.ELOQKV`: EloqKV module
  - `EloqModule.ELOQDOC`: EloqDoc module
- `cloud_provider` (CloudProvider enum): Cloud provider filter
  - `CloudProvider.AWS`: Amazon Web Services
  - `CloudProvider.GCP`: Google Cloud Platform

**Output**: List of `SKUInfo` objects, each containing:
- `sku_id` (int): SKU ID
- `sku_name` (str): SKU name
- `sku_type` (str): SKU type ("serverless", "dedicated", "unspecified")
- `module_type` (str): Module type ("EloqSQL", "EloqKV", "EloqDoc")
- `version` (str): Version
- `tx_cpu_limit` (float): Transaction CPU limit
- `tx_memory_mi_limit` (float): Transaction memory limit (Mi)
- `tx_ev_gi_limit` (float): Transaction ephemeral volume limit (Gi)
- `tx_pv_gi_limit` (float): Transaction persistent volume limit (Gi)
- `log_cpu_limit` (float): Log CPU limit
- `log_memory_mi_limit` (float): Log memory limit (Mi)
- `log_pv_gi_limit` (float): Log persistent volume limit (Gi)
- `cloud_provider` (str): Cloud provider ("AWS", "GCP")
- `tx_replica` (int): Transaction replica count
- `log_replica` (int): Log replica count

**Example**:

```python
from eloq_sdk import schema

skus = client.get_skus(
    sku_type=schema.SKUType.SERVERLESS,
    eloq_module=schema.EloqModule.ELOQKV,
    cloud_provider=schema.CloudProvider.AWS
)

print(f"Found {len(skus)} available SKUs:")
for sku in skus:
    print(f"  - SKU ID: {sku.sku_id}, Name: {sku.sku_name}")
    print(f"    Type: {sku.sku_type}, Module: {sku.module_type}")
    print(f"    Cloud: {sku.cloud_provider}")
```

## Data Structures

### OperationResult

Result object returned by create and delete operations.

```python
@dataclass
class OperationResult:
    success: bool  # True if operation succeeded, False otherwise
    message: str   # Human-readable message describing the result
```

### SKUInfo

SKU information object.

```python
@dataclass
class SKUInfo:
    sku_id: int
    sku_name: str
    sku_type: str
    module_type: str
    version: str
    tx_cpu_limit: float
    tx_memory_mi_limit: float
    tx_ev_gi_limit: float
    tx_pv_gi_limit: float
    log_cpu_limit: float
    log_memory_mi_limit: float
    log_pv_gi_limit: float
    cloud_provider: str
    tx_replica: int
    log_replica: int
```

### ClusterList

List of clusters with pagination information.

```python
@dataclass
class ClusterList:
    cluster_list: List[ClusterListItem]
    total: int
```

### DescClusterDTO

Detailed cluster information.

```python
@dataclass
class DescClusterDTO:
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
```

### ClusterCredentials

Cluster credentials for database connection.

```python
@dataclass
class ClusterCredentials:
    username: str
    password: str
    host: str
    port: int
    status: str
```

### UserOrgInfoDTO

User organization information.

```python
@dataclass
class UserOrgInfoDTO:
    auth_provider: str
    create_at: str
    email: str
    org_info: OrgInfo
    user_name: str
```

### Enums

#### SKUType

```python
class SKUType(Enum):
    SERVERLESS = "serverless"
    DEDICATED = "dedicated"
```

#### EloqModule

```python
class EloqModule(Enum):
    ELOQKV = "eloqkv"
    ELOQDOC = "eloqdoc"
```

#### CloudProvider

```python
class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

### Exception Types

- `EloqAPIError`: Base exception for all API errors
- `EloqAuthenticationError`: Authentication failed (401)
- `EloqPermissionError`: Permission denied (403)
- `EloqNotFoundError`: Resource not found (404)
- `EloqRateLimitError`: Rate limit exceeded (429)
- `EloqValidationError`: Invalid request (400)
- `EloqServerError`: Server error (500+)

### Handling Errors

```python
from eloq_sdk import EloqAPI
from eloq_sdk.exceptions import EloqAPIError, EloqNotFoundError

try:
    cluster = client.cluster("non-existent-cluster")
except EloqNotFoundError:
    print("Cluster not found")
except EloqAPIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Operation Results

For create and delete operations, errors are automatically handled and returned as `OperationResult` objects:

```python
result = client.cluster_create(
    cluster_name="my-cluster",
    region="us-west-1",
    sku_id=123
)

if not result.success:
    print(f"Operation failed: {result.message}")
```

## Complete Examples

### Full Workflow: Get SKUs → Create Cluster → Check Status → Delete Cluster

```python
from eloq_sdk import EloqAPI
from eloq_sdk import schema

# Initialize client
client = EloqAPI.from_environ()

# Step 1: Get available SKUs
skus = client.get_skus(
    sku_type=schema.SKUType.SERVERLESS,
    eloq_module=schema.EloqModule.ELOQKV,
    cloud_provider=schema.CloudProvider.AWS
)

if not skus:
    print("No SKUs available")
    exit(1)

# Step 2: Create cluster
result = client.cluster_create(
    cluster_name="my-cluster",
    region="us-west-1",
    sku_id=skus[0].sku_id
)

if not result.success:
    print(f"Failed to create cluster: {result.message}")
    exit(1)

print(f"✅ {result.message}")

# Step 3: Check cluster status
cluster_info = client.cluster("my-cluster")
print(f"Cluster status: {cluster_info.status}")

# Step 4: Get credentials
credentials = client.cluster_credentials("my-cluster")
print(f"Connection: {credentials.host}:{credentials.port}")

# Step 5: Delete cluster (when done)
result = client.cluster_delete("my-cluster")
if result.success:
    print(f"✅ {result.message}")
```

### More Examples

See the `example/` directory for additional examples:

- `test_orginfo.py`: Get organization information
- `test_cluster.py`: List and manage clusters
- `test_skus.py`: Get available SKUs
- `test_create_cluster.py`: Create a new cluster
- `test_delete_cluster.py`: Delete a cluster

## Requirements

- Python 3.7 or higher
- `requests>=2.25.0`
- `pydantic>=1.8.0`

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Links

- **Homepage**: https://github.com/monographdb/eloq-sdk-python
- **Repository**: https://github.com/monographdb/eloq-sdk-python
- **Issues**: https://github.com/monographdb/eloq-sdk-python/issues

