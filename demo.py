#!/usr/bin/env python3
"""
Azure Redis管理工具 - 功能演示脚本
展示优化后的新功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time

def create_demo_window():
    """创建演示窗口"""
    root = tk.Tk()
    root.title("Azure Redis管理工具 - 功能演示")
    root.geometry("800x600")
    
    # 主框架
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(main_frame, text="Azure Redis管理工具 - 优化功能演示", 
                           font=("", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # 功能介绍
    features_text = """
🚀 版本 2.0 新功能和优化：

1. ⚡ 连接速度优化
   • 连接超时从5秒缩短到2秒
   • 后台线程处理，避免界面冻结
   • 实时连接状态提示

2. 🛠️ 错误处理增强
   • 详细的错误分类（认证失败、连接超时、网络错误等）
   • 所有异常都在UI状态栏显示
   • 友好的错误提示信息

3. 👆 完整值查看功能（重要新功能）
   • 单击任意键名查看完整内容
   • 支持所有Redis数据类型格式化显示：
     - String: 完整字符串内容
     - List: 带索引的列表 [0] item1, [1] item2
     - Set: 排序的集合成员
     - Hash: field: value 格式
     - ZSet: member (score: 1.0) 格式
   • 值详情窗口功能：
     - 显示键信息（名称、类型、TTL）
     - 可滚动查看长内容
     - 复制到剪贴板
     - 实时刷新按钮

4. 📊 性能提升
   • Redis Pipeline批量数据获取
   • 后台线程处理数据加载
   • 避免界面卡顿和无响应

5. 🎯 用户体验改进
   • 加载过程状态提示
   • 改进的按钮状态管理
   • 更直观的操作反馈

使用方法：
1. 运行主程序：python azure_redis_manager.py
2. 输入Azure Redis连接信息
3. 连接后单击任意键名查看完整值
4. 享受更快速流畅的Redis管理体验！
    """
    
    # 创建文本框显示功能介绍
    text_frame = ttk.Frame(main_frame)
    text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
    scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget.insert(1.0, features_text)
    text_widget.config(state=tk.DISABLED)
    
    # 按钮框架
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X)
    
    def start_app():
        """启动主应用"""
        root.destroy()
        import subprocess
        import sys
        subprocess.Popen([sys.executable, "azure_redis_manager.py"])
    
    def show_changelog():
        """显示更新日志"""
        try:
            with open("CHANGELOG.md", "r", encoding="utf-8") as f:
                content = f.read()
            
            changelog_window = tk.Toplevel(root)
            changelog_window.title("更新日志")
            changelog_window.geometry("700x500")
            
            text_widget = tk.Text(changelog_window, wrap=tk.WORD, font=("Consolas", 9))
            scrollbar = ttk.Scrollbar(changelog_window, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
            
            text_widget.insert(1.0, content)
            text_widget.config(state=tk.DISABLED)
            
        except FileNotFoundError:
            messagebox.showerror("错误", "找不到更新日志文件")
    
    # 按钮
    ttk.Button(btn_frame, text="启动Redis管理工具", command=start_app).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(btn_frame, text="查看更新日志", command=show_changelog).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(btn_frame, text="关闭", command=root.destroy).pack(side=tk.RIGHT)
    
    return root

if __name__ == "__main__":
    print("正在启动功能演示...")
    demo_window = create_demo_window()
    demo_window.mainloop()
