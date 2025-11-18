# modules/generate_monitoring.py
import os
import json

def get_monitoring_resources(project_name):
    """Monitoring module ke resources input leta hai"""
    resources = {
        "cloudwatch_alarms": [],
        "dashboards": [],
        "log_groups": [],
        "sns_topics": []
    }
    
    print("\n📈 MONITORING MODULE CONFIGURATION")
    print("Ab hum CloudWatch alarms, dashboards, log groups aur SNS topics ke values input karenge...")
    
    # SNS Topics Configuration
    print("\n🔹 SNS Topics Setup:")
    num_sns_topics = int(input("   Kitne SNS topics banane hain? [default: 2]: ").strip() or "2")
    
    common_sns_use_cases = {
        "1": {"name": "alerts", "purpose": "Critical alerts and notifications"},
        "2": {"name": "notifications", "purpose": "General system notifications"},
        "3": {"name": "security-alerts", "purpose": "Security related alerts"},
        "4": {"name": "cost-alerts", "purpose": "Cost and billing alerts"}
    }
    
    for i in range(num_sns_topics):
        print(f"\n   📢 SNS Topic {i+1}:")
        print("   Available templates:")
        print("   1. Alerts Topic")
        print("   2. Notifications Topic")
        print("   3. Security Alerts")
        print("   4. Cost Alerts")
        print("   5. Custom Topic")
        
        topic_choice = input("   Select template (1-5) [default: 1]: ").strip() or "1"
        
        if topic_choice in common_sns_use_cases:
            topic_config = common_sns_use_cases[topic_choice]
            topic_name = input(f"   Enter topic name [default: {project_name}-{topic_config['name']}]: ").strip() or f"{project_name}-{topic_config['name']}"
            topic_purpose = topic_config['purpose']
        else:
            topic_name = input("   Enter topic name: ").strip()
            topic_purpose = input("   Enter topic purpose: ").strip()
        
        # Subscription Configuration
        print(f"\n   📨 Subscriptions for {topic_name}:")
        num_subscriptions = int(input("   Kitne subscriptions add karna hai? [default: 1]: ").strip() or "1")
        
        subscriptions = []
        for j in range(num_subscriptions):
            print(f"\n     Subscription {j+1}:")
            print("     Protocol options:")
            print("     1. Email")
            print("     2. SMS")
            print("     3. Lambda")
            print("     4. HTTP/HTTPS")
            
            protocol_choice = input("     Select protocol (1-4) [default: 1]: ").strip() or "1"
            
            protocols = {
                "1": "email",
                "2": "sms", 
                "3": "lambda",
                "4": "https"
            }
            protocol = protocols[protocol_choice]
            
            endpoint = input(f"     Enter {protocol} endpoint: ").strip()
            
            subscriptions.append({
                "protocol": protocol,
                "endpoint": endpoint
            })
        
        sns_topic = {
            "name": topic_name,
            "purpose": topic_purpose,
            "subscriptions": subscriptions
        }
        
        resources["sns_topics"].append(sns_topic)
    
    # CloudWatch Log Groups Configuration
    print("\n🔹 CloudWatch Log Groups Setup:")
    num_log_groups = int(input("   Kitne log groups banane hain? [default: 3]: ").strip() or "3")
    
    common_log_groups = {
        "1": {"name": "application", "retention": 30, "purpose": "Application logs"},
        "2": {"name": "web-server", "retention": 90, "purpose": "Web server access logs"},
        "3": {"name": "database", "retention": 365, "purpose": "Database audit logs"},
        "4": {"name": "security", "retention": 180, "purpose": "Security and compliance logs"},
        "5": {"name": "audit", "retention": 365, "purpose": "Audit trail logs"}
    }
    
    for i in range(num_log_groups):
        print(f"\n   📝 Log Group {i+1}:")
        print("   Available templates:")
        print("   1. Application Logs (30 days)")
        print("   2. Web Server Logs (90 days)")
        print("   3. Database Logs (1 year)")
        print("   4. Security Logs (6 months)")
        print("   5. Audit Logs (1 year)")
        print("   6. Custom Log Group")
        
        log_choice = input("   Select template (1-6) [default: 1]: ").strip() or "1"
        
        if log_choice in common_log_groups:
            log_config = common_log_groups[log_choice]
            log_group_name = input(f"   Enter log group name [default: /aws/{project_name}/{log_config['name']}]: ").strip() or f"/aws/{project_name}/{log_config['name']}"
            retention_days = log_config['retention']
            log_purpose = log_config['purpose']
        else:
            log_group_name = input("   Enter log group name: ").strip()
            retention_days = int(input("   Enter retention in days [default: 30]: ").strip() or "30")
            log_purpose = input("   Enter log group purpose: ").strip()
        
        log_group = {
            "name": log_group_name,
            "retention_days": retention_days,
            "purpose": log_purpose
        }
        
        resources["log_groups"].append(log_group)
    
    # CloudWatch Alarms Configuration
    print("\n🔹 CloudWatch Alarms Setup:")
    num_alarms = int(input("   Kitne CloudWatch alarms banane hain? [default: 5]: ").strip() or "5")
    
    common_alarms = {
        "1": {
            "name": "high-cpu",
            "metric": "CPUUtilization",
            "namespace": "AWS/EC2",
            "threshold": 80,
            "description": "High CPU utilization"
        },
        "2": {
            "name": "high-memory",
            "metric": "MemoryUtilization", 
            "namespace": "CWAgent",
            "threshold": 85,
            "description": "High memory utilization"
        },
        "3": {
            "name": "low-disk",
            "metric": "disk_used_percent",
            "namespace": "CWAgent",
            "threshold": 90,
            "description": "Low disk space"
        },
        "4": {
            "name": "high-latency",
            "metric": "TargetResponseTime",
            "namespace": "AWS/ApplicationELB",
            "threshold": 2,
            "description": "High application latency"
        },
        "5": {
            "name": "5xx-errors",
            "metric": "HTTPCode_Target_5XX_Count",
            "namespace": "AWS/ApplicationELB", 
            "threshold": 10,
            "description": "High 5XX error rate"
        },
        "6": {
            "name": "db-connections",
            "metric": "DatabaseConnections",
            "namespace": "AWS/RDS",
            "threshold": 100,
            "description": "High database connections"
        }
    }
    
    for i in range(num_alarms):
        print(f"\n   🚨 CloudWatch Alarm {i+1}:")
        print("   Available alarm templates:")
        print("   1. High CPU Utilization")
        print("   2. High Memory Utilization") 
        print("   3. Low Disk Space")
        print("   4. High Application Latency")
        print("   5. High 5XX Errors")
        print("   6. High Database Connections")
        print("   7. Custom Alarm")
        
        alarm_choice = input("   Select alarm template (1-7) [default: 1]: ").strip() or "1"
        
        if alarm_choice in common_alarms:
            alarm_config = common_alarms[alarm_choice]
            alarm_name = input(f"   Enter alarm name [default: {project_name}-{alarm_config['name']}]: ").strip() or f"{project_name}-{alarm_config['name']}"
            metric_name = alarm_config['metric']
            namespace = alarm_config['namespace']
            threshold = alarm_config['threshold']
            description = alarm_config['description']
        else:
            alarm_name = input("   Enter alarm name: ").strip()
            metric_name = input("   Enter metric name: ").strip()
            namespace = input("   Enter namespace: ").strip()
            threshold = float(input("   Enter threshold: ").strip())
            description = input("   Enter alarm description: ").strip()
        
        # Alarm Configuration
        print(f"\n   ⚙️ Alarm Configuration for {alarm_name}:")
        comparison_operator = input("   Comparison operator (GreaterThanThreshold/LessThanThreshold) [default: GreaterThanThreshold]: ").strip() or "GreaterThanThreshold"
        evaluation_periods = int(input("   Evaluation periods [default: 2]: ").strip() or "2")
        period = int(input("   Period in seconds [default: 300]: ").strip() or "300")
        statistic = input("   Statistic (Average/Sum/Maximum/Minimum) [default: Average]: ").strip() or "Average"
        
        # Alarm Actions
        print(f"\n   🔔 Alarm Actions for {alarm_name}:")
        enable_actions = input("   Enable alarm actions? (y/n) [default: y]: ").strip().lower() or 'y'
        
        alarm_actions = []
        ok_actions = []
        if enable_actions == 'y' and resources["sns_topics"]:
            print("   Available SNS topics for notifications:")
            for idx, topic in enumerate(resources["sns_topics"]):
                print(f"   {idx + 1}. {topic['name']} - {topic['purpose']}")
            
            topic_choice = input("   Select topic for alarm notifications [default: 1]: ").strip() or "1"
            if topic_choice.isdigit() and int(topic_choice) <= len(resources["sns_topics"]):
                selected_topic = resources["sns_topics"][int(topic_choice) - 1]
                topic_var_name = selected_topic['name'].replace('-', '_')
                # Double quotes mein reference banayenge
                alarm_actions = [f"aws_sns_topic.{topic_var_name}.arn"]
                ok_actions = [f"aws_sns_topic.{topic_var_name}.arn"]
        
        cloudwatch_alarm = {
            "name": alarm_name,
            "metric_name": metric_name,
            "namespace": namespace,
            "threshold": threshold,
            "description": description,
            "comparison_operator": comparison_operator,
            "evaluation_periods": evaluation_periods,
            "period": period,
            "statistic": statistic,
            "alarm_actions": alarm_actions,
            "ok_actions": ok_actions
        }
        
        resources["cloudwatch_alarms"].append(cloudwatch_alarm)
    
    # CloudWatch Dashboards Configuration
    print("\n🔹 CloudWatch Dashboards Setup:")
    num_dashboards = int(input("   Kitne dashboards banane hain? [default: 1]: ").strip() or "1")
    
    common_dashboards = {
        "1": {"name": "infrastructure", "purpose": "Infrastructure overview dashboard"},
        "2": {"name": "application", "purpose": "Application performance dashboard"},
        "3": {"name": "business", "purpose": "Business metrics dashboard"},
        "4": {"name": "security", "purpose": "Security monitoring dashboard"}
    }
    
    for i in range(num_dashboards):
        print(f"\n   📊 Dashboard {i+1}:")
        print("   Available templates:")
        print("   1. Infrastructure Overview")
        print("   2. Application Performance") 
        print("   3. Business Metrics")
        print("   4. Security Monitoring")
        print("   5. Custom Dashboard")
        
        dashboard_choice = input("   Select template (1-5) [default: 1]: ").strip() or "1"
        
        if dashboard_choice in common_dashboards:
            dashboard_config = common_dashboards[dashboard_choice]
            dashboard_name = input(f"   Enter dashboard name [default: {project_name}-{dashboard_config['name']}]: ").strip() or f"{project_name}-{dashboard_config['name']}"
            dashboard_purpose = dashboard_config['purpose']
        else:
            dashboard_name = input("   Enter dashboard name: ").strip()
            dashboard_purpose = input("   Enter dashboard purpose: ").strip()
        
        dashboard = {
            "name": dashboard_name,
            "purpose": dashboard_purpose
        }
        
        resources["dashboards"].append(dashboard)
    
    return resources

def generate_monitoring_main_tf(resources, project_name):
    """Monitoring module ke liye main.tf content generate karta hai"""
    content = f'''# Main Terraform configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Monitoring

'''
    
    # SNS Topics
    for topic in resources["sns_topics"]:
        topic_var_name = topic['name'].replace('-', '_')
        
        content += f'''# SNS Topic: {topic['name']}
resource "aws_sns_topic" "{topic_var_name}" {{
  name = "{topic['name']}"

  tags = {{
    Name        = "{topic['name']}"
    Purpose     = "{topic['purpose']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
        
        # SNS Topic Subscriptions
        for j, subscription in enumerate(topic['subscriptions']):
            content += f'''resource "aws_sns_topic_subscription" "{topic_var_name}_{subscription['protocol']}_{j}" {{
  topic_arn = aws_sns_topic.{topic_var_name}.arn
  protocol  = "{subscription['protocol']}"
  endpoint  = "{subscription['endpoint']}"
}}

'''
    
    # CloudWatch Log Groups
    for log_group in resources["log_groups"]:
        log_group_var_name = log_group['name'].replace('/', '_').replace('-', '_').strip('_')
        
        content += f'''# CloudWatch Log Group: {log_group['name']}
resource "aws_cloudwatch_log_group" "{log_group_var_name}" {{
  name              = "{log_group['name']}"
  retention_in_days = {log_group['retention_days']}

  tags = {{
    Name        = "{log_group['name']}"
    Purpose     = "{log_group['purpose']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # CloudWatch Alarms
    for alarm in resources["cloudwatch_alarms"]:
        alarm_var_name = alarm['name'].replace('-', '_')
        
        content += f'''# CloudWatch Alarm: {alarm['name']}
resource "aws_cloudwatch_metric_alarm" "{alarm_var_name}" {{
  alarm_name          = "{alarm['name']}"
  comparison_operator = "{alarm['comparison_operator']}"
  evaluation_periods  = "{alarm['evaluation_periods']}"
  metric_name         = "{alarm['metric_name']}"
  namespace           = "{alarm['namespace']}"
  period              = "{alarm['period']}"
  statistic           = "{alarm['statistic']}"
  threshold           = {alarm['threshold']}
  alarm_description   = "{alarm['description']}"

'''
        
        if alarm['alarm_actions']:
            # Proper Terraform interpolation syntax
            content += f'  alarm_actions       = ["${{{alarm["alarm_actions"][0]}}}"]\n'
        
        if alarm['ok_actions']:
            content += f'  ok_actions          = ["${{{alarm["ok_actions"][0]}}}"]\n'
        
        content += f'''
  tags = {{
    Name        = "{alarm['name']}"
    Project     = var.project_name
    Environment = var.environment
  }}
}}

'''
    
    # CloudWatch Dashboards
    for dashboard in resources["dashboards"]:
        dashboard_var_name = dashboard['name'].replace('-', '_')
        
        # Generate dashboard body based on dashboard type
        dashboard_body = generate_dashboard_body(dashboard, project_name)
        
        content += f'''# CloudWatch Dashboard: {dashboard['name']}
resource "aws_cloudwatch_dashboard" "{dashboard_var_name}" {{
  dashboard_name = "{dashboard['name']}"
  dashboard_body = <<EOF
{dashboard_body}
EOF
}}

'''
    
    return content

def generate_dashboard_body(dashboard, project_name):
    """Dashboard ke liye body content generate karta hai"""
    
    if "infrastructure" in dashboard['name']:
        dashboard_data = {
            "widgets": [
                {
                    "type": "metric",
                    "x": 0,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/EC2", "CPUUtilization"],
                            [".", "NetworkIn"],
                            [".", "NetworkOut"]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-east-1",
                        "title": "EC2 Instance Metrics"
                    }
                },
                {
                    "type": "metric", 
                    "x": 0,
                    "y": 6,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/RDS", "CPUUtilization"],
                            [".", "DatabaseConnections"],
                            [".", "FreeStorageSpace"]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-east-1",
                        "title": "RDS Database Metrics"
                    }
                }
            ]
        }
    
    elif "application" in dashboard['name']:
        dashboard_data = {
            "widgets": [
                {
                    "type": "metric",
                    "x": 0,
                    "y": 0,
                    "width": 12,
                    "height": 6,
                    "properties": {
                        "metrics": [
                            ["AWS/ApplicationELB", "TargetResponseTime"],
                            [".", "HTTPCode_Target_2XX_Count"],
                            [".", "HTTPCode_Target_4XX_Count"],
                            [".", "HTTPCode_Target_5XX_Count"]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-east-1",
                        "title": "Application Load Balancer Metrics"
                    }
                }
            ]
        }
    
    else:
        # Default dashboard
        dashboard_data = {
            "widgets": [
                {
                    "type": "text",
                    "x": 0,
                    "y": 0,
                    "width": 24,
                    "height": 3,
                    "properties": {
                        "markdown": f"# {dashboard['name']}\\n## {dashboard['purpose']}"
                    }
                }
            ]
        }
    
    # JSON format mein properly convert karenge
    return json.dumps(dashboard_data, indent=2)

def generate_monitoring_variables_tf(project_name, resources):
    """Monitoring module ke liye variables.tf generate karta hai"""
    content = f'''# Variables configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Monitoring

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

def generate_monitoring_outputs_tf(resources, project_name):
    """Monitoring module ke liye outputs.tf generate karta hai"""
    content = f'''# Outputs configuration file
# Auto-generated by Python Script
# Project: {project_name}
# Module: Monitoring

'''
    
    # SNS Topic Outputs
    for topic in resources["sns_topics"]:
        topic_var_name = topic['name'].replace('-', '_')
        content += f'''output "{topic_var_name}_arn" {{
  description = "ARN of the {topic['name']} SNS topic"
  value       = aws_sns_topic.{topic_var_name}.arn
}}

'''
    
    # CloudWatch Log Group Outputs
    for log_group in resources["log_groups"]:
        log_group_var_name = log_group['name'].replace('/', '_').replace('-', '_').strip('_')
        content += f'''output "{log_group_var_name}_arn" {{
  description = "ARN of the {log_group['name']} log group"
  value       = aws_cloudwatch_log_group.{log_group_var_name}.arn
}}

output "{log_group_var_name}_name" {{
  description = "Name of the {log_group['name']} log group"
  value       = aws_cloudwatch_log_group.{log_group_var_name}.name
}}

'''
    
    # CloudWatch Alarm Outputs
    for alarm in resources["cloudwatch_alarms"]:
        alarm_var_name = alarm['name'].replace('-', '_')
        content += f'''output "{alarm_var_name}_arn" {{
  description = "ARN of the {alarm['name']} CloudWatch alarm"
  value       = aws_cloudwatch_metric_alarm.{alarm_var_name}.arn
}}

'''
    
    # CloudWatch Dashboard Outputs
    for dashboard in resources["dashboards"]:
        dashboard_var_name = dashboard['name'].replace('-', '_')
        content += f'''output "{dashboard_var_name}_arn" {{
  description = "ARN of the {dashboard['name']} CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.{dashboard_var_name}.dashboard_arn
}}

'''
    
    return content

def generate_monitoring_module(module_path, project_name):
    """Monitoring module generate karta hai"""
    print(f"\n🔧 Generating Monitoring Module for project: {project_name}")
    
    # Resources input
    resources = get_monitoring_resources(project_name)
    
    # Files generate karte hain
    main_tf_content = generate_monitoring_main_tf(resources, project_name)
    variables_tf_content = generate_monitoring_variables_tf(project_name, resources)
    outputs_tf_content = generate_monitoring_outputs_tf(resources, project_name)
    
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
    print(f"\n📊 Monitoring Resources Summary:")
    print(f"   • SNS Topics: {len(resources['sns_topics'])}")
    print(f"   • CloudWatch Log Groups: {len(resources['log_groups'])}")
    print(f"   • CloudWatch Alarms: {len(resources['cloudwatch_alarms'])}")
    print(f"   • CloudWatch Dashboards: {len(resources['dashboards'])}")
    
    for topic in resources["sns_topics"]:
        print(f"   • SNS: {topic['name']} - {len(topic['subscriptions'])} subscriptions")
    
    for log_group in resources["log_groups"]:
        print(f"   • Log Group: {log_group['name']} - {log_group['retention_days']} days retention")
    
    for alarm in resources["cloudwatch_alarms"]:
        print(f"   • Alarm: {alarm['name']} - {alarm['metric_name']}")