import os

def is_in_git_repo():
    """检查当前目录是否在git仓库中（包括子目录）
    
    Returns:
        bool: True if current directory is inside a git repository, False otherwise
    """
    current_dir = os.getcwd()
    while current_dir != '/':
        if os.path.exists(os.path.join(current_dir, '.git')):
            return True
        current_dir = os.path.dirname(current_dir)
    return False

def pretty_print_dataclass(obj):
    """美化打印dataclass对象"""
    class_name = obj.__class__.__name__
    print(f"\n╭─ {class_name} ─╮")
    for field, value in obj.__dict__.items():
        print(f"│ {field:<20}: {value}")
    print("╰" + "─" * (len(class_name) + 4) + "╯\n")

# 使用示例
if __name__ == "__main__":
    print(f"当前目录在git仓库中: {is_in_git_repo()}")