# modules/generate_kubernetes.py
import os

def get_kubernetes_resources(project_name):
    """Kubernetes module ke resources input leta hai"""
    resources = {
        "eks_cluster": {},
        "node_groups": [],
        "fargate_profiles": []
    }
    
    print("\n☸️ KUBERNETES MODULE CONFIGURATION")
    print("Ab hum EKS cluster, node groups aur fargate profiles ke values input karenge...")
    
    # EKS Cluster Configuration
    print("\n🔹 EKS Cluster Setup:")
    cluster_name = input(f"   Enter EKS cluster name [default: {project_name}-cluster]: ").strip() or f"{project_name}-cluster"
    
    print(f"\n   ⚙️ Configuration for {cluster_name}:")
    
    # Kubernetes Version
    print("\n   Kubernetes Version:")
    print("   1. 1.28 (Latest)")
    print("   2. 1.27")
    print("   3. 1.26")
    print("   4. 1.25")
    version_choice = input("   Select Kubernetes version (1-4) [default: 1]: ").strip() or "1"
    
    k8s_versions = {
        "1": "1.28",
        "2": "1.27", 
        "3": "1.26",
        "4": "1.25"
    }
    kubernetes_version = k8s_versions[version_choice]
    
    # Cluster Configuration
    print("\n   🔧 Cluster Configuration:")
    enable_private_access = input("   Enable private API server endpoint? (y/n) [default: y]: ").strip().lower() or 'y'
    enable_public_access = input("   Enable public API server endpoint? (y/n) [default: y]: ").strip().lower() or 'y'
    
    # Logging Configuration
    print("\n   📝 Logging Configuration:")
    print("   Enable which types of logs?")
    enable_api_logs = input("   API server logs? (y/n) [default: y]: ").strip().lower() or 'y'
    enable_audit_logs = input("   Audit logs? (y/n) [default: y]: ").strip().lower() or 'y'
    enable_authenticator_logs = input("   Authenticator logs? (y/n) [default: y]: ").strip().lower() or 'y'
    enable_controller_manager_logs = input("   Controller manager logs? (y/n) [default: n]: ").strip().lower() or 'n'
    enable_scheduler_logs = input("   Scheduler logs? (y/n) [default: n]: ").strip().lower() or 'n'
    
    # Addons Configuration
    print("\n   🔌 Cluster Addons:")
    enable_kube_proxy = input("   Enable kube-proxy? (y/n) [default: y]: ").strip().lower() or 'y'
    enable_core_dns = input("   Enable CoreDNS? (y/n) [default: y]: ").strip().lower() or 'y'
    enable_vpc_cni = input("   Enable VPC CNI? (y/n) [default: y]: ").strip().lower() or 'y'
    
    resources["eks_cluster"] = {
        "name": cluster_name,
        "kubernetes_version": kubernetes_version,
        "endpoint_private_access": enable_private_access == 'y',
        "endpoint_public_access": enable_public_access == 'y',
        "enabled_cluster_log_types": {
            "api": enable_api_logs == 'y',
            "audit": enable_audit_logs == 'y',
            "authenticator": enable_authenticator_logs == 'y',
            "controllerManager": enable_controller_manager_logs == 'y',
            "scheduler": enable_scheduler_logs == 'y'
        },
        "addons": {
            "kube_proxy": enable_kube_proxy == 'y',
            "core_dns": enable_core_dns == 'y',
            "vpc_cni": enable_vpc_cni == 'y'
        }
    }
    
    # Node Groups Configuration
    print("\n🔹 Node Groups Setup:")
    num_node_groups = int(input("   Kitne node groups banane hain? [default: 2]: ").strip() or "2")
    
    common_instance_types = {
        "1": "t3.medium",
        "2": "t3.large", 
        "3": "m5.large",
        "4": "m5.xlarge",
        "5": "c5.large",
        "6": "r5.large"
    }
    
    for i in range(num_node_groups):
        print(f"\n   🔧 Node Group {i+1}:")
        nodegroup_name = input(f"   Enter node group name [default: {project_name}-ng-{i+1}]: ").strip() or f"{project_name}-ng-{i+1}"
        
        print("\n   Instance Type:")
        print("   1. t3.medium (2 vCPU, 4GB RAM)")
        print("   2. t3.large (2 vCPU, 8GB RAM)")
        print("   3. m5.large (2 vCPU, 8GB RAM)")
        print("   4. m5.xlarge (4 vCPU, 16GB RAM)")
        print("   5. c5.large (2 vCPU, 4GB RAM) - Compute Optimized")
        print("   6. r5.large (2 vCPU, 16GB RAM) - Memory Optimized")
        print("   7. Custom Instance Type")
        
        instance_choice = input("   Select instance type (1-7) [default: 1]: ").strip() or "1"
        
        if instance_choice in common_instance_types:
            instance_type = common_instance_types[instance_choice]
        else:
            instance_type = input("   Enter custom instance type: ").strip()
        
        # Scaling Configuration
        print(f"\n   📈 Scaling Configuration for {nodegroup_name}:")
        min_size = int(input("   Minimum number of nodes [default: 1]: ").strip() or "1")
        max_size = int(input("   Maximum number of nodes [default: 3]: ").strip() or "3")
        desired_size = int(input("   Desired number of nodes [default: 2]: ").strip() or "2")
        
        # Disk Configuration
        print(f"\n   💾 Disk Configuration for {nodegroup_name}:")
        disk_size = int(input("   Node disk size in GB [default: 20]: ").strip() or "20")
        
        # Capacity Type
        print(f"\n   💰 Capacity Type:")
        print("   1. ON_DEMAND (More expensive, no interruption)")
        print("   2. SPOT (Cost effective, can be interrupted)")
        capacity_choice = input("   Select capacity type (1-2) [default: 1]: ").strip() or "1"
        capacity_type = "ON_DEMAND" if capacity_choice == "1" else "SPOT"
        
        # Labels and Taints
        print(f"\n   🏷️ Node Labels (optional):")
        labels_input = input("   Enter node labels as key=value, separated by commas [e.g., environment=prod,team=backend]: ").strip()
        labels = {}
        if labels_input:
            for label in labels_input.split(','):
                if '=' in label:
                    key, value = label.split('=', 1)
                    labels[key.strip()] = value.strip()
        
        print(f"\n   ⚠️ Node Taints (optional):")
        taints_input = input("   Enter node taints as key=value:effect, separated by commas [e.g., dedicated=gpu:NoSchedule]: ").strip()
        taints = []
        if taints_input:
            for taint in taints_input.split(','):
                if '=' in taint and ':' in taint:
                    parts = taint.split('=', 1)
                    key = parts[0].strip()
                    value_effect = parts[1].split(':', 1)
                    value = value_effect[0].strip()
                    effect = value_effect[1].strip()
                    taints.append({
                        "key": key,
                        "value": value,
                        "effect": effect
                    })
        
        node_group = {
            "name": nodegroup_name,
            "instance_type": instance_type,
            "min_size": min_size,
            "max_size": max_size,
            "desired_size": desired_size,
            "disk_size": disk_size,
            "capacity_type": capacity_type,
            "labels": labels,
            "taints": taints
        }
        
        resources["node_groups"].append(node_group)
    
    # Fargate Profiles Configuration
    print("\n🔹 Fargate Profiles Setup:")
    enable_fargate = input("   Enable Fargate profiles? (y/n) [default: y]: ").strip().lower() or 'y'
    
    if enable_fargate == 'y':
        num_fargate_profiles = int(input("   Kitne Fargate profiles banane hain? [default: 2]: ").strip() or "2")
        
        common_fargate_profiles = {
            "1": {"name": "default", "namespace": "default", "purpose": "Default namespace workloads"},
            "2": {"name": "kube-system", "namespace": "kube-system", "purpose": "System workloads"},
            "3": {"name": "monitoring", "namespace": "monitoring", "purpose": "Monitoring stack"},
            "4": {"name": "ci-cd", "namespace": "ci-cd", "purpose": "CI/CD workloads"}
        }
        
        for i in range(num_fargate_profiles):
            print(f"\n   🚀 Fargate Profile {i+1}:")
            print("   Available templates:")
            print("   1. Default Namespace")
            print("   2. kube-system Namespace") 
            print("   3. Monitoring Namespace")
            print("   4. CI/CD Namespace")
            print("   5. Custom Profile")
            
            profile_choice = input("   Select template (1-5) [default: 1]: ").strip() or "1"
            
            if profile_choice in common_fargate_profiles:
                profile_config = common_fargate_profiles[profile_choice]
                profile_name = input(f"   Enter profile name [default: {profile_config['name']}]: ").strip() or profile_config['name']
                namespace = input(f"   Enter namespace [default: {profile_config['namespace']}]: ").strip() or profile_config['namespace']
                purpose = profile_config['purpose']
            else:
                profile_name = input("   Enter profile name: ").strip()
                namespace = input("   Enter namespace: ").strip()
                purpose = input("   Enter profile purpose: ").strip()
            
            # Selector Configuration
            print(f"\n   🔍 Selectors for {profile_name}:")
            num_selectors = int(input("   Kitne selectors add karna hai? [default: 1]: ").strip() or "1")
            
            selectors = []
            for j in range(num_selectors):
                print(f"\n     Selector {j+1}:")
                selector_namespace = input(f"     Namespace [default: {namespace}]: ").strip() or namespace
                
                print("     Labels (optional):")
                labels_input = input("     Enter labels as key=value, separated by commas: ").strip()
                labels = {}
                if labels_input:
                    for label in labels_input.split(','):
                        if '=' in label:
                            key, value = label.split('=', 1)
                            labels[key.strip()] = value.strip()
                
                selectors.append({
                    "namespace": selector_namespace,
                    "labels": labels
                })
            
            fargate_profile = {
                "name": profile_name,
                "namespace": namespace,
                "purpose": purpose,
                "selectors": selectors
            }
            
            resources["fargate_profiles"].append(fargate_profile)
    
    return resources

def generate_kubernetes_main_tf(resources, project_name):
    """Kubernetes module ke liye main.tf content generate karta hai"""
    content = f'''# Main Terraform configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Kubernetes (EKS)

# EKS Cluster
resource "aws_eks_cluster" "{resources['eks_cluster']['name'].replace('-', '_')}" {{
  name     = "{resources['eks_cluster']['name']}"
  version  = "{resources['eks_cluster']['kubernetes_version']}"
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {{
    subnet_ids              = var.cluster_subnet_ids
    endpoint_private_access = {str(resources['eks_cluster']['endpoint_private_access']).lower()}
    endpoint_public_access  = {str(resources['eks_cluster']['endpoint_public_access']).lower()}
    security_group_ids      = var.cluster_security_group_ids
  }}

  enabled_cluster_log_types = [
'''
    
    # Add enabled log types
    enabled_logs = []
    for log_type, enabled in resources['eks_cluster']['enabled_cluster_log_types'].items():
        if enabled:
            enabled_logs.append(f'    "{log_type}"')
    
    content += ',\n'.join(enabled_logs)
    
    content += f'''
  ]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
  ]

  tags = {{
    Name        = "{resources['eks_cluster']['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # EKS Cluster IAM Role
    content += f'''# EKS Cluster IAM Role
resource "aws_iam_role" "eks_cluster" {{
  name = "${{var.project_name}}-eks-cluster-role"

  assume_role_policy = <<POLICY
{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Effect": "Allow",
      "Principal": {{
        "Service": "eks.amazonaws.com"
      }},
      "Action": "sts:AssumeRole"
    }}
  ]
}}
POLICY

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}}

resource "aws_iam_role_policy_attachment" "eks_vpc_resource_controller" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster.name
}}

'''
    
    # Node Group IAM Role
    content += f'''# Node Group IAM Role
resource "aws_iam_role" "eks_node_group" {{
  name = "${{var.project_name}}-eks-node-group-role"

  assume_role_policy = <<POLICY
{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Effect": "Allow",
      "Principal": {{
        "Service": "ec2.amazonaws.com"
      }},
      "Action": "sts:AssumeRole"
    }}
  ]
}}
POLICY

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group.name
}}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group.name
}}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group.name
}}

'''
    
    # Node Groups
    for node_group in resources["node_groups"]:
        node_group_var_name = node_group['name'].replace('-', '_')
        
        content += f'''# Node Group: {node_group['name']}
resource "aws_eks_node_group" "{node_group_var_name}" {{
  cluster_name    = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.name
  node_group_name = "{node_group['name']}"
  node_role_arn   = aws_iam_role.eks_node_group.arn
  subnet_ids      = var.node_group_subnet_ids

  capacity_type  = "{node_group['capacity_type']}"
  instance_types = ["{node_group['instance_type']}"]

  scaling_config {{
    desired_size = {node_group['desired_size']}
    max_size     = {node_group['max_size']}
    min_size     = {node_group['min_size']}
  }}

  disk_size = {node_group['disk_size']}

  update_config {{
    max_unavailable = 1
  }}

'''
        
        # Node Labels
        if node_group['labels']:
            content += '  labels = {\n'
            for key, value in node_group['labels'].items():
                content += f'    "{key}" = "{value}"\n'
            content += '  }\n\n'
        
        # Node Taints
        if node_group['taints']:
            content += '  taint {\n'
            for taint in node_group['taints']:
                content += f'    key    = "{taint["key"]}"\n'
                content += f'    value  = "{taint["value"]}"\n'
                content += f'    effect = "{taint["effect"]}"\n'
            content += '  }\n\n'
        
        content += f'''  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]

  tags = {{
    Name        = "{node_group['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Fargate Profiles
    for fargate_profile in resources["fargate_profiles"]:
        fargate_var_name = fargate_profile['name'].replace('-', '_')
        
        content += f'''# Fargate Profile: {fargate_profile['name']}
resource "aws_eks_fargate_profile" "{fargate_var_name}" {{
  cluster_name           = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.name
  fargate_profile_name   = "{fargate_profile['name']}"
  pod_execution_role_arn = aws_iam_role.eks_fargate_profile.arn
  subnet_ids             = var.fargate_subnet_ids

'''
        
        # Selectors
        content += '  selector {\n'
        for selector in fargate_profile['selectors']:
            content += f'    namespace = "{selector["namespace"]}"\n'
            if selector['labels']:
                content += '    labels = {\n'
                for key, value in selector['labels'].items():
                    content += f'      "{key}" = "{value}"\n'
                content += '    }\n'
        content += '  }\n\n'
        
        content += f'''  tags = {{
    Name        = "{fargate_profile['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Fargate IAM Role
    if resources["fargate_profiles"]:
        content += f'''# Fargate Profile IAM Role
resource "aws_iam_role" "eks_fargate_profile" {{
  name = "${{var.project_name}}-eks-fargate-profile-role"

  assume_role_policy = <<POLICY
{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Effect": "Allow",
      "Principal": {{
        "Service": "eks-fargate-pods.amazonaws.com"
      }},
      "Action": "sts:AssumeRole"
    }}
  ]
}}
POLICY

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy_attachment" "eks_fargate_pod_execution_role_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSFargatePodExecutionRolePolicy"
  role       = aws_iam_role.eks_fargate_profile.name
}}

'''
    
    # EKS Addons
    content += f'''# EKS Addons
'''
    
    if resources['eks_cluster']['addons']['kube_proxy']:
        content += f'''resource "aws_eks_addon" "kube_proxy" {{
  cluster_name = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.name
  addon_name   = "kube-proxy"

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    if resources['eks_cluster']['addons']['core_dns']:
        content += f'''resource "aws_eks_addon" "coredns" {{
  cluster_name = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.name
  addon_name   = "coredns"

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    if resources['eks_cluster']['addons']['vpc_cni']:
        content += f'''resource "aws_eks_addon" "vpc_cni" {{
  cluster_name = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.name
  addon_name   = "vpc-cni"

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    return content

def generate_kubernetes_variables_tf(project_name, resources):
    """Kubernetes module ke liye variables.tf generate karta hai"""
    content = f'''# Variables configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Kubernetes (EKS)

variable "cluster_subnet_ids" {{
  description = "List of subnet IDs for EKS cluster"
  type        = list(string)
}}

variable "node_group_subnet_ids" {{
  description = "List of subnet IDs for node groups"
  type        = list(string)
}}

variable "fargate_subnet_ids" {{
  description = "List of subnet IDs for Fargate profiles"
  type        = list(string)
}}

variable "cluster_security_group_ids" {{
  description = "List of security group IDs for EKS cluster"
  type        = list(string)
}}

variable "environment" {{
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {{
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }}
}}

variable "project_name" {{
  description = "Project name for tagging"
  type        = string
  default     = "{project_name}"
}}

variable "region" {{
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}}

'''
    
    return content

def generate_kubernetes_outputs_tf(resources, project_name):
    """Kubernetes module ke liye outputs.tf generate karta hai"""
    content = f'''# Outputs configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Kubernetes (EKS)

output "cluster_id" {{
  description = "ID of the EKS cluster"
  value       = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.id
}}

output "cluster_arn" {{
  description = "ARN of the EKS cluster"
  value       = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.arn
}}

output "cluster_endpoint" {{
  description = "Endpoint for EKS cluster API server"
  value       = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.endpoint
}}

output "cluster_certificate_authority_data" {{
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.certificate_authority[0].data
}}

output "cluster_security_group_id" {{
  description = "Security group ID attached to the EKS cluster"
  value       = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.vpc_config[0].cluster_security_group_id
}}

output "cluster_oidc_issuer_url" {{
  description = "URL of the OIDC identity provider for the cluster"
  value       = aws_eks_cluster.{resources['eks_cluster']['name'].replace('-', '_')}.identity[0].oidc[0].issuer
}}

'''
    
    # Node Group Outputs
    for node_group in resources["node_groups"]:
        node_group_var_name = node_group['name'].replace('-', '_')
        content += f'''output "{node_group_var_name}_arn" {{
  description = "ARN of the {node_group['name']} node group"
  value       = aws_eks_node_group.{node_group_var_name}.arn
}}

output "{node_group_var_name}_id" {{
  description = "ID of the {node_group['name']} node group"
  value       = aws_eks_node_group.{node_group_var_name}.id
}}

'''
    
    # Fargate Profile Outputs
    for fargate_profile in resources["fargate_profiles"]:
        fargate_var_name = fargate_profile['name'].replace('-', '_')
        content += f'''output "{fargate_var_name}_arn" {{
  description = "ARN of the {fargate_profile['name']} fargate profile"
  value       = aws_eks_fargate_profile.{fargate_var_name}.arn
}}

'''
    
    return content

def generate_kubernetes_module(module_path, project_name):
    """Kubernetes module generate karta hai"""
    print(f"\n🔧 Generating Kubernetes Module for project: {project_name}")
    
    # Resources input
    resources = get_kubernetes_resources(project_name)
    
    # Files generate karte hain
    main_tf_content = generate_kubernetes_main_tf(resources, project_name)
    variables_tf_content = generate_kubernetes_variables_tf(project_name, resources)
    outputs_tf_content = generate_kubernetes_outputs_tf(resources, project_name)
    
    # Files save karte hain
    with open(os.path.join(module_path, "main.tf"), 'w') as f:
        f.write(main_tf_content)
    print("✅ Created: main.tf")
    
    with open(os.path.join(module_path, "variables.tf"), 'w') as f:
        f.write(variables_tf_content)
    print("✅ Created: variables.tf")
    
    with open(os.path.join(module_path, "outputs.tf"), 'w') as f:
        f.write(outputs_tf_content)
    print("✅ Created: outputs.tf")
    
    # Resources summary
    print(f"\n📊 Kubernetes Resources Summary:")
    print(f"   • EKS Cluster: {resources['eks_cluster']['name']} (K8s {resources['eks_cluster']['kubernetes_version']})")
    print(f"   • Node Groups: {len(resources['node_groups'])}")
    print(f"   • Fargate Profiles: {len(resources['fargate_profiles'])}")
    
    for node_group in resources["node_groups"]:
        print(f"   • Node Group: {node_group['name']} - {node_group['instance_type']} ({node_group['capacity_type']})")
        print(f"     - Scaling: {node_group['min_size']}-{node_group['max_size']} nodes")
    
    for fargate_profile in resources["fargate_profiles"]:
        print(f"   • Fargate Profile: {fargate_profile['name']} - {fargate_profile['namespace']} namespace")