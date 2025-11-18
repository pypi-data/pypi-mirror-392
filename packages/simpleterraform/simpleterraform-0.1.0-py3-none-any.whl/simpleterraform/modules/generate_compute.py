# modules/generate_compute.py
import os

def get_compute_resources(project_name):
    """Compute module ke resources input leta hai"""
    resources = {
        "instances": [],
        "auto_scaling": {},
        "load_balancer": {}
    }
    
    print("\n💻 COMPUTE MODULE CONFIGURATION")
    print("Ab hum EC2 instances, Auto Scaling aur Load Balancer ke values input karenge...")
    
    # EC2 Instances Configuration
    print("\n🔹 EC2 Instances Setup:")
    num_instances = int(input("   Kitne EC2 instances banane hain? [default: 2]: ").strip() or "2")
    
    common_instance_types = {
        "1": "t3.micro",
        "2": "t3.small", 
        "3": "t3.medium",
        "4": "m5.large",
        "5": "m5.xlarge",
        "6": "c5.large"
    }
    
    common_amis = {
        "1": "ami-0c02fb55956c7d316",  # Amazon Linux 2
        "2": "ami-0fc5d935ebf8bc3bc",  # Ubuntu 20.04
        "3": "ami-0be2609ba883822ec",  # Ubuntu 22.04
        "4": "ami-0b0dcb5067f052a63",  # Amazon Linux 2023
        "5": "ami-0b0af3577fe5e3532",  # RHEL 9
        "6": "ami-0a3c3a20c09d6f377"   # Windows Server 2022
    }
    
    for i in range(num_instances):
        print(f"\n   🔧 EC2 Instance {i+1}:")
        instance_name = input(f"   Enter instance name [default: {project_name}-instance-{i+1}]: ").strip() or f"{project_name}-instance-{i+1}"
        
        print("\n   Instance Type:")
        print("   1. t3.micro (1 vCPU, 1GB RAM) - Free Tier")
        print("   2. t3.small (2 vCPU, 2GB RAM)")
        print("   3. t3.medium (2 vCPU, 4GB RAM)")
        print("   4. m5.large (2 vCPU, 8GB RAM)")
        print("   5. m5.xlarge (4 vCPU, 16GB RAM)")
        print("   6. c5.large (2 vCPU, 4GB RAM) - Compute Optimized")
        print("   7. Custom Instance Type")
        
        instance_choice = input("   Select instance type (1-7) [default: 1]: ").strip() or "1"
        
        if instance_choice in common_instance_types:
            instance_type = common_instance_types[instance_choice]
        else:
            instance_type = input("   Enter custom instance type (e.g., t3.micro): ").strip()
        
        print("\n   AMI Selection:")
        print("   1. Amazon Linux 2")
        print("   2. Ubuntu 20.04 LTS")
        print("   3. Ubuntu 22.04 LTS")
        print("   4. Amazon Linux 2023")
        print("   5. RHEL 9")
        print("   6. Windows Server 2022")
        print("   7. Custom AMI ID")
        
        ami_choice = input("   Select AMI (1-7) [default: 1]: ").strip() or "1"
        
        if ami_choice in common_amis:
            ami_id = common_amis[ami_choice]
        else:
            ami_id = input("   Enter custom AMI ID: ").strip()
        
        # Key Pair
        key_name = input("   Enter key pair name [default: my-key]: ").strip() or "my-key"
        
        # Storage
        print("\n   💾 Storage Configuration:")
        volume_size = int(input("   Enter root volume size in GB [default: 20]: ").strip() or "20")
        volume_type = input("   Enter volume type (gp2/gp3/io1) [default: gp3]: ").strip() or "gp3"
        
        # Network
        print("\n   🌐 Network Configuration:")
        associate_public_ip = input("   Associate public IP? (y/n) [default: y]: ").strip().lower() or 'y'
        
        instance_config = {
            "name": instance_name,
            "instance_type": instance_type,
            "ami_id": ami_id,
            "key_name": key_name,
            "volume_size": volume_size,
            "volume_type": volume_type,
            "associate_public_ip": associate_public_ip == 'y'
        }
        
        resources["instances"].append(instance_config)
    
    # Auto Scaling Configuration
    print("\n🔹 Auto Scaling Group Setup:")
    enable_asg = input("   Enable Auto Scaling Group? (y/n) [default: y]: ").strip().lower() or 'y'
    
    if enable_asg == 'y':
        asg_name = input("   Enter ASG name [default: web-asg]: ").strip() or "web-asg"
        min_size = int(input("   Enter minimum size [default: 2]: ").strip() or "2")
        max_size = int(input("   Enter maximum size [default: 5]: ").strip() or "5")
        desired_size = int(input("   Enter desired capacity [default: 2]: ").strip() or "2")
        
        # Scaling Policies
        print("\n   📈 Scaling Policies:")
        enable_scaling_policies = input("   Enable scaling policies? (y/n) [default: y]: ").strip().lower() or 'y'
        
        scaling_policies = {}
        if enable_scaling_policies == 'y':
            target_cpu = int(input("   Target CPU utilization percentage [default: 70]: ").strip() or "70")
            scaling_policies = {
                "target_cpu_utilization": target_cpu,
                "enable": True
            }
        else:
            scaling_policies = {"enable": False}
        
        resources["auto_scaling"] = {
            "enable": True,
            "name": asg_name,
            "min_size": min_size,
            "max_size": max_size,
            "desired_size": desired_size,
            "scaling_policies": scaling_policies
        }
    else:
        resources["auto_scaling"] = {"enable": False}
    
    # Load Balancer Configuration
    print("\n🔹 Load Balancer Setup:")
    enable_lb = input("   Enable Load Balancer? (y/n) [default: y]: ").strip().lower() or 'y'
    
    if enable_lb == 'y':
        lb_name = input("   Enter load balancer name [default: web-lb]: ").strip() or "web-lb"
        lb_type = "1"
        
        print("\n   Load Balancer Type:")
        print("   1. Application Load Balancer (ALB)")
        print("   2. Network Load Balancer (NLB)")
        lb_type_choice = input("   Select type (1-2) [default: 1]: ").strip() or "1"
        lb_type = "application" if lb_type_choice == "1" else "network"
        
        # Listeners
        print("\n   🔊 Listener Configuration:")
        enable_http = input("   Enable HTTP listener? (y/n) [default: y]: ").strip().lower() or 'y'
        enable_https = input("   Enable HTTPS listener? (y/n) [default: n]: ").strip().lower() or 'n'
        
        listeners = []
        if enable_http == 'y':
            listeners.append({"protocol": "HTTP", "port": 80})
        if enable_https == 'y':
            listeners.append({"protocol": "HTTPS", "port": 443})
        
        # Health Check
        print("\n   🏥 Health Check Configuration:")
        health_check_path = input("   Health check path [default: /]: ").strip() or "/"
        health_check_port = input("   Health check port [default: 80]: ").strip() or "80"
        
        resources["load_balancer"] = {
            "enable": True,
            "name": lb_name,
            "type": lb_type,
            "listeners": listeners,
            "health_check_path": health_check_path,
            "health_check_port": health_check_port
        }
    else:
        resources["load_balancer"] = {"enable": False}
    
    return resources

def generate_compute_main_tf(resources, project_name):
    """Compute module ke liye main.tf content generate karta hai"""
    content = f'''# Main Terraform configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Compute

'''
    
    # EC2 Instances
    if resources["instances"]:
        content += '# EC2 Instances\n'
        for instance in resources["instances"]:
            content += f'''resource "aws_instance" "{instance['name'].replace('-', '_')}" {{
  ami                    = "{instance['ami_id']}"
  instance_type          = "{instance['instance_type']}"
  key_name               = "{instance['key_name']}"
  vpc_security_group_ids = var.security_group_ids
  subnet_id              = var.subnet_ids[0]  # First subnet from list

  root_block_device {{
    volume_size = {instance['volume_size']}
    volume_type = "{instance['volume_type']}"
    encrypted   = true
  }}

  associate_public_ip_address = {str(instance['associate_public_ip']).lower()}

  tags = {{
    Name        = "{instance['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Auto Scaling Group
    if resources["auto_scaling"]["enable"]:
        asg = resources["auto_scaling"]
        content += f'''# Auto Scaling Group
resource "aws_launch_template" "{asg['name'].replace('-', '_')}" {{
  name_prefix = "${{var.project_name}}-{asg['name']}-"
  image_id      = "{resources['instances'][0]['ami_id'] if resources['instances'] else 'ami-0c02fb55956c7d316'}"
  instance_type = "{resources['instances'][0]['instance_type'] if resources['instances'] else 't3.micro'}"
  key_name      = "{resources['instances'][0]['key_name'] if resources['instances'] else 'my-key'}"

  block_device_mappings {{
    device_name = "/dev/xvda"

    ebs {{
      volume_size = {resources['instances'][0]['volume_size'] if resources['instances'] else 20}
      volume_type = "{resources['instances'][0]['volume_type'] if resources['instances'] else 'gp3'}"
      encrypted   = true
    }}
  }}

  network_interfaces {{
    associate_public_ip_address = true
    security_groups             = var.security_group_ids
  }}

  tag_specifications {{
    resource_type = "instance"

    tags = {{
      Name        = "${{var.project_name}}-{asg['name']}"
      Project     = var.project_name
      Environment = var.environment
    }}
  }}

  lifecycle {{
    create_before_destroy = true
  }}
}}

resource "aws_autoscaling_group" "{asg['name'].replace('-', '_')}" {{
  name_prefix         = "${{var.project_name}}-{asg['name']}-"
  vpc_zone_identifier = var.subnet_ids
  desired_capacity    = {asg['desired_size']}
  min_size            = {asg['min_size']}
  max_size            = {asg['max_size']}

  launch_template {{
    id      = aws_launch_template.{asg['name'].replace('-', '_')}.id
    version = "$Latest"
  }}

  target_group_arns = var.load_balancer_target_group_arns

  tag {{
    key                 = "Name"
    value               = "${{var.project_name}}-{asg['name']}"
    propagate_at_launch = true
  }}

  tag {{
    key                 = "Project"
    value               = var.project_name
    propagate_at_launch = true
  }}

  tag {{
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }}

  lifecycle {{
    create_before_destroy = true
    ignore_changes        = [load_balancers, target_group_arns]
  }}
}}

'''
        
        # Auto Scaling Policies
        if asg["scaling_policies"]["enable"]:
            content += f'''# Auto Scaling Policies
resource "aws_autoscaling_policy" "{asg['name'].replace('-', '_')}_scale_up" {{
  name                   = "${{var.project_name}}-{asg['name']}-scale-up"
  autoscaling_group_name = aws_autoscaling_group.{asg['name'].replace('-', '_')}.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = 1
  cooldown               = 300
}}

resource "aws_autoscaling_policy" "{asg['name'].replace('-', '_')}_scale_down" {{
  name                   = "${{var.project_name}}-{asg['name']}-scale-down"
  autoscaling_group_name = aws_autoscaling_group.{asg['name'].replace('-', '_')}.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = -1
  cooldown               = 300
}}

resource "aws_cloudwatch_metric_alarm" "{asg['name'].replace('-', '_')}_cpu_high" {{
  alarm_name          = "${{var.project_name}}-{asg['name']}-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "{asg['scaling_policies']['target_cpu_utilization']}"

  dimensions = {{
    AutoScalingGroupName = aws_autoscaling_group.{asg['name'].replace('-', '_')}.name
  }}

  alarm_description = "Scale up if CPU > {asg['scaling_policies']['target_cpu_utilization']}% for 2 periods"
  alarm_actions     = [aws_autoscaling_policy.{asg['name'].replace('-', '_')}_scale_up.arn]
}}

resource "aws_cloudwatch_metric_alarm" "{asg['name'].replace('-', '_')}_cpu_low" {{
  alarm_name          = "${{var.project_name}}-{asg['name']}-cpu-utilization-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "30"

  dimensions = {{
    AutoScalingGroupName = aws_autoscaling_group.{asg['name'].replace('-', '_')}.name
  }}

  alarm_description = "Scale down if CPU < 30% for 2 periods"
  alarm_actions     = [aws_autoscaling_policy.{asg['name'].replace('-', '_')}_scale_down.arn]
}}

'''
    
    # Load Balancer
    if resources["load_balancer"]["enable"]:
        lb = resources["load_balancer"]
        content += f'''# Load Balancer
resource "aws_lb" "{lb['name'].replace('-', '_')}" {{
  name               = "${{var.project_name}}-{lb['name']}"
  internal           = false
  load_balancer_type = "{lb['type']}"
  security_groups    = var.security_group_ids
  subnets           = var.subnet_ids

  enable_deletion_protection = false

  tags = {{
    Name        = "${{var.project_name}}-{lb['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
        
        # Target Group
        content += f'''# Target Group
resource "aws_lb_target_group" "{lb['name'].replace('-', '_')}" {{
  name     = "${{var.project_name}}-{lb['name']}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {{
    path                = "{lb['health_check_path']}"
    port                = "{lb['health_check_port']}"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    matcher             = "200"
  }}

  tags = {{
    Name        = "${{var.project_name}}-{lb['name']}-tg"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
        
        # Listeners
        for listener in lb["listeners"]:
            protocol_lower = listener["protocol"].lower()
            content += f'''# {listener["protocol"]} Listener
resource "aws_lb_listener" "{lb['name'].replace('-', '_')}_{protocol_lower}" {{
  load_balancer_arn = aws_lb.{lb['name'].replace('-', '_')}.arn
  port              = {listener["port"]}
  protocol          = "{listener["protocol"]}"

  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.{lb['name'].replace('-', '_')}.arn
  }}
}}

'''
    
    return content

def generate_compute_variables_tf(project_name, resources):
    """Compute module ke liye variables.tf generate karta hai"""
    content = f'''# Variables configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Compute

variable "vpc_id" {{
  description = "VPC ID where resources will be created"
  type        = string
}}

variable "subnet_ids" {{
  description = "List of subnet IDs for instances and load balancer"
  type        = list(string)
}}

variable "security_group_ids" {{
  description = "List of security group IDs for instances"
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

variable "load_balancer_target_group_arns" {{
  description = "List of target group ARNs for Auto Scaling Group"
  type        = list(string)
  default     = []
}}

'''
    
    return content

def generate_compute_outputs_tf(resources, project_name):
    """Compute module ke liye outputs.tf generate karta hai"""
    content = f'''# Outputs configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Compute

'''
    
    # EC2 Instances Outputs
    for instance in resources["instances"]:
        instance_var = instance['name'].replace('-', '_')
        content += f'''output "{instance_var}_id" {{
  description = "ID of the {instance['name']} instance"
  value       = aws_instance.{instance_var}.id
}}

output "{instance_var}_private_ip" {{
  description = "Private IP of the {instance['name']} instance"
  value       = aws_instance.{instance_var}.private_ip
}}

'''
        if instance['associate_public_ip']:
            content += f'''output "{instance_var}_public_ip" {{
  description = "Public IP of the {instance['name']} instance"
  value       = aws_instance.{instance_var}.public_ip
}}

'''
    
    # Auto Scaling Outputs
    if resources["auto_scaling"]["enable"]:
        asg_var = resources["auto_scaling"]['name'].replace('-', '_')
        content += f'''output "{asg_var}_id" {{
  description = "ID of the {resources['auto_scaling']['name']} Auto Scaling Group"
  value       = aws_autoscaling_group.{asg_var}.id
}}

output "{asg_var}_name" {{
  description = "Name of the {resources['auto_scaling']['name']} Auto Scaling Group"
  value       = aws_autoscaling_group.{asg_var}.name
}}

'''
    
    # Load Balancer Outputs
    if resources["load_balancer"]["enable"]:
        lb_var = resources["load_balancer"]['name'].replace('-', '_')
        content += f'''output "{lb_var}_arn" {{
  description = "ARN of the {resources['load_balancer']['name']} Load Balancer"
  value       = aws_lb.{lb_var}.arn
}}

output "{lb_var}_dns_name" {{
  description = "DNS name of the {resources['load_balancer']['name']} Load Balancer"
  value       = aws_lb.{lb_var}.dns_name
}}

output "{lb_var}_zone_id" {{
  description = "Zone ID of the {resources['load_balancer']['name']} Load Balancer"
  value       = aws_lb.{lb_var}.zone_id
}}

output "{lb_var}_target_group_arn" {{
  description = "ARN of the {resources['load_balancer']['name']} Target Group"
  value       = aws_lb_target_group.{lb_var}.arn
}}

'''
    
    return content

def generate_compute_module(module_path, project_name):
    """Compute module generate karta hai"""
    print(f"\n🔧 Generating Compute Module for project: {project_name}")
    
    # Resources input
    resources = get_compute_resources(project_name)
    
    # Files generate karte hain
    main_tf_content = generate_compute_main_tf(resources, project_name)
    variables_tf_content = generate_compute_variables_tf(project_name, resources)
    outputs_tf_content = generate_compute_outputs_tf(resources, project_name)
    
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
    print(f"\n📊 Compute Resources Summary:")
    print(f"   • EC2 Instances: {len(resources['instances'])}")
    print(f"   • Auto Scaling: {'Enabled' if resources['auto_scaling']['enable'] else 'Disabled'}")
    print(f"   • Load Balancer: {'Enabled' if resources['load_balancer']['enable'] else 'Disabled'}")
    
    for instance in resources["instances"]:
        print(f"   • {instance['name']}: {instance['instance_type']}")