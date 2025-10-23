#!/usr/bin/env python3
"""
Redis SSL 快速修复工具
一键解决SSL连接问题
"""

import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading

def run_command(command, description):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def fix_redis_ssl():
    """修复Redis SSL问题"""
    fixes = [
        {
            "name": "卸载当前Redis版本",
            "command": f"{sys.executable} -m pip uninstall redis -y",
            "required": True
        },
        {
            "name": "安装兼容的Redis版本",
            "command": f"{sys.executable} -m pip install redis==4.5.4",
            "required": True
        },
        {
            "name": "验证安装",
            "command": f"{sys.executable} -c \"import redis; print('Redis版本:', redis.__version__)\"",
            "required": False
        }
    ]
    
    results = []
    
    for fix in fixes:
        print(f"执行: {fix['name']}...")
        success, stdout, stderr = run_command(fix['command'], fix['name'])
        
        result = {
            "name": fix['name'],
            "success": success,
            "output": stdout if success else stderr,
            "required": fix['required']
        }
        results.append(result)
        
        if fix['required'] and not success:
            print(f"❌ {fix['name']} 失败: {stderr}")
            break
        elif success:
            print(f"✅ {fix['name']} 成功")
        else:
            print(f"⚠️ {fix['name']} 可选步骤失败")
    
    return results

def create_ssl_fix_gui():
    """创建SSL修复GUI"""
    root = tk.Tk()
    root.title("Redis SSL 快速修复工具")
    root.geometry("600x500")
    
    # 主框架
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(main_frame, text="Redis SSL 连接问题修复", 
                           font=("", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # 问题描述
    problem_frame = ttk.LabelFrame(main_frame, text="问题描述", padding="10")
    problem_frame.pack(fill=tk.X, pady=(0, 20))
    
    problem_text = """如果您遇到以下错误：
• SSL配置错误
• AbstractConnection.__init__() got an unexpected keyword argument 'ssl'
• 连接失败相关的SSL问题

本工具将自动安装兼容的Redis版本来解决这些问题。"""
    
    ttk.Label(problem_frame, text=problem_text, justify=tk.LEFT).pack(anchor=tk.W)
    
    # 修复进度
    progress_frame = ttk.LabelFrame(main_frame, text="修复进度", padding="10")
    progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    # 进度条
    progress_var = tk.StringVar(value="准备就绪...")
    progress_label = ttk.Label(progress_frame, textvariable=progress_var)
    progress_label.pack(pady=(0, 10))
    
    progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
    progress_bar.pack(fill=tk.X, pady=(0, 10))
    
    # 结果显示
    result_text = tk.Text(progress_frame, height=15, wrap=tk.WORD, font=("Consolas", 10))
    scrollbar = ttk.Scrollbar(progress_frame, orient="vertical", command=result_text.yview)
    result_text.configure(yscrollcommand=scrollbar.set)
    
    result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log_message(message):
        """记录消息"""
        result_text.insert(tk.END, message + "\n")
        result_text.see(tk.END)
        root.update()
    
    def start_fix():
        """开始修复"""
        fix_btn.config(state="disabled")
        test_btn.config(state="disabled")
        progress_bar.start(10)
        
        def fix_thread():
            try:
                progress_var.set("正在修复Redis SSL问题...")
                log_message("开始修复Redis SSL连接问题")
                log_message("=" * 50)
                
                results = fix_redis_ssl()
                
                log_message("\n修复结果:")
                log_message("-" * 30)
                
                all_success = True
                for result in results:
                    status = "✅" if result['success'] else "❌"
                    log_message(f"{status} {result['name']}")
                    
                    if result['output']:
                        log_message(f"   输出: {result['output'].strip()}")
                    
                    if result['required'] and not result['success']:
                        all_success = False
                
                if all_success:
                    log_message("\n🎉 修复完成！")
                    log_message("现在可以重新启动Azure Redis管理工具")
                    progress_var.set("修复成功！")
                else:
                    log_message("\n❌ 修复失败，请手动执行以下命令:")
                    log_message("pip uninstall redis")
                    log_message("pip install redis==4.5.4")
                    progress_var.set("修复失败")
                
            except Exception as e:
                log_message(f"\n❌ 修复过程出错: {e}")
                progress_var.set("修复出错")
            
            finally:
                progress_bar.stop()
                fix_btn.config(state="normal")
                test_btn.config(state="normal")
        
        threading.Thread(target=fix_thread, daemon=True).start()
    
    def test_connection():
        """测试连接"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "test_ssl_connection.py"])
            log_message("已启动SSL连接测试工具")
        except Exception as e:
            log_message(f"启动测试工具失败: {e}")
    
    def start_main_app():
        """启动主应用"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "azure_redis_manager.py"])
            log_message("已启动Azure Redis管理工具")
        except Exception as e:
            log_message(f"启动主应用失败: {e}")
    
    # 按钮框架
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X)
    
    fix_btn = ttk.Button(btn_frame, text="开始修复", command=start_fix)
    fix_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    test_btn = ttk.Button(btn_frame, text="测试连接", command=test_connection)
    test_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    ttk.Button(btn_frame, text="启动Redis工具", command=start_main_app).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(btn_frame, text="关闭", command=root.destroy).pack(side=tk.RIGHT)
    
    # 初始提示
    log_message("Redis SSL 快速修复工具")
    log_message("点击'开始修复'自动解决SSL连接问题")
    log_message("修复完成后可以正常使用Azure Redis管理工具")
    
    return root

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # 命令行模式
        print("Redis SSL 快速修复工具 (命令行模式)")
        print("=" * 50)
        
        results = fix_redis_ssl()
        
        print("\n修复结果:")
        print("-" * 30)
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['name']}")
            
            if result['output']:
                print(f"   输出: {result['output'].strip()}")
    else:
        # GUI模式
        root = create_ssl_fix_gui()
        root.mainloop()

if __name__ == "__main__":
    main()
