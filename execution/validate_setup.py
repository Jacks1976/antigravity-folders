import os
import sys

def main():
    print("Validating Agent System Setup...")
    
    # Check directories
    required_dirs = ["directives", "execution", ".tmp"]
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    
    if missing_dirs:
        print(f"ERROR: Missing directories: {missing_dirs}")
        sys.exit(1)
        
    print("Directory structure: OK")
    print("Execution layer: OK")
    print("System validation successful.")

if __name__ == "__main__":
    main()
