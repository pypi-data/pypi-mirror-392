# main.py
import os
from modules.generate_networking import generate_networking_module
from modules.generate_security import generate_security_module
from modules.generate_compute import generate_compute_module
from modules.generate_database import generate_database_module
from modules.generate_storage import generate_storage_module
from modules.generate_monitoring import generate_monitoring_module
from modules.generate_kubernetes import generate_kubernetes_module
from modules.generate_ecs import generate_ecs_module

def display_welcome():
    """Welcome message display karta hai"""
    print("\n" + "="*50)
    print("🚀 TERRAFORM MODULE GENERATOR")
    print("="*50)
    print("Welcome Bhai! Ye script Terraform modules automatically generate karegi")
    print("="*50)

def get_project_details():
    """User se project details leta hai"""
    print("\n📁 Project Setup:")
    project_name = input("Enter your project name: ").strip().replace(" ", "-")
    
    if not project_name:
        project_name = "my-terraform-project"
    
    return project_name

def select_module_type():
    """User se module type select karwata hai"""
    print("\n📦 Available Modules:")
    print("1. Networking 🌐")
    print("2. Security 🔒") 
    print("3. Compute 💻")
    print("4. Database 🗄️")
    print("5. Storage 📊")
    print("6. Monitoring 📈")
    print("7. Kubernetes ☸️")
    print("8. ECS 🐳")
    
    while True:
        choice = input("\n✅ Select module number (1-8): ").strip()
        
        module_types = {
            "1": "networking",
            "2": "security", 
            "3": "compute",
            "4": "database",
            "5": "storage",
            "6": "monitoring",
            "7": "kubernetes",
            "8": "ecs"
        }
        
        if choice in module_types:
            return module_types[choice]
        else:
            print("❌ Invalid choice! Please select 1-8")

def create_module_directory(project_name, module_name):
    """Module directory structure banata hai"""
    base_path = "terraform-modules"
    folder_name = f"{project_name}-{module_name}"
    module_path = os.path.join(base_path, folder_name)
    
    # Create directories
    os.makedirs(module_path, exist_ok=True)
    print(f"📁 Created directory: {module_path}")
    
    return module_path

def main():
    """Main function"""
    try:
        # Welcome message
        display_welcome()
        
        # Project details
        project_name = get_project_details()
        
        # Module selection
        module_name = select_module_type()
        
        # Directory creation
        module_path = create_module_directory(project_name, module_name)
        
        # Module-specific generation
        if module_name == "networking":
            generate_networking_module(module_path, project_name)
        elif module_name == "security":
            generate_security_module(module_path, project_name)
        elif module_name == "compute":
            generate_compute_module(module_path, project_name)
        elif module_name == "database":
            generate_database_module(module_path, project_name)
        elif module_name == "storage":
            generate_storage_module(module_path, project_name)
        elif module_name == "monitoring":
            generate_monitoring_module(module_path, project_name)
        elif module_name == "kubernetes":
            generate_kubernetes_module(module_path, project_name)
        elif module_name == "ecs":
            generate_ecs_module(module_path, project_name)
        else:
            print(f"\n⚠️  {module_name.capitalize()} module coming soon!")
            print("Abhi ke liye koi bhi module try karo bhai!")
        
        # Success message
        print(f"\n🎉 TERRAFORM MODULE SUCCESSFULLY CREATED! 🎉")
        print(f"📍 Location: {module_path}")
        print(f"📋 Module Type: {module_name}")
        print(f"🏷️  Project: {project_name}")
        print("\n📚 Next steps:")
        print("   1. cd " + module_path)
        print("   2. terraform init")
        print("   3. terraform plan")
        print("   4. terraform apply")
            
    except KeyboardInterrupt:
        print("\n\n❌ Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()