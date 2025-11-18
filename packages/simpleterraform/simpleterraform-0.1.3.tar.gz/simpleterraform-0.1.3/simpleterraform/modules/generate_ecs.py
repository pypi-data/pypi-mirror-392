# modules/generate_ecs.py
import os

def get_ecs_resources(project_name):
    """ECS module ke resources input leta hai"""
    resources = {
        "cluster": {},
        "services": [],
        "task_definitions": [],
        "load_balancers": []
    }
    
    print("\n🐳 ECS MODULE CONFIGURATION")
    print("Ab hum ECS cluster, services, task definitions aur load balancers ke values input karenge...")
    
    # ECS Cluster Configuration
    print("\n🔹 ECS Cluster Setup:")
    cluster_name = input(f"   Enter ECS cluster name [default: {project_name}-cluster]: ").strip() or f"{project_name}-cluster"
    
    print(f"\n   ⚙️ Configuration for {cluster_name}:")
    
    # Cluster Type
    print("\n   🔧 Cluster Type:")
    print("   1. EC2 (Run containers on EC2 instances)")
    print("   2. Fargate (Serverless containers)")
    print("   3. External (Connect to external instances)")
    cluster_type_choice = input("   Select cluster type (1-3) [default: 2]: ").strip() or "2"
    
    cluster_types = {
        "1": "EC2",
        "2": "FARGATE", 
        "3": "EXTERNAL"
    }
    capacity_providers = [cluster_types[cluster_type_choice]]
    
    # Container Insights
    enable_container_insights = input("   Enable Container Insights for monitoring? (y/n) [default: y]: ").strip().lower() or 'y'
    
    resources["cluster"] = {
        "name": cluster_name,
        "capacity_providers": capacity_providers,
        "container_insights": enable_container_insights == 'y'
    }
    
    # Services Configuration
    print("\n🔹 ECS Services Setup:")
    num_services = int(input("   Kitne ECS services banane hain? [default: 2]: ").strip() or "2")
    
    common_service_types = {
        "1": {"name": "web-api", "purpose": "Web API backend service"},
        "2": {"name": "worker", "purpose": "Background worker service"},
        "3": {"name": "cache", "purpose": "Caching service"},
        "4": {"name": "database", "purpose": "Database service"}
    }
    
    for i in range(num_services):
        print(f"\n   🚀 ECS Service {i+1}:")
        print("   Available templates:")
        print("   1. Web API Service")
        print("   2. Worker Service")
        print("   3. Cache Service")
        print("   4. Database Service")
        print("   5. Custom Service")
        
        service_choice = input("   Select template (1-5) [default: 1]: ").strip() or "1"
        
        if service_choice in common_service_types:
            service_config = common_service_types[service_choice]
            service_name = input(f"   Enter service name [default: {project_name}-{service_config['name']}]: ").strip() or f"{project_name}-{service_config['name']}"
            service_purpose = service_config['purpose']
        else:
            service_name = input("   Enter service name: ").strip()
            service_purpose = input("   Enter service purpose: ").strip()
        
        # Service Configuration
        print(f"\n   ⚙️ Service Configuration for {service_name}:")
        
        # Launch Type
        print("\n   🚀 Launch Type:")
        print("   1. FARGATE (Serverless)")
        print("   2. EC2 (On instances)")
        launch_type_choice = input("   Select launch type (1-2) [default: 1]: ").strip() or "1"
        launch_type = "FARGATE" if launch_type_choice == "1" else "EC2"
        
        # Desired Count
        desired_count = int(input("   Desired number of tasks [default: 2]: ").strip() or "2")
        
        # Deployment Configuration
        print(f"\n   📦 Deployment Configuration:")
        deployment_minimum_healthy_percent = int(input("   Minimum healthy percent during deployment [default: 100]: ").strip() or "100")
        deployment_maximum_percent = int(input("   Maximum percent during deployment [default: 200]: ").strip() or "200")
        
        # Load Balancer Integration
        print(f"\n   ⚖️ Load Balancer Integration:")
        enable_load_balancer = input("   Attach to load balancer? (y/n) [default: y]: ").strip().lower() or 'y'
        
        load_balancer_config = {}
        if enable_load_balancer == 'y':
            print("   Load Balancer Type:")
            print("   1. Application Load Balancer (ALB)")
            print("   2. Network Load Balancer (NLB)")
            lb_type_choice = input("   Select type (1-2) [default: 1]: ").strip() or "1"
            lb_type = "application" if lb_type_choice == "1" else "network"
            
            container_port = int(input("   Container port [default: 80]: ").strip() or "80")
            target_group_port = int(input("   Target group port [default: 80]: ").strip() or "80")
            health_check_path = input("   Health check path [default: /health]: ").strip() or "/health"
            
            load_balancer_config = {
                "enabled": True,
                "type": lb_type,
                "container_port": container_port,
                "target_group_port": target_group_port,
                "health_check_path": health_check_path
            }
        else:
            load_balancer_config = {"enabled": False}
        
        # Auto Scaling
        print(f"\n   📈 Auto Scaling:")
        enable_auto_scaling = input("   Enable auto scaling? (y/n) [default: y]: ").strip().lower() or 'y'
        
        auto_scaling_config = {}
        if enable_auto_scaling == 'y':
            min_capacity = int(input("   Minimum capacity [default: 1]: ").strip() or "1")
            max_capacity = int(input("   Maximum capacity [default: 5]: ").strip() or "5")
            
            print("   Scaling Policy:")
            print("   1. CPU Utilization")
            print("   2. Memory Utilization")
            print("   3. Request Count")
            scaling_policy_choice = input("   Select scaling policy (1-3) [default: 1]: ").strip() or "1"
            
            scaling_metrics = {
                "1": {"type": "ECSServiceAverageCPUUtilization", "target_value": 70},
                "2": {"type": "ECSServiceAverageMemoryUtilization", "target_value": 80},
                "3": {"type": "ALBRequestCountPerTarget", "target_value": 1000}
            }
            scaling_metric = scaling_metrics[scaling_policy_choice]
            
            auto_scaling_config = {
                "enabled": True,
                "min_capacity": min_capacity,
                "max_capacity": max_capacity,
                "scaling_metric": scaling_metric["type"],
                "target_value": scaling_metric["target_value"]
            }
        else:
            auto_scaling_config = {"enabled": False}
        
        service_config = {
            "name": service_name,
            "purpose": service_purpose,
            "launch_type": launch_type,
            "desired_count": desired_count,
            "deployment_minimum_healthy_percent": deployment_minimum_healthy_percent,
            "deployment_maximum_percent": deployment_maximum_percent,
            "load_balancer": load_balancer_config,
            "auto_scaling": auto_scaling_config
        }
        
        resources["services"].append(service_config)
    
    # Task Definitions Configuration
    print("\n🔹 Task Definitions Setup:")
    num_task_definitions = int(input("   Kitne task definitions banane hain? [default: 2]: ").strip() or "2")
    
    for i in range(num_task_definitions):
        print(f"\n   📋 Task Definition {i+1}:")
        task_family = input(f"   Enter task family name [default: {project_name}-task-{i+1}]: ").strip() or f"{project_name}-task-{i+1}"
        
        print(f"\n   🐳 Container Configuration for {task_family}:")
        
        # Container Configuration
        container_name = input("   Enter container name [default: app]: ").strip() or "app"
        container_image = input("   Enter container image [default: nginx:latest]: ").strip() or "nginx:latest"
        container_port = int(input("   Container port [default: 80]: ").strip() or "80")
        
        # CPU and Memory
        print(f"\n   💪 Resource Allocation:")
        cpu_units = input("   CPU units [1024=1 vCPU, default: 256]: ").strip() or "256"
        memory_mb = input("   Memory in MB [default: 512]: ").strip() or "512"
        
        # Environment Variables
        print(f"\n   🔧 Environment Variables:")
        env_vars_input = input("   Enter environment variables as KEY=VALUE, separated by commas [e.g., ENV=prod,LOG_LEVEL=info]: ").strip()
        environment = []
        if env_vars_input:
            for env_var in env_vars_input.split(','):
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    environment.append({
                        "name": key.strip(),
                        "value": value.strip()
                    })
        
        # Log Configuration
        print(f"\n   📝 Log Configuration:")
        enable_logging = input("   Enable CloudWatch logging? (y/n) [default: y]: ").strip().lower() or 'y'
        
        log_configuration = {}
        if enable_logging == 'y':
            log_group_name = input(f"   Log group name [default: /ecs/{task_family}]: ").strip() or f"/ecs/{task_family}"
            log_configuration = {
                "enabled": True,
                "log_group": log_group_name,
                "region": "us-east-1"
            }
        else:
            log_configuration = {"enabled": False}
        
        task_definition = {
            "family": task_family,
            "container_name": container_name,
            "image": container_image,
            "container_port": container_port,
            "cpu": cpu_units,
            "memory": memory_mb,
            "environment": environment,
            "log_configuration": log_configuration
        }
        
        resources["task_definitions"].append(task_definition)
    
    return resources

def generate_ecs_main_tf(resources, project_name):
    """ECS module ke liye main.tf content generate karta hai"""
    content = f'''# Main Terraform configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: ECS (Elastic Container Service)

# ECS Cluster
resource "aws_ecs_cluster" "{resources['cluster']['name'].replace('-', '_')}" {{
  name = "{resources['cluster']['name']}"

  setting {{
    name  = "containerInsights"
    value = "{ "enabled" if resources['cluster']['container_insights'] else "disabled" }"
  }}

  tags = {{
    Name        = "{resources['cluster']['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # ECS Task Execution IAM Role
    content += f'''# ECS Task Execution IAM Role
resource "aws_iam_role" "ecs_task_execution_role" {{
  name = "${{var.project_name}}-ecs-task-execution-role"

  assume_role_policy = <<EOF
{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Action": "sts:AssumeRole",
      "Principal": {{
        "Service": "ecs-tasks.amazonaws.com"
      }},
      "Effect": "Allow"
    }}
  ]
}}
EOF

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {{
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}}

'''
    
    # ECS Task IAM Role
    content += f'''# ECS Task IAM Role
resource "aws_iam_role" "ecs_task_role" {{
  name = "${{var.project_name}}-ecs-task-role"

  assume_role_policy = <<EOF
{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Action": "sts:AssumeRole",
      "Principal": {{
        "Service": "ecs-tasks.amazonaws.com"
      }},
      "Effect": "Allow"
    }}
  ]
}}
EOF

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Load Balancer (if any service needs it)
    load_balancer_required = any(service.get('load_balancer', {}).get('enabled', False) for service in resources['services'])
    
    if load_balancer_required:
        content += f'''# Application Load Balancer
resource "aws_lb" "ecs_alb" {{
  name               = "${{var.project_name}}-ecs-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = var.alb_security_group_ids
  subnets           = var.public_subnet_ids

  enable_deletion_protection = false

  tags = {{
    Name        = "${{var.project_name}}-ecs-alb"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Task Definitions
    for task_def in resources["task_definitions"]:
        task_def_var_name = task_def['family'].replace('-', '_')
        
        content += f'''# ECS Task Definition: {task_def['family']}
resource "aws_ecs_task_definition" "{task_def_var_name}" {{
  family                   = "{task_def['family']}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "{task_def['cpu']}"
  memory                   = "{task_def['memory']}"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{{
    name      = "{task_def['container_name']}"
    image     = "{task_def['image']}"
    essential = true

    portMappings = [{{
      containerPort = {task_def['container_port']}
      hostPort      = {task_def['container_port']}
      protocol      = "tcp"
    }}]

'''
        
        # Environment Variables
        if task_def['environment']:
            content += '    environment = [\n'
            for env_var in task_def['environment']:
                content += f'      {{ name = "{env_var["name"]}", value = "{env_var["value"]}" }},\n'
            content += '    ]\n\n'
        
        # Log Configuration
        if task_def['log_configuration'].get('enabled', False):
            content += f'''    logConfiguration = {{
      logDriver = "awslogs"
      options = {{
        awslogs-group         = "{task_def['log_configuration']['log_group']}"
        awslogs-region        = "{task_def['log_configuration']['region']}"
        awslogs-stream-prefix = "ecs"
      }}
    }}

'''
        
        content += f'''  }}])

  tags = {{
    Name        = "{task_def['family']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Target Groups (for services with load balancer)
    for service in resources["services"]:
        if service.get('load_balancer', {}).get('enabled', False):
            service_var_name = service['name'].replace('-', '_')
            
            content += f'''# Target Group for {service['name']}
resource "aws_lb_target_group" "{service_var_name}" {{
  name        = "${{var.project_name}}-{service['name']}-tg"
  port        = {service['load_balancer']['target_group_port']}
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {{
    path                = "{service['load_balancer']['health_check_path']}"
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    matcher             = "200"
  }}

  tags = {{
    Name        = "${{var.project_name}}-{service['name']}-tg"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Load Balancer Listener
    if load_balancer_required:
        content += f'''# Load Balancer Listener
resource "aws_lb_listener" "ecs_alb" {{
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.{resources['services'][0]['name'].replace('-', '_')}.arn
  }}

  tags = {{
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # ECS Services
    for service in resources["services"]:
        service_var_name = service['name'].replace('-', '_')
        
        content += f'''# ECS Service: {service['name']}
resource "aws_ecs_service" "{service_var_name}" {{
  name            = "{service['name']}"
  cluster         = aws_ecs_cluster.{resources['cluster']['name'].replace('-', '_')}.id
  task_definition = aws_ecs_task_definition.{resources['task_definitions'][0]['family'].replace('-', '_')}.arn
  desired_count   = {service['desired_count']}
  launch_type     = "{service['launch_type']}"

  network_configuration {{
    subnets          = var.private_subnet_ids
    security_groups  = var.ecs_security_group_ids
    assign_public_ip = false
  }}

  deployment_controller {{
    type = "ECS"
  }}

  deployment_circuit_breaker {{
    enable   = true
    rollback = true
  }}

  deployment_maximum_percent         = {service['deployment_maximum_percent']}
  deployment_minimum_healthy_percent = {service['deployment_minimum_healthy_percent']}

'''
        
        # Load Balancer Configuration
        if service.get('load_balancer', {}).get('enabled', False):
            content += f'''  load_balancer {{
    target_group_arn = aws_lb_target_group.{service_var_name}.arn
    container_name   = "{resources['task_definitions'][0]['container_name']}"
    container_port   = {service['load_balancer']['container_port']}
  }}

'''
        
        content += f'''  tags = {{
    Name        = "{service['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}

  depends_on = [aws_lb_listener.ecs_alb]
}}

'''
        
        # Auto Scaling
        if service.get('auto_scaling', {}).get('enabled', False):
            content += f'''# Auto Scaling for {service['name']}
resource "aws_appautoscaling_target" "{service_var_name}" {{
  max_capacity       = {service['auto_scaling']['max_capacity']}
  min_capacity       = {service['auto_scaling']['min_capacity']}
  resource_id        = "service/${{aws_ecs_cluster.{resources['cluster']['name'].replace('-', '_')}.name}}/${{aws_ecs_service.{service_var_name}.name}}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}}

resource "aws_appautoscaling_policy" "{service_var_name}_cpu" {{
  name               = "${{var.project_name}}-{service['name']}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.{service_var_name}.resource_id
  scalable_dimension = aws_appautoscaling_target.{service_var_name}.scalable_dimension
  service_namespace  = aws_appautoscaling_target.{service_var_name}.service_namespace

  target_tracking_scaling_policy_configuration {{
    predefined_metric_specification {{
      predefined_metric_type = "{service['auto_scaling']['scaling_metric']}"
    }}
    target_value       = {service['auto_scaling']['target_value']}.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }}
}}

'''
    
    return content

def generate_ecs_variables_tf(project_name, resources):
    """ECS module ke liye variables.tf generate karta hai"""
    content = f'''# Variables configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: ECS

variable "vpc_id" {{
  description = "VPC ID where ECS resources will be created"
  type        = string
}}

variable "private_subnet_ids" {{
  description = "List of private subnet IDs for ECS tasks"
  type        = list(string)
}}

variable "public_subnet_ids" {{
  description = "List of public subnet IDs for load balancer"
  type        = list(string)
}}

variable "ecs_security_group_ids" {{
  description = "List of security group IDs for ECS tasks"
  type        = list(string)
}}

variable "alb_security_group_ids" {{
  description = "List of security group IDs for Application Load Balancer"
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

def generate_ecs_outputs_tf(resources, project_name):
    """ECS module ke liye outputs.tf generate karta hai"""
    content = f'''# Outputs configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: ECS

output "cluster_id" {{
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.{resources['cluster']['name'].replace('-', '_')}.id
}}

output "cluster_name" {{
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.{resources['cluster']['name'].replace('-', '_')}.name
}}

output "cluster_arn" {{
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.{resources['cluster']['name'].replace('-', '_')}.arn
}}

'''
    
    # Service Outputs
    for service in resources["services"]:
        service_var_name = service['name'].replace('-', '_')
        content += f'''output "{service_var_name}_id" {{
  description = "ID of the {service['name']} ECS service"
  value       = aws_ecs_service.{service_var_name}.id
}}

output "{service_var_name}_name" {{
  description = "Name of the {service['name']} ECS service"
  value       = aws_ecs_service.{service_var_name}.name
}}

'''
    
    # Task Definition Outputs
    for task_def in resources["task_definitions"]:
        task_def_var_name = task_def['family'].replace('-', '_')
        content += f'''output "{task_def_var_name}_arn" {{
  description = "ARN of the {task_def['family']} task definition"
  value       = aws_ecs_task_definition.{task_def_var_name}.arn
}}

output "{task_def_var_name}_family" {{
  description = "Family of the {task_def['family']} task definition"
  value       = aws_ecs_task_definition.{task_def_var_name}.family
}}

'''
    
    # Load Balancer Outputs
    load_balancer_required = any(service.get('load_balancer', {}).get('enabled', False) for service in resources['services'])
    
    if load_balancer_required:
        content += f'''output "load_balancer_arn" {{
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.ecs_alb.arn
}}

output "load_balancer_dns_name" {{
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.ecs_alb.dns_name
}}

'''
    
    return content

def generate_ecs_module(module_path, project_name):
    """ECS module generate karta hai"""
    print(f"\n🔧 Generating ECS Module for project: {project_name}")
    
    # Resources input
    resources = get_ecs_resources(project_name)
    
    # Files generate karte hain
    main_tf_content = generate_ecs_main_tf(resources, project_name)
    variables_tf_content = generate_ecs_variables_tf(project_name, resources)
    outputs_tf_content = generate_ecs_outputs_tf(resources, project_name)
    
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
    print(f"\n📊 ECS Resources Summary:")
    print(f"   • ECS Cluster: {resources['cluster']['name']} ({resources['cluster']['capacity_providers'][0]})")
    print(f"   • ECS Services: {len(resources['services'])}")
    print(f"   • Task Definitions: {len(resources['task_definitions'])}")
    
    load_balancer_count = sum(1 for service in resources['services'] if service.get('load_balancer', {}).get('enabled', False))
    auto_scaling_count = sum(1 for service in resources['services'] if service.get('auto_scaling', {}).get('enabled', False))
    
    print(f"   • Services with Load Balancer: {load_balancer_count}")
    print(f"   • Services with Auto Scaling: {auto_scaling_count}")
    
    for service in resources["services"]:
        print(f"   • Service: {service['name']} - {service['launch_type']} ({service['desired_count']} tasks)")
        if service.get('auto_scaling', {}).get('enabled', False):
            print(f"     - Auto Scaling: {service['auto_scaling']['min_capacity']}-{service['auto_scaling']['max_capacity']}")
    
    for task_def in resources["task_definitions"]:
        print(f"   • Task: {task_def['family']} - {task_def['cpu']} CPU / {task_def['memory']} MB")