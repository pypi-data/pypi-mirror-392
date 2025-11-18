# modules/generate_database.py
import os

def get_database_resources(project_name):
    """Database module ke resources input leta hai"""
    resources = {
        "databases": [],
        "parameter_groups": {},
        "subnet_group": {}
    }
    
    print("\n🗄️ DATABASE MODULE CONFIGURATION")
    print("Ab hum RDS databases aur related resources ke values input karenge...")
    
    # Database Configuration
    print("\n🔹 Database Setup:")
    num_databases = int(input("   Kitne databases banane hain? [default: 1]: ").strip() or "1")
    
    common_db_engines = {
        "1": {"engine": "mysql", "engine_version": "8.0.32", "family": "mysql8.0"},
        "2": {"engine": "postgres", "engine_version": "14.7", "family": "postgres14"},
        "3": {"engine": "mariadb", "engine_version": "10.11.4", "family": "mariadb10.11"},
        "4": {"engine": "oracle-se2", "engine_version": "19.0.0.0.ru-2023-04.rur-2023-04.r1", "family": "oracle-se2-19"},
        "5": {"engine": "sqlserver-ex", "engine_version": "15.00.4073.23.v1", "family": "sqlserver-ex-15.0"}
    }
    
    common_instance_types = {
        "1": "db.t3.micro",
        "2": "db.t3.small", 
        "3": "db.t3.medium",
        "4": "db.m5.large",
        "5": "db.m5.xlarge",
        "6": "db.r5.large"
    }
    
    for i in range(num_databases):
        print(f"\n   🔧 Database {i+1}:")
        db_identifier = input(f"   Enter database identifier [default: {project_name}-db-{i+1}]: ").strip() or f"{project_name}-db-{i+1}"
        
        print("\n   Database Engine:")
        print("   1. MySQL 8.0")
        print("   2. PostgreSQL 14")
        print("   3. MariaDB 10.11")
        print("   4. Oracle SE2")
        print("   5. SQL Server Express")
        print("   6. Custom Engine")
        
        engine_choice = input("   Select database engine (1-6) [default: 1]: ").strip() or "1"
        
        if engine_choice in common_db_engines:
            db_engine = common_db_engines[engine_choice]["engine"]
            db_engine_version = common_db_engines[engine_choice]["engine_version"]
            parameter_group_family = common_db_engines[engine_choice]["family"]
        else:
            db_engine = input("   Enter database engine (mysql/postgres/mariadb): ").strip()
            db_engine_version = input("   Enter engine version: ").strip()
            parameter_group_family = input("   Enter parameter group family: ").strip()
        
        print("\n   Instance Type:")
        print("   1. db.t3.micro (1 vCPU, 1GB RAM) - Free Tier")
        print("   2. db.t3.small (2 vCPU, 2GB RAM)")
        print("   3. db.t3.medium (2 vCPU, 4GB RAM)")
        print("   4. db.m5.large (2 vCPU, 8GB RAM)")
        print("   5. db.m5.xlarge (4 vCPU, 16GB RAM)")
        print("   6. db.r5.large (2 vCPU, 16GB RAM) - Memory Optimized")
        print("   7. Custom Instance Type")
        
        instance_choice = input("   Select instance type (1-7) [default: 1]: ").strip() or "1"
        
        if instance_choice in common_instance_types:
            instance_type = common_instance_types[instance_choice]
        else:
            instance_type = input("   Enter custom instance type (e.g., db.t3.micro): ").strip()
        
        # Storage Configuration
        print("\n   💾 Storage Configuration:")
        allocated_storage = int(input("   Enter allocated storage in GB [default: 20]: ").strip() or "20")
        max_allocated_storage = int(input("   Enter maximum allocated storage for autoscaling [default: 100]: ").strip() or "100")
        storage_type = input("   Enter storage type (gp2/gp3/io1) [default: gp3]: ").strip() or "gp3"
        
        # Database Credentials
        print("\n   🔐 Database Credentials:")
        username = input("   Enter master username [default: admin]: ").strip() or "admin"
        password = input("   Enter master password [default: ChangeMe123!]: ").strip() or "ChangeMe123!"
        
        # Backup & Maintenance
        print("\n   🛟 Backup & Maintenance:")
        backup_retention_period = int(input("   Backup retention period in days [default: 7]: ").strip() or "7")
        backup_window = input("   Preferred backup window [default: 02:00-03:00]: ").strip() or "02:00-03:00"
        maintenance_window = input("   Preferred maintenance window [default: sun:03:00-sun:04:00]: ").strip() or "sun:03:00-sun:04:00"
        
        # High Availability
        print("\n   🔄 High Availability:")
        multi_az = input("   Enable Multi-AZ deployment? (y/n) [default: n]: ").strip().lower() or 'n'
        
        # Performance Insights
        performance_insights = input("   Enable Performance Insights? (y/n) [default: n]: ").strip().lower() or 'n'
        
        # Monitoring
        monitoring_interval = input("   Enhanced Monitoring interval in seconds [0/1/5/10/15/30/60, default: 0]: ").strip() or "0"
        
        database_config = {
            "identifier": db_identifier,
            "engine": db_engine,
            "engine_version": db_engine_version,
            "instance_type": instance_type,
            "allocated_storage": allocated_storage,
            "max_allocated_storage": max_allocated_storage,
            "storage_type": storage_type,
            "username": username,
            "password": password,
            "backup_retention_period": backup_retention_period,
            "backup_window": backup_window,
            "maintenance_window": maintenance_window,
            "multi_az": multi_az == 'y',
            "performance_insights": performance_insights == 'y',
            "monitoring_interval": int(monitoring_interval),
            "parameter_group_family": parameter_group_family
        }
        
        resources["databases"].append(database_config)
    
    # Database Subnet Group
    print("\n🔹 Database Subnet Group:")
    subnet_group_name = input("   Enter DB subnet group name [default: main-db-subnet-group]: ").strip() or "main-db-subnet-group"
    resources["subnet_group"] = {
        "name": subnet_group_name
    }
    
    # Parameter Groups
    print("\n🔹 Parameter Groups:")
    enable_custom_parameters = input("   Enable custom parameter groups? (y/n) [default: n]: ").strip().lower() or 'n'
    
    if enable_custom_parameters == 'y':
        for db in resources["databases"]:
            print(f"\n   📝 Custom Parameters for {db['identifier']}:")
            param_group_name = input(f"   Enter parameter group name [default: {db['identifier']}-pg]: ").strip() or f"{db['identifier']}-pg"
            
            # Common parameters based on engine
            parameters = []
            
            if db["engine"] in ["mysql", "mariadb"]:
                print("   MySQL/MariaDB Parameters:")
                max_connections = input("   max_connections [default: leave empty]: ").strip()
                if max_connections:
                    parameters.append({
                        "name": "max_connections",
                        "value": max_connections
                    })
                
                wait_timeout = input("   wait_timeout in seconds [default: 28800]: ").strip() or "28800"
                parameters.append({
                    "name": "wait_timeout",
                    "value": wait_timeout
                })
            
            elif db["engine"] == "postgres":
                print("   PostgreSQL Parameters:")
                max_connections = input("   max_connections [default: leave empty]: ").strip()
                if max_connections:
                    parameters.append({
                        "name": "max_connections",
                        "value": max_connections
                    })
                
                shared_preload_libraries = input("   shared_preload_libraries [default: auto_explain,pg_stat_statements]: ").strip() or "auto_explain,pg_stat_statements"
                parameters.append({
                    "name": "shared_preload_libraries",
                    "value": shared_preload_libraries
                })
            
            resources["parameter_groups"][db["identifier"]] = {
                "name": param_group_name,
                "family": db["parameter_group_family"],
                "parameters": parameters
            }
    
    return resources

def generate_database_main_tf(resources, project_name):
    """Database module ke liye main.tf content generate karta hai"""
    content = f'''# Main Terraform configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Database

'''
    
    # Database Subnet Group
    content += f'''# Database Subnet Group
resource "aws_db_subnet_group" "{resources['subnet_group']['name'].replace('-', '_')}" {{
  name       = "${{var.project_name}}-{resources['subnet_group']['name']}"
  subnet_ids = var.database_subnet_ids

  tags = {{
    Name        = "${{var.project_name}}-{resources['subnet_group']['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Parameter Groups (if any)
    for db_identifier, pg_config in resources["parameter_groups"].items():
        content += f'''# Parameter Group for {db_identifier}
resource "aws_db_parameter_group" "{pg_config['name'].replace('-', '_')}" {{
  name   = "${{var.project_name}}-{pg_config['name']}"
  family = "{pg_config['family']}"

'''
        
        for param in pg_config["parameters"]:
            content += f'''  parameter {{
    name  = "{param['name']}"
    value = "{param['value']}"
  }}

'''
        
        content += f'''  tags = {{
    Name        = "${{var.project_name}}-{pg_config['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # RDS Instances
    for db in resources["databases"]:
        db_var_name = db['identifier'].replace('-', '_')
        
        # Determine parameter group
        parameter_group_name = f'aws_db_parameter_group.{resources["parameter_groups"][db["identifier"]]["name"].replace("-", "_")}.name' if db["identifier"] in resources["parameter_groups"] else f'"{db["parameter_group_family"]}"'
        
        content += f'''# RDS Instance: {db['identifier']}
resource "aws_db_instance" "{db_var_name}" {{
  identifier              = "{db['identifier']}"
  engine                 = "{db['engine']}"
  engine_version         = "{db['engine_version']}"
  instance_class         = "{db['instance_type']}"
  allocated_storage      = {db['allocated_storage']}
  max_allocated_storage  = {db['max_allocated_storage']}
  storage_type           = "{db['storage_type']}"
  storage_encrypted      = true

  db_name                = var.database_name
  username               = "{db['username']}"
  password               = var.database_password

  db_subnet_group_name   = aws_db_subnet_group.{resources['subnet_group']['name'].replace('-', '_')}.name
  vpc_security_group_ids = var.database_security_group_ids

  multi_az               = {str(db['multi_az']).lower()}
  publicly_accessible    = false

  backup_retention_period = {db['backup_retention_period']}
  backup_window          = "{db['backup_window']}"
  maintenance_window     = "{db['maintenance_window']}"

  skip_final_snapshot    = var.skip_final_snapshot
  final_snapshot_identifier = "${{var.project_name}}-{db['identifier']}-final"

  performance_insights_enabled = {str(db['performance_insights']).lower()}
  monitoring_interval    = {db['monitoring_interval']}

  parameter_group_name   = {parameter_group_name if db["identifier"] in resources["parameter_groups"] else "null"}

  tags = {{
    Name        = "{db['identifier']}"
    Project     = var.project_name
    Environment = var.environment
  }}

  lifecycle {{
    ignore_changes = [
      password,
      latest_restorable_time
    ]
  }}
}}

'''
    
    return content

def generate_database_variables_tf(project_name, resources):
    """Database module ke liye variables.tf generate karta hai"""
    content = f'''# Variables configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Database

variable "vpc_id" {{
  description = "VPC ID where database will be created"
  type        = string
}}

variable "database_subnet_ids" {{
  description = "List of subnet IDs for database subnet group"
  type        = list(string)
}}

variable "database_security_group_ids" {{
  description = "List of security group IDs for database"
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

variable "database_name" {{
  description = "Initial database name"
  type        = string
  default     = "appdb"
}}

variable "database_password" {{
  description = "Database master password"
  type        = string
  sensitive   = true
  default     = "ChangeMe123!"
}}

variable "skip_final_snapshot" {{
  description = "Whether to skip final snapshot when destroying"
  type        = bool
  default     = false
}}

'''
    
    return content

def generate_database_outputs_tf(resources, project_name):
    """Database module ke liye outputs.tf generate karta hai"""
    content = f'''# Outputs configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Database

output "db_subnet_group_id" {{
  description = "ID of the database subnet group"
  value       = aws_db_subnet_group.{resources['subnet_group']['name'].replace('-', '_')}.id
}}

output "db_subnet_group_name" {{
  description = "Name of the database subnet group"
  value       = aws_db_subnet_group.{resources['subnet_group']['name'].replace('-', '_')}.name
}}

'''
    
    # Database Outputs
    for db in resources["databases"]:
        db_var_name = db['identifier'].replace('-', '_')
        content += f'''output "{db_var_name}_id" {{
  description = "ID of the {db['identifier']} database"
  value       = aws_db_instance.{db_var_name}.id
}}

output "{db_var_name}_arn" {{
  description = "ARN of the {db['identifier']} database"
  value       = aws_db_instance.{db_var_name}.arn
}}

output "{db_var_name}_endpoint" {{
  description = "Connection endpoint for {db['identifier']}"
  value       = aws_db_instance.{db_var_name}.endpoint
}}

output "{db_var_name}_address" {{
  description = "Address of {db['identifier']} database"
  value       = aws_db_instance.{db_var_name}.address
}}

output "{db_var_name}_port" {{
  description = "Port of {db['identifier']} database"
  value       = aws_db_instance.{db_var_name}.port
}}

'''
    
    # Parameter Group Outputs
    for db_identifier, pg_config in resources["parameter_groups"].items():
        pg_var_name = pg_config['name'].replace('-', '_')
        content += f'''output "{pg_var_name}_id" {{
  description = "ID of the {pg_config['name']} parameter group"
  value       = aws_db_parameter_group.{pg_var_name}.id
}}

'''
    
    return content

def generate_database_module(module_path, project_name):
    """Database module generate karta hai"""
    print(f"\n🔧 Generating Database Module for project: {project_name}")
    
    # Resources input
    resources = get_database_resources(project_name)
    
    # Files generate karte hain
    main_tf_content = generate_database_main_tf(resources, project_name)
    variables_tf_content = generate_database_variables_tf(project_name, resources)
    outputs_tf_content = generate_database_outputs_tf(resources, project_name)
    
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
    print(f"\n📊 Database Resources Summary:")
    print(f"   • RDS Instances: {len(resources['databases'])}")
    print(f"   • DB Subnet Group: {resources['subnet_group']['name']}")
    print(f"   • Parameter Groups: {len(resources['parameter_groups'])}")
    
    for db in resources["databases"]:
        print(f"   • {db['identifier']}: {db['engine']} {db['engine_version']} ({db['instance_type']})")
        print(f"     - Multi-AZ: {'Yes' if db['multi_az'] else 'No'}")
        print(f"     - Storage: {db['allocated_storage']}GB ({db['storage_type']})")