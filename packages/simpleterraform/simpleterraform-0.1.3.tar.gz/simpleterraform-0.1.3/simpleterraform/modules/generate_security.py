# modules/generate_security.py
import os
import json

def get_security_resources(project_name):
    """Security module ke resources input leta hai"""
    resources = {
        "security_groups": []
    }
    
    print("\n🔒 SECURITY MODULE CONFIGURATION")
    print("Ab hum security groups aur rules ke values input karenge...")
    
    # Security Groups Configuration
    print("\n🔹 Security Groups Setup:")
    num_security_groups = int(input("   Kitne security groups banane hain? [default: 3]: ").strip() or "3")
    
    common_security_groups = {
        "1": {"name": "web-sg", "description": "Security group for web servers"},
        "2": {"name": "app-sg", "description": "Security group for application servers"}, 
        "3": {"name": "db-sg", "description": "Security group for database servers"},
        "4": {"name": "alb-sg", "description": "Security group for load balancers"},
        "5": {"name": "bastion-sg", "description": "Security group for bastion hosts"}
    }
    
    for i in range(num_security_groups):
        print(f"\n   🔧 Security Group {i+1}:")
        print("   Available templates:")
        print("   1. Web Server (HTTP/HTTPS/SSH)")
        print("   2. Application Server (APP/SSH)")
        print("   3. Database Server (MySQL/PostgreSQL)")
        print("   4. Load Balancer (HTTP/HTTPS)")
        print("   5. Bastion Host (SSH)")
        print("   6. Custom Security Group")
        
        sg_choice = input("   Select template (1-6) [default: 1]: ").strip() or "1"
        
        if sg_choice in common_security_groups:
            sg_config = common_security_groups[sg_choice]
            sg_name = input(f"   Enter security group name [default: {sg_config['name']}]: ").strip() or sg_config['name']
            sg_description = input(f"   Enter description [default: {sg_config['description']}]: ").strip() or sg_config['description']
        else:
            sg_name = input("   Enter security group name: ").strip()
            sg_description = input("   Enter security group description: ").strip()
        
        # Ingress Rules
        print(f"\n   📥 Ingress Rules for {sg_name}:")
        ingress_rules = get_security_rules("ingress")
        
        # Egress Rules  
        print(f"\n   📤 Egress Rules for {sg_name}:")
        egress_rules = get_security_rules("egress")
        
        security_group = {
            "name": sg_name,
            "description": sg_description,
            "ingress_rules": ingress_rules,
            "egress_rules": egress_rules
        }
        
        resources["security_groups"].append(security_group)
    
    return resources

def get_security_rules(rule_type):
    """Security rules input leta hai"""
    rules = []
    
    print(f"   Kitne {rule_type} rules add karna hai? [default: 2]: ", end="")
    num_rules = int(input().strip() or "2")
    
    common_ports = {
        "1": {"from_port": 80, "to_port": 80, "protocol": "tcp", "description": "HTTP"},
        "2": {"from_port": 443, "to_port": 443, "protocol": "tcp", "description": "HTTPS"},
        "3": {"from_port": 22, "to_port": 22, "protocol": "tcp", "description": "SSH"},
        "4": {"from_port": 3389, "to_port": 3389, "protocol": "tcp", "description": "RDP"},
        "5": {"from_port": 5432, "to_port": 5432, "protocol": "tcp", "description": "PostgreSQL"},
        "6": {"from_port": 3306, "to_port": 3306, "protocol": "tcp", "description": "MySQL"},
        "7": {"from_port": 8080, "to_port": 8080, "protocol": "tcp", "description": "HTTP-Alt"},
        "8": {"from_port": 8443, "to_port": 8443, "protocol": "tcp", "description": "HTTPS-Alt"},
        "9": {"from_port": -1, "to_port": -1, "protocol": "icmp", "description": "ICMP"},
        "10": {"from_port": 0, "to_port": 0, "protocol": "-1", "description": "All Traffic"}
    }
    
    for i in range(num_rules):
        print(f"\n     📍 {rule_type.capitalize()} Rule {i+1}:")
        print("     Common ports:")
        print("     1. HTTP (80)")
        print("     2. HTTPS (443)") 
        print("     3. SSH (22)")
        print("     4. RDP (3389)")
        print("     5. PostgreSQL (5432)")
        print("     6. MySQL (3306)")
        print("     7. HTTP-Alt (8080)")
        print("     8. HTTPS-Alt (8443)")
        print("     9. ICMP")
        print("     10. All Traffic")
        print("     11. Custom Port")
        
        port_choice = input("     Select port (1-11) [default: 1]: ").strip() or "1"
        
        if port_choice in common_ports:
            rule_config = common_ports[port_choice]
            from_port = rule_config["from_port"]
            to_port = rule_config["to_port"] 
            protocol = rule_config["protocol"]
            description = rule_config["description"]
        else:
            from_port = int(input("     Enter from port: ").strip())
            to_port = int(input("     Enter to port: ").strip())
            protocol = input("     Enter protocol (tcp/udp/icmp/-1) [default: tcp]: ").strip() or "tcp"
            description = input("     Enter rule description: ").strip()
        
        # CIDR blocks input
        print("\n     🔐 CIDR Blocks for this rule:")
        cidr_blocks = []
        num_cidrs = int(input("     Kitne CIDR blocks add karna hai? [default: 1]: ").strip() or "1")
        
        for j in range(num_cidrs):
            default_cidr = "0.0.0.0/0" if j == 0 else ""
            cidr = input(f"       CIDR block {j+1} [default: {default_cidr}]: ").strip() or default_cidr
            cidr_blocks.append(cidr)
        
        rule = {
            "from_port": from_port,
            "to_port": to_port,
            "protocol": protocol,
            "cidr_blocks": cidr_blocks,
            "description": description
        }
        
        rules.append(rule)
    
    return rules

def format_cidr_blocks(cidr_blocks):
    """CIDR blocks ko Terraform format mein convert karta hai"""
    # Double quotes ke sath list banate hain
    formatted = '["' + '", "'.join(cidr_blocks) + '"]'
    return formatted

def generate_security_main_tf(resources, project_name):
    """Security module ke liye main.tf content generate karta hai"""
    content = f'''# Main Terraform configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Security

'''
    
    # Security Groups
    for i, sg in enumerate(resources["security_groups"]):
        content += f'''# Security Group: {sg['name']}
resource "aws_security_group" "{sg['name'].replace('-', '_')}" {{
  name        = "${{var.project_name}}-{sg['name']}"
  description = "{sg['description']}"
  vpc_id      = var.vpc_id

  tags = {{
    Name        = "${{var.project_name}}-{sg['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # Ingress Rules
    for sg in resources["security_groups"]:
        sg_name_var = sg['name'].replace('-', '_')
        
        for j, rule in enumerate(sg['ingress_rules']):
            cidr_blocks_formatted = format_cidr_blocks(rule['cidr_blocks'])
            
            content += f'''# Ingress Rule {j+1} for {sg['name']}
resource "aws_security_group_rule" "{sg_name_var}_ingress_{j+1}" {{
  type              = "ingress"
  description       = "{rule['description']}"
  from_port         = {rule['from_port']}
  to_port           = {rule['to_port']}
  protocol          = "{rule['protocol']}"
  cidr_blocks       = {cidr_blocks_formatted}
  security_group_id = aws_security_group.{sg_name_var}.id
}}

'''
    
    # Egress Rules  
    for sg in resources["security_groups"]:
        sg_name_var = sg['name'].replace('-', '_')
        
        for j, rule in enumerate(sg['egress_rules']):
            cidr_blocks_formatted = format_cidr_blocks(rule['cidr_blocks'])
            
            content += f'''# Egress Rule {j+1} for {sg['name']}
resource "aws_security_group_rule" "{sg_name_var}_egress_{j+1}" {{
  type              = "egress"
  description       = "{rule['description']}"
  from_port         = {rule['from_port']}
  to_port           = {rule['to_port']}
  protocol          = "{rule['protocol']}"
  cidr_blocks       = {cidr_blocks_formatted}
  security_group_id = aws_security_group.{sg_name_var}.id
}}

'''
    
    return content

def generate_security_variables_tf(project_name, resources):
    """Security module ke liye variables.tf generate karta hai"""
    content = f'''# Variables configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Security

variable "vpc_id" {{
  description = "VPC ID where security groups will be created"
  type        = string
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

'''
    
    return content

def generate_security_outputs_tf(resources, project_name):
    """Security module ke liye outputs.tf generate karta hai"""
    content = f'''# Outputs configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Security

'''
    
    for sg in resources["security_groups"]:
        sg_name_var = sg['name'].replace('-', '_')
        content += f'''output "{sg_name_var}_id" {{
  description = "ID of the {sg['name']} security group"
  value       = aws_security_group.{sg_name_var}.id
}}

'''
    
    # All security groups combined output
    sg_ids = [f'aws_security_group.{sg["name"].replace("-", "_")}.id' for sg in resources["security_groups"]]
    
    content += f'''output "all_security_group_ids" {{
  description = "Map of all security group IDs"
  value = {{
'''
    
    for sg in resources["security_groups"]:
        sg_name_var = sg['name'].replace('-', '_')
        content += f'    {sg_name_var} = aws_security_group.{sg_name_var}.id\n'
    
    content += '''  }
}

'''
    
    return content

def generate_security_module(module_path, project_name):
    """Security module generate karta hai"""
    print(f"\n🔧 Generating Security Module for project: {project_name}")
    
    # Resources input
    resources = get_security_resources(project_name)
    
    # Files generate karte hain
    main_tf_content = generate_security_main_tf(resources, project_name)
    variables_tf_content = generate_security_variables_tf(project_name, resources)
    outputs_tf_content = generate_security_outputs_tf(resources, project_name)
    
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
    print(f"\n📊 Security Resources Summary:")
    print(f"   • Total Security Groups: {len(resources['security_groups'])}")
    
    for sg in resources["security_groups"]:
        print(f"   • {sg['name']}:")
        print(f"     - Ingress Rules: {len(sg['ingress_rules'])}")
        print(f"     - Egress Rules: {len(sg['egress_rules'])}")