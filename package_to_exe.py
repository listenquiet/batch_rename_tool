import os
import subprocess
import sys
import shutil

def install_pyinstaller():
    """安装PyInstaller打包工具"""
    try:
        print("🔧 正在安装PyInstaller...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                              capture_output=True, text=True, check=True)
        print("✅ PyInstaller安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装PyInstaller失败：{e}")
        return False

def package_to_exe():
    """将Python脚本打包为exe"""
    script_name = "batch_rename_tool.py"
    output_name = "批量文件重命名工具"
    
    # 检查脚本是否存在
    if not os.path.exists(script_name):
        print(f"❌ 错误：找不到脚本文件 {script_name}")
        return False
    
    # 清理之前的打包文件
    print("🧹 清理之前的打包文件...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"   已删除 {folder} 文件夹")
            except Exception as e:
                print(f"   删除 {folder} 失败：{e}")
    
    # 清理spec文件
    spec_file = f"{output_name}.spec"
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"   已删除 {spec_file}")
        except Exception as e:
            print(f"   删除 {spec_file} 失败：{e}")
    
    # 基本打包命令
    cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--onefile",                    # 打包成单个exe文件
        "--windowed",                   # 使用GUI模式，不显示控制台窗口
        "--name", output_name,          # 输出文件名
        "--clean",                      # 清理临时文件
        "--add-data", "*.ico;.",        # 添加图标文件（如果有的话）
        "--distpath", "dist",           # 输出目录
        "--workpath", "build",          # 工作目录
        script_name
    ]
    
    # 如果没有图标文件，移除图标参数
    icon_files = [f for f in os.listdir('.') if f.endswith('.ico')]
    if not icon_files:
        cmd = [arg for arg in cmd if arg != "--add-data" and arg != "*.ico;."]
    else:
        print(f"🎨 找到图标文件：{icon_files}")
    
    try:
        print("🚀 开始打包程序...")
        print(f"📋 执行命令：{' '.join(cmd)}")
        print("-" * 60)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("✅ 打包成功！")
        print("-" * 60)
        
        # 显示打包输出信息
        if result.stdout:
            print("📄 打包输出信息：")
            print(result.stdout)
        
        # 检查输出文件
        exe_path = os.path.join("dist", f"{output_name}.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / 1024 / 1024
            print(f"\n🎉 程序已成功打包！")
            print(f"📂 输出路径：{os.path.abspath(exe_path)}")
            print(f"📏 文件大小：{file_size:.2f} MB")
            
            # 创建使用说明文件
            create_readme(output_name)
            
            return True
        else:
            print("❌ 打包完成但找不到输出文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print("❌ 打包失败！")
        print("-" * 60)
        print(f"错误信息：{e}")
        if e.stderr:
            print("错误详情：")
            print(e.stderr)
        return False

def create_readme(app_name):
    """创建使用说明文件"""
    readme_content = f"""# {app_name}

## 功能说明
这是一个批量文件重命名工具，可以批量重命名指定文件夹中的所有文件。

## 主要特性
- 📁 图形界面选择文件夹
- 🏷️ 自定义文件名前缀和后缀
- 📊 多种排序方式：文件名、修改时间、创建时间、文件大小
- 🔢 多种编号样式：数字(1,2,3/01,02,03/001,002,003)、中文数字(一、二、三)、罗马数字(Ⅰ,Ⅱ,Ⅲ)、字母(a,b,c/A,B,C)
- 👀 实时预览重命名结果
- ✅ 安全确认机制，防止误操作

## 使用方法
1. 双击运行 {app_name}.exe
2. 点击"浏览..."按钮选择要重命名的文件夹
3. 设置文件名前缀和后缀（可选）
4. 选择排序方式和编号样式
5. 点击"刷新预览"查看重命名效果
6. 确认无误后点击"执行重命名"

## 注意事项
- 重命名操作不可撤销，请谨慎操作！
- 建议先预览确认效果再执行重命名
- 如果目标文件名已存在，程序会自动跳过

## 系统要求
- Windows 7/8/10/11
- 无需安装Python环境

## 生成时间
{os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}
"""
    
    try:
        with open(os.path.join("dist", "使用说明.txt"), "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("📝 已创建使用说明文件")
    except Exception as e:
        print(f"⚠️ 创建使用说明文件失败：{e}")

def main():
    print("=" * 60)
    print("🎯 Python脚本打包为EXE工具")
    print("=" * 60)
    print()
    
    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
        print("✅ 检测到PyInstaller已安装")
    except ImportError:
        print("⚠️ 未检测到PyInstaller，开始安装...")
        if not install_pyinstaller():
            print("❌ 安装PyInstaller失败，请手动安装：pip install pyinstaller")
            return
    
    # 执行打包
    if package_to_exe():
        print()
        print("🎉 打包完成！")
        print("📁 您可以在 'dist' 文件夹中找到生成的exe文件")
        print("📖 同时生成的使用说明.txt文件包含详细的使用方法")
        print("🚀 双击exe文件即可使用批量文件重命名工具！")
        print()
        print("💡 提示：您可以将exe文件复制到任何Windows电脑上使用")
    else:
        print()
        print("💥 打包失败，请检查错误信息并重试")

if __name__ == "__main__":
    main()