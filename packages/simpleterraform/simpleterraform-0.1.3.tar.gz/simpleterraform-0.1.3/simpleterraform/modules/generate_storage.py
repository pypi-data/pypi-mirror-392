# modules/generate_storage.py
import os

def get_storage_resources(project_name):
    """Storage module ke resources input leta hai"""
    resources = {
        "s3_buckets": [],
        "ebs_volumes": [],
        "efs_file_systems": []
    }
    
    print("\n📊 STORAGE MODULE CONFIGURATION")
    print("Ab hum S3 buckets, EBS volumes, aur EFS file systems ke values input karenge...")
    
    # S3 Buckets Configuration
    print("\n🔹 S3 Buckets Setup:")
    num_s3_buckets = int(input("   Kitne S3 buckets banane hain? [default: 1]: ").strip() or "1")
    
    common_bucket_use_cases = {
        "1": {"name": "web-static", "purpose": "Static website hosting"},
        "2": {"name": "app-logs", "purpose": "Application logs storage"},
        "3": {"name": "data-backup", "purpose": "Data backups and archives"},
        "4": {"name": "media-assets", "purpose": "Media files and assets"},
        "5": {"name": "config-files", "purpose": "Configuration files storage"}
    }
    
    for i in range(num_s3_buckets):
        print(f"\n   🪣 S3 Bucket {i+1}:")
        print("   Available templates:")
        print("   1. Web Static Hosting")
        print("   2. Application Logs")
        print("   3. Data Backup")
        print("   4. Media Assets")
        print("   5. Config Files")
        print("   6. Custom Bucket")
        
        bucket_choice = input("   Select template (1-6) [default: 1]: ").strip() or "1"
        
        if bucket_choice in common_bucket_use_cases:
            bucket_config = common_bucket_use_cases[bucket_choice]
            bucket_name = input(f"   Enter bucket name [default: {project_name}-{bucket_config['name']}]: ").strip() or f"{project_name}-{bucket_config['name']}"
            bucket_purpose = bucket_config['purpose']
        else:
            bucket_name = input("   Enter bucket name: ").strip()
            bucket_purpose = input("   Enter bucket purpose: ").strip()
        
        # Bucket Configuration
        print(f"\n   ⚙️ Configuration for {bucket_name}:")
        
        # Versioning
        enable_versioning = input("   Enable versioning? (y/n) [default: y]: ").strip().lower() or 'y'
        
        # Encryption
        print("\n   🔐 Encryption:")
        enable_encryption = input("   Enable server-side encryption? (y/n) [default: y]: ").strip().lower() or 'y'
        encryption_type = "AES256"
        if enable_encryption == 'y':
            print("   Encryption type:")
            print("   1. SSE-S3 (AWS Managed Keys)")
            print("   2. SSE-KMS (AWS KMS)")
            encryption_choice = input("   Select encryption type (1-2) [default: 1]: ").strip() or "1"
            encryption_type = "AES256" if encryption_choice == "1" else "aws:kms"
        
        # Lifecycle Rules
        print("\n   📅 Lifecycle Rules:")
        enable_lifecycle = input("   Enable lifecycle rules? (y/n) [default: y]: ").strip().lower() or 'y'
        
        lifecycle_rules = []
        if enable_lifecycle == 'y':
            print("   Lifecycle configuration:")
            
            # Transition to IA
            enable_ia_transition = input("   Transition to Standard-IA after days [default: 30, 0 to disable]: ").strip() or "30"
            if enable_ia_transition != "0":
                lifecycle_rules.append({
                    "name": "transition_to_ia",
                    "transition_days": int(enable_ia_transition),
                    "storage_class": "STANDARD_IA"
                })
            
            # Transition to Glacier
            enable_glacier_transition = input("   Transition to Glacier after days [default: 90, 0 to disable]: ").strip() or "90"
            if enable_glacier_transition != "0":
                lifecycle_rules.append({
                    "name": "transition_to_glacier",
                    "transition_days": int(enable_glacier_transition),
                    "storage_class": "GLACIER"
                })
            
            # Expiration
            enable_expiration = input("   Expire objects after days [default: 365, 0 to disable]: ").strip() or "365"
            if enable_expiration != "0":
                lifecycle_rules.append({
                    "name": "object_expiration",
                    "expiration_days": int(enable_expiration)
                })
        
        # Public Access
        print("\n   🌐 Public Access:")
        block_public_access = input("   Block all public access? (y/n) [default: y]: ").strip().lower() or 'y'
        
        # Static Website Hosting
        enable_website = input("   Enable static website hosting? (y/n) [default: n]: ").strip().lower() or 'n'
        
        website_config = {}
        if enable_website == 'y':
            index_document = input("   Index document [default: index.html]: ").strip() or "index.html"
            error_document = input("   Error document [default: error.html]: ").strip() or "error.html"
            website_config = {
                "index_document": index_document,
                "error_document": error_document
            }
        
        s3_bucket = {
            "name": bucket_name,
            "purpose": bucket_purpose,
            "versioning": enable_versioning == 'y',
            "encryption": enable_encryption == 'y',
            "encryption_type": encryption_type,
            "lifecycle_rules": lifecycle_rules,
            "block_public_access": block_public_access == 'y',
            "website_hosting": enable_website == 'y',
            "website_config": website_config
        }
        
        resources["s3_buckets"].append(s3_bucket)
    
    # EBS Volumes Configuration
    print("\n🔹 EBS Volumes Setup:")
    num_ebs_volumes = int(input("   Kitne EBS volumes banane hain? [default: 1]: ").strip() or "1")
    
    common_volume_use_cases = {
        "1": {"name": "root-volume", "size": 20, "type": "gp3", "purpose": "Root volume for instances"},
        "2": {"name": "data-volume", "size": 50, "type": "gp3", "purpose": "Data storage volume"},
        "3": {"name": "backup-volume", "size": 100, "type": "st1", "purpose": "Backup and archive storage"},
        "4": {"name": "high-iops-volume", "size": 30, "type": "io2", "purpose": "High performance database"}
    }
    
    for i in range(num_ebs_volumes):
        print(f"\n   💾 EBS Volume {i+1}:")
        print("   Available templates:")
        print("   1. Root Volume (20GB gp3)")
        print("   2. Data Volume (50GB gp3)")
        print("   3. Backup Volume (100GB st1)")
        print("   4. High IOPS Volume (30GB io2)")
        print("   5. Custom Volume")
        
        volume_choice = input("   Select template (1-5) [default: 1]: ").strip() or "1"
        
        if volume_choice in common_volume_use_cases:
            volume_config = common_volume_use_cases[volume_choice]
            volume_name = input(f"   Enter volume name [default: {project_name}-{volume_config['name']}]: ").strip() or f"{project_name}-{volume_config['name']}"
            volume_size = volume_config['size']
            volume_type = volume_config['type']
            volume_purpose = volume_config['purpose']
        else:
            volume_name = input("   Enter volume name: ").strip()
            volume_size = int(input("   Enter volume size in GB [default: 20]: ").strip() or "20")
            volume_type = input("   Enter volume type (gp2/gp3/io1/io2/st1/sc1) [default: gp3]: ").strip() or "gp3"
            volume_purpose = input("   Enter volume purpose: ").strip()
        
        # Advanced EBS Configuration
        print(f"\n   ⚙️ Advanced Configuration for {volume_name}:")
        
        # IOPS (for provisioned IOPS volumes)
        iops = None
        if volume_type in ["io1", "io2"]:
            iops = int(input("   Enter provisioned IOPS [default: 100]: ").strip() or "100")
        
        # Throughput (for gp3)
        throughput = None
        if volume_type == "gp3":
            throughput = int(input("   Enter throughput in MB/s [default: 125]: ").strip() or "125")
        
        # Encryption
        enable_encryption = input("   Enable encryption? (y/n) [default: y]: ").strip().lower() or 'y'
        
        # Multi-attach (for io1/io2)
        multi_attach = False
        if volume_type in ["io1", "io2"]:
            multi_attach = input("   Enable multi-attach? (y/n) [default: n]: ").strip().lower() == 'y'
        
        ebs_volume = {
            "name": volume_name,
            "size": volume_size,
            "type": volume_type,
            "purpose": volume_purpose,
            "iops": iops,
            "throughput": throughput,
            "encrypted": enable_encryption == 'y',
            "multi_attach": multi_attach
        }
        
        resources["ebs_volumes"].append(ebs_volume)
    
    # EFS File Systems Configuration
    print("\n🔹 EFS File Systems Setup:")
    num_efs_systems = int(input("   Kitne EFS file systems banane hain? [default: 1]: ").strip() or "1")
    
    for i in range(num_efs_systems):
        print(f"\n   📁 EFS File System {i+1}:")
        efs_name = input(f"   Enter EFS name [default: {project_name}-efs-{i+1}]: ").strip() or f"{project_name}-efs-{i+1}"
        
        print(f"\n   ⚙️ Configuration for {efs_name}:")
        
        # Performance Mode
        print("   Performance Mode:")
        print("   1. General Purpose (default)")
        print("   2. Max I/O")
        perf_mode_choice = input("   Select performance mode (1-2) [default: 1]: ").strip() or "1"
        performance_mode = "generalPurpose" if perf_mode_choice == "1" else "maxIO"
        
        # Throughput Mode
        print("\n   Throughput Mode:")
        print("   1. Bursting (default)")
        print("   2. Provisioned")
        throughput_choice = input("   Select throughput mode (1-2) [default: 1]: ").strip() or "1"
        throughput_mode = "bursting" if throughput_choice == "1" else "provisioned"
        
        provisioned_throughput = None
        if throughput_mode == "provisioned":
            provisioned_throughput = int(input("   Enter provisioned throughput in MB/s [default: 50]: ").strip() or "50")
        
        # Encryption
        enable_encryption = input("   Enable encryption at rest? (y/n) [default: y]: ").strip().lower() or 'y'
        
        # Lifecycle Policy
        print("\n   📅 Lifecycle Policy:")
        print("   1. None")
        print("   2. After 14 days")
        print("   3. After 30 days")
        print("   4. After 60 days")
        print("   5. After 90 days")
        lifecycle_choice = input("   Select lifecycle policy (1-5) [default: 3]: ").strip() or "3"
        
        lifecycle_policies = {
            "1": [],
            "2": [{"transition_to_ia": "AFTER_14_DAYS"}],
            "3": [{"transition_to_ia": "AFTER_30_DAYS"}],
            "4": [{"transition_to_ia": "AFTER_60_DAYS"}],
            "5": [{"transition_to_ia": "AFTER_90_DAYS"}]
        }
        lifecycle_policy = lifecycle_policies[lifecycle_choice]
        
        efs_system = {
            "name": efs_name,
            "performance_mode": performance_mode,
            "throughput_mode": throughput_mode,
            "provisioned_throughput": provisioned_throughput,
            "encrypted": enable_encryption == 'y',
            "lifecycle_policy": lifecycle_policy
        }
        
        resources["efs_file_systems"].append(efs_system)
    
    return resources

def generate_storage_main_tf(resources, project_name):
    """Storage module ke liye main.tf content generate karta hai"""
    content = f'''# Main Terraform configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Storage

'''
    
    # S3 Buckets
    for bucket in resources["s3_buckets"]:
        bucket_var_name = bucket['name'].replace('-', '_').replace('.', '_')
        
        content += f'''# S3 Bucket: {bucket['name']}
resource "aws_s3_bucket" "{bucket_var_name}" {{
  bucket = "{bucket['name']}"

  tags = {{
    Name        = "{bucket['name']}"
    Purpose     = "{bucket['purpose']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
        
        # Versioning
        if bucket['versioning']:
            content += f'''resource "aws_s3_bucket_versioning" "{bucket_var_name}" {{
  bucket = aws_s3_bucket.{bucket_var_name}.id

  versioning_configuration {{
    status = "Enabled"
  }}
}}

'''
        
        # Server-Side Encryption
        if bucket['encryption']:
            content += f'''resource "aws_s3_bucket_server_side_encryption_configuration" "{bucket_var_name}" {{
  bucket = aws_s3_bucket.{bucket_var_name}.id

  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "{bucket['encryption_type']}"
    }}
  }}
}}

'''
        
        # Lifecycle Rules
        if bucket['lifecycle_rules']:
            content += f'''resource "aws_s3_bucket_lifecycle_configuration" "{bucket_var_name}" {{
  bucket = aws_s3_bucket.{bucket_var_name}.id

'''
            for rule in bucket['lifecycle_rules']:
                if 'transition_days' in rule:
                    content += f'''  rule {{
    id     = "{rule['name']}"
    status = "Enabled"

    transition {{
      days          = {rule['transition_days']}
      storage_class = "{rule['storage_class']}"
    }}

    noncurrent_version_transition {{
      noncurrent_days = {rule['transition_days'] + 30}
      storage_class   = "{rule['storage_class']}"
    }}
  }}

'''
                elif 'expiration_days' in rule:
                    content += f'''  rule {{
    id     = "{rule['name']}"
    status = "Enabled"

    expiration {{
      days = {rule['expiration_days']}
    }}

    noncurrent_version_expiration {{
      noncurrent_days = {rule['expiration_days'] + 30}
    }}
  }}

'''
            content += "}\n\n"
        
        # Public Access Block
        if bucket['block_public_access']:
            content += f'''resource "aws_s3_bucket_public_access_block" "{bucket_var_name}" {{
  bucket = aws_s3_bucket.{bucket_var_name}.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

'''
        
        # Website Configuration
        if bucket['website_hosting']:
            content += f'''resource "aws_s3_bucket_website_configuration" "{bucket_var_name}" {{
  bucket = aws_s3_bucket.{bucket_var_name}.id

  index_document {{
    suffix = "{bucket['website_config']['index_document']}"
  }}

  error_document {{
    key = "{bucket['website_config']['error_document']}"
  }}
}}

'''
    
    # EBS Volumes
    for volume in resources["ebs_volumes"]:
        volume_var_name = volume['name'].replace('-', '_')
        
        content += f'''# EBS Volume: {volume['name']}
resource "aws_ebs_volume" "{volume_var_name}" {{
  availability_zone = var.availability_zone
  size              = {volume['size']}
  type              = "{volume['type']}"
  encrypted         = {str(volume['encrypted']).lower()}

'''
        
        if volume['iops']:
            content += f'  iops             = {volume["iops"]}\n'
        
        if volume['throughput']:
            content += f'  throughput       = {volume["throughput"]}\n'
        
        if volume['multi_attach']:
            content += '  multi_attach_enabled = true\n'
        
        content += f'''
  tags = {{
    Name        = "{volume['name']}"
    Purpose     = "{volume['purpose']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # EFS File Systems
    for efs in resources["efs_file_systems"]:
        efs_var_name = efs['name'].replace('-', '_')
        
        content += f'''# EFS File System: {efs['name']}
resource "aws_efs_file_system" "{efs_var_name}" {{
  creation_token = "{efs['name']}"
  
  performance_mode = "{efs['performance_mode']}"
  throughput_mode  = "{efs['throughput_mode']}"
  encrypted        = {str(efs['encrypted']).lower()}

'''
        
        if efs['provisioned_throughput']:
            content += f'  provisioned_throughput_in_mibps = {efs["provisioned_throughput"]}\n'
        
        # Lifecycle Policy
        if efs['lifecycle_policy']:
            content += f'''
  lifecycle_policy {{
    transition_to_ia = "{efs['lifecycle_policy'][0]['transition_to_ia']}"
  }}
'''
        
        content += f'''
  tags = {{
    Name        = "{efs['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
        
        # EFS Mount Targets (need to be in each AZ)
        content += f'''# EFS Mount Targets for {efs['name']}
resource "aws_efs_mount_target" "{efs_var_name}" {{
  count = length(var.subnet_ids)

  file_system_id  = aws_efs_file_system.{efs_var_name}.id
  subnet_id       = var.subnet_ids[count.index]
  security_groups = var.efs_security_group_ids
}}

'''
    
    return content

def generate_storage_variables_tf(project_name, resources):
    """Storage module ke liye variables.tf generate karta hai"""
    content = f'''# Variables configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Storage

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

variable "availability_zone" {{
  description = "Availability zone for EBS volumes"
  type        = string
  default     = "us-east-1a"
}}

variable "subnet_ids" {{
  description = "List of subnet IDs for EFS mount targets"
  type        = list(string)
  default     = []
}}

variable "efs_security_group_ids" {{
  description = "List of security group IDs for EFS"
  type        = list(string)
  default     = []
}}

'''
    
    return content

def generate_storage_outputs_tf(resources, project_name):
    """Storage module ke liye outputs.tf generate karta hai"""
    content = f'''# Outputs configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Storage

'''
    
    # S3 Bucket Outputs
    for bucket in resources["s3_buckets"]:
        bucket_var_name = bucket['name'].replace('-', '_').replace('.', '_')
        content += f'''output "{bucket_var_name}_id" {{
  description = "ID of the {bucket['name']} S3 bucket"
  value       = aws_s3_bucket.{bucket_var_name}.id
}}

output "{bucket_var_name}_arn" {{
  description = "ARN of the {bucket['name']} S3 bucket"
  value       = aws_s3_bucket.{bucket_var_name}.arn
}}

output "{bucket_var_name}_bucket_domain_name" {{
  description = "Bucket domain name of {bucket['name']}"
  value       = aws_s3_bucket.{bucket_var_name}.bucket_domain_name
}}

'''
        if bucket['website_hosting']:
            content += f'''output "{bucket_var_name}_website_endpoint" {{
  description = "Website endpoint for {bucket['name']}"
  value       = aws_s3_bucket_website_configuration.{bucket_var_name}.website_endpoint
}}

'''
    
    # EBS Volume Outputs
    for volume in resources["ebs_volumes"]:
        volume_var_name = volume['name'].replace('-', '_')
        content += f'''output "{volume_var_name}_id" {{
  description = "ID of the {volume['name']} EBS volume"
  value       = aws_ebs_volume.{volume_var_name}.id
}}

output "{volume_var_name}_arn" {{
  description = "ARN of the {volume['name']} EBS volume"
  value       = aws_ebs_volume.{volume_var_name}.arn
}}

output "{volume_var_name}_size" {{
  description = "Size of the {volume['name']} EBS volume in GB"
  value       = aws_ebs_volume.{volume_var_name}.size
}}

'''
    
    # EFS Outputs
    for efs in resources["efs_file_systems"]:
        efs_var_name = efs['name'].replace('-', '_')
        content += f'''output "{efs_var_name}_id" {{
  description = "ID of the {efs['name']} EFS file system"
  value       = aws_efs_file_system.{efs_var_name}.id
}}

output "{efs_var_name}_arn" {{
  description = "ARN of the {efs['name']} EFS file system"
  value       = aws_efs_file_system.{efs_var_name}.arn
}}

output "{efs_var_name}_dns_name" {{
  description = "DNS name of the {efs['name']} EFS file system"
  value       = aws_efs_file_system.{efs_var_name}.dns_name
}}

'''
    
    return content

def generate_storage_module(module_path, project_name):
    """Storage module generate karta hai"""
    print(f"\n🔧 Generating Storage Module for project: {project_name}")
    
    # Resources input
    resources = get_storage_resources(project_name)
    
    # Files generate karte hain
    main_tf_content = generate_storage_main_tf(resources, project_name)
    variables_tf_content = generate_storage_variables_tf(project_name, resources)
    outputs_tf_content = generate_storage_outputs_tf(resources, project_name)
    
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
    print(f"\n📊 Storage Resources Summary:")
    print(f"   • S3 Buckets: {len(resources['s3_buckets'])}")
    print(f"   • EBS Volumes: {len(resources['ebs_volumes'])}")
    print(f"   • EFS File Systems: {len(resources['efs_file_systems'])}")
    
    for bucket in resources["s3_buckets"]:
        print(f"   • S3: {bucket['name']} - {bucket['purpose']}")
    
    for volume in resources["ebs_volumes"]:
        print(f"   • EBS: {volume['name']} - {volume['size']}GB {volume['type']}")
    
    for efs in resources["efs_file_systems"]:
        print(f"   • EFS: {efs['name']} - {efs['performance_mode']}")