import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import redis
from datetime import datetime, timedelta
import json
import threading
import time
from redis.connection import ConnectionPool

class AzureRedisManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure Redis 管理工具")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Redis连接
        self.redis_client = None
        self.connection_pool = None
        self.is_connected = False
        
        # 分页设置
        self.page_size = 1000  # 每页显示的键数量
        self.current_page = 0
        self.total_keys = 0
        self.all_keys = []
        
        # 加载控制
        self.loading = False
        self.cancel_loading = False
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 连接部分
        self.create_connection_section(main_frame)
        
        # 操作按钮部分
        self.create_action_buttons(main_frame)
        
        # 数据显示部分
        self.create_data_display(main_frame)
        
        # 状态栏
        self.create_status_bar(main_frame)
        
    def create_connection_section(self, parent):
        # 连接框架
        conn_frame = ttk.LabelFrame(parent, text="Redis 连接设置", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        
        # 主机地址
        ttk.Label(conn_frame, text="主机地址:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.host_var = tk.StringVar(value="your-redis.redis.cache.windows.net")
        self.host_entry = ttk.Entry(conn_frame, textvariable=self.host_var, width=40)
        self.host_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 端口
        ttk.Label(conn_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.port_var = tk.StringVar(value="6380")
        self.port_entry = ttk.Entry(conn_frame, textvariable=self.port_var, width=10)
        self.port_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # 密码
        ttk.Label(conn_frame, text="密码:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(conn_frame, textvariable=self.password_var, show="*", width=40)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))
        
        # SSL
        self.ssl_var = tk.BooleanVar(value=True)
        self.ssl_check = ttk.Checkbutton(conn_frame, text="使用 SSL", variable=self.ssl_var)
        self.ssl_check.grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # 连接按钮
        self.connect_btn = ttk.Button(conn_frame, text="连接", command=self.connect_to_redis)
        self.connect_btn.grid(row=0, column=4, rowspan=2, padx=(10, 0))
        
        # 断开连接按钮
        self.disconnect_btn = ttk.Button(conn_frame, text="断开", command=self.disconnect_from_redis, state="disabled")
        self.disconnect_btn.grid(row=0, column=5, rowspan=2, padx=(5, 0))
        
    def create_action_buttons(self, parent):
        # 操作按钮框架
        action_frame = ttk.LabelFrame(parent, text="操作", padding="5")
        action_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        action_frame.columnconfigure(6, weight=1)
        
        # 查询模式框架
        query_frame = ttk.LabelFrame(action_frame, text="查询模式", padding="3")
        query_frame.grid(row=0, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 查询模式选择
        self.query_mode_var = tk.StringVar(value="all")
        
        # 获取所有数据单选按钮
        self.all_data_radio = ttk.Radiobutton(query_frame, text="获取所有数据", 
                                             variable=self.query_mode_var, value="all",
                                             command=self.on_query_mode_change)
        self.all_data_radio.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # 按key查询单选按钮
        self.key_query_radio = ttk.Radiobutton(query_frame, text="按Key查询", 
                                              variable=self.query_mode_var, value="key",
                                              command=self.on_query_mode_change)
        self.key_query_radio.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Key查询输入框
        ttk.Label(query_frame, text="Key:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.key_query_var = tk.StringVar()
        self.key_query_entry = ttk.Entry(query_frame, textvariable=self.key_query_var, width=25, state="disabled")
        self.key_query_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.key_query_entry.bind('<Return>', self.on_key_query_enter)
        
        # 模糊查询复选框
        self.fuzzy_search_var = tk.BooleanVar(value=False)
        self.fuzzy_search_check = ttk.Checkbutton(query_frame, text="模糊查询", 
                                                 variable=self.fuzzy_search_var,
                                                 state="disabled")
        self.fuzzy_search_check.grid(row=0, column=4, sticky=tk.W, padx=(10, 10))
        
        # 查询按钮
        self.query_btn = ttk.Button(query_frame, text="查询", command=self.execute_query, state="disabled")
        self.query_btn.grid(row=0, column=5, padx=5)
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(action_frame, text="刷新数据", command=self.refresh_data, state="disabled")
        self.refresh_btn.grid(row=1, column=0, padx=(0, 5))
        
        # 停止加载按钮
        self.stop_btn = ttk.Button(action_frame, text="停止加载", command=self.stop_loading, state="disabled")
        self.stop_btn.grid(row=1, column=1, padx=5)
        
        # 新增按钮
        self.add_btn = ttk.Button(action_frame, text="新增 Key", command=self.add_key_dialog, state="disabled")
        self.add_btn.grid(row=1, column=2, padx=5)
        
        # 删除按钮
        self.delete_btn = ttk.Button(action_frame, text="删除选中", command=self.delete_selected_key, state="disabled")
        self.delete_btn.grid(row=1, column=3, padx=5)
        
        # 编辑按钮
        self.edit_btn = ttk.Button(action_frame, text="编辑选中", command=self.edit_selected_key, state="disabled")
        self.edit_btn.grid(row=1, column=4, padx=5)
        
        # 清空显示按钮
        self.clear_display_btn = ttk.Button(action_frame, text="清空显示", command=self.clear_display, state="disabled")
        self.clear_display_btn.grid(row=1, column=5, padx=5)
        
        # 分页控制
        page_frame = ttk.Frame(action_frame)
        page_frame.grid(row=2, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.prev_btn = ttk.Button(page_frame, text="上一页", command=self.prev_page, state="disabled")
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_info_var = tk.StringVar(value="第 0 页，共 0 页")
        self.page_info_label = ttk.Label(page_frame, textvariable=self.page_info_var)
        self.page_info_label.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(page_frame, text="下一页", command=self.next_page, state="disabled")
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # 页大小设置
        ttk.Label(page_frame, text="每页:").pack(side=tk.LEFT, padx=(20, 5))
        self.page_size_var = tk.StringVar(value="1000")
        page_size_combo = ttk.Combobox(page_frame, textvariable=self.page_size_var, 
                                      values=["100", "500", "1000", "2000", "5000"], 
                                      width=8, state="readonly")
        page_size_combo.pack(side=tk.LEFT, padx=5)
        page_size_combo.bind("<<ComboboxSelected>>", self.on_page_size_change)
        
        # 统计信息
        self.stats_var = tk.StringVar(value="总计: 0 个键")
        self.stats_label = ttk.Label(page_frame, textvariable=self.stats_var)
        self.stats_label.pack(side=tk.RIGHT, padx=(20, 0))
        
        # 本地搜索框
        search_frame = ttk.Frame(page_frame)
        search_frame.pack(side=tk.RIGHT, padx=(20, 20))
        
        ttk.Label(search_frame, text="本地搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.local_search_var = tk.StringVar()
        self.local_search_entry = ttk.Entry(search_frame, textvariable=self.local_search_var, width=15)
        self.local_search_entry.pack(side=tk.LEFT, padx=5)
        self.local_search_entry.bind('<KeyRelease>', self.on_local_search_change)
        
        # 清空本地搜索按钮
        self.clear_local_search_btn = ttk.Button(search_frame, text="清空", command=self.clear_local_search)
        self.clear_local_search_btn.pack(side=tk.LEFT, padx=5)
        
    def create_data_display(self, parent):
        # 数据显示框架
        data_frame = ttk.LabelFrame(parent, text="Redis 数据", padding="5")
        data_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ("key", "type", "value", "ttl", "size")
        self.tree = ttk.Treeview(data_frame, columns=columns, show="headings", height=20)
        
        # 定义列标题
        self.tree.heading("key", text="Key")
        self.tree.heading("type", text="类型")
        self.tree.heading("value", text="值")
        self.tree.heading("ttl", text="过期时间 (TTL)")
        self.tree.heading("size", text="大小")
        
        # 设置列宽
        self.tree.column("key", width=200, minwidth=100)
        self.tree.column("type", width=80, minwidth=60)
        self.tree.column("value", width=300, minwidth=200)
        self.tree.column("ttl", width=150, minwidth=100)
        self.tree.column("size", width=80, minwidth=60)
        
        # 滚动条
        v_scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(data_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 绑定事件
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-1>", self.on_item_single_click)
        
    def create_status_bar(self, parent):
        # 状态栏
        self.status_var = tk.StringVar(value="未连接")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def connect_to_redis(self):
        """连接到Redis"""
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get())
            password = self.password_var.get() if self.password_var.get() else None
            ssl = self.ssl_var.get()
            
            if not host:
                self.show_connection_error("请输入主机地址")
                return
                
            # 显示连接状态
            self.status_var.set("正在连接...")
            self.connect_btn.config(state="disabled")
            self.root.update()
            
            # 在后台线程中进行连接
            def connect_thread():
                try:
                    # 基础连接参数
                    base_kwargs = {
                        'decode_responses': True,
                        'socket_timeout': 10,
                        'socket_connect_timeout': 5,
                        'socket_keepalive': True,
                        'socket_keepalive_options': {},
                        'retry_on_timeout': True,
                        'health_check_interval': 30
                    }
                    
                    # 尝试创建Redis连接
                    if ssl:
                        # SSL连接 - 使用Redis 4.5.4兼容方式
                        try:
                            # 方法1: 直接SSL连接
                            self.redis_client = redis.Redis(
                                host=host,
                                port=port,
                                password=password,
                                ssl=True,
                                ssl_cert_reqs=None,
                                **base_kwargs
                            )
                            connection_method = "SSL Direct"
                        except Exception as e1:
                            try:
                                # 方法2: 使用连接池
                                self.connection_pool = ConnectionPool(
                                    host=host,
                                    port=port,
                                    password=password,
                                    ssl=True,
                                    ssl_cert_reqs=None,
                                    max_connections=20,
                                    **base_kwargs
                                )
                                self.redis_client = redis.Redis(connection_pool=self.connection_pool)
                                connection_method = "SSL Pool"
                            except Exception as e2:
                                # 方法3: 使用SSLConnection类
                                self.connection_pool = ConnectionPool(
                                    connection_class=redis.SSLConnection,
                                    host=host,
                                    port=port,
                                    password=password,
                                    max_connections=20,
                                    **base_kwargs
                                )
                                self.redis_client = redis.Redis(connection_pool=self.connection_pool)
                                connection_method = "SSL Connection Class"
                    else:
                        # 非SSL连接
                        try:
                            # 方法1: 直接连接
                            self.redis_client = redis.Redis(
                                host=host,
                                port=port,
                                password=password,
                                **base_kwargs
                            )
                            connection_method = "Standard"
                        except Exception:
                            # 方法2: 使用连接池
                            self.connection_pool = ConnectionPool(
                                host=host,
                                port=port,
                                password=password,
                                max_connections=20,
                                **base_kwargs
                            )
                            self.redis_client = redis.Redis(connection_pool=self.connection_pool)
                            connection_method = "Standard Pool"
                    
                    # 测试连接
                    self.redis_client.ping()
                    
                    # 在主线程中更新UI
                    self.root.after(0, self.on_connection_success, host, port, connection_method)
                    
                except redis.AuthenticationError as e:
                    self.root.after(0, self.show_connection_error, f"认证失败: {str(e)}")
                except redis.ConnectionError as e:
                    self.root.after(0, self.show_connection_error, f"连接失败: {str(e)}")
                except redis.TimeoutError as e:
                    self.root.after(0, self.show_connection_error, f"连接超时: {str(e)}")
                except Exception as e:
                    error_msg = f"连接失败: {str(e)}"
                    if 'ssl' in str(e).lower():
                        error_msg += "\n\n✅ 好消息: Redis已更新到兼容版本(4.5.4)"
                        error_msg += "\n如果仍有SSL问题，请:"
                        error_msg += "\n1. 检查Redis服务器是否支持SSL"
                        error_msg += "\n2. 验证端口号(SSL通常是6380)"
                        error_msg += "\n3. 确认Azure Redis配置正确"
                    else:
                        error_msg += "\n\n建议:"
                        error_msg += "\n1. 检查网络连接"
                        error_msg += "\n2. 验证主机地址和端口"
                        error_msg += "\n3. 确认访问密钥正确"
                    
                    self.root.after(0, self.show_connection_error, error_msg)
                    
            # 启动连接线程
            threading.Thread(target=connect_thread, daemon=True).start()
            
        except ValueError:
            self.show_connection_error("端口必须是数字")
        except Exception as e:
            self.show_connection_error(f"参数错误: {str(e)}")
            
    def on_connection_success(self, host, port, method_name=None):
        """连接成功的回调"""
        self.is_connected = True
        
        status_msg = f"已连接到 {host}:{port}"
        if method_name:
            status_msg += f" (使用 {method_name})"
        
        self.status_var.set(status_msg)
        
        # 重置分页状态
        self.current_page = 0
        self.total_keys = 0
        self.all_keys = []
        
        # 更新按钮状态
        self.disconnect_btn.config(state="normal")
        self.refresh_btn.config(state="normal")
        self.add_btn.config(state="normal")
        self.delete_btn.config(state="normal")
        self.edit_btn.config(state="normal")
        self.clear_display_btn.config(state="normal")
        
        # 根据查询模式启用相应功能
        if self.query_mode_var.get() == "key":
            self.query_btn.config(state="normal")
        
        # 默认刷新所有数据
        if self.query_mode_var.get() == "all":
            self.refresh_data()
        
        success_msg = "成功连接到Redis服务器"
        if method_name:
            success_msg += f"\n连接方式: {method_name}"
        
        messagebox.showinfo("成功", success_msg)
        
    def show_connection_error(self, error_message):
        """显示连接错误"""
        self.status_var.set(f"连接失败: {error_message}")
        self.connect_btn.config(state="normal")
        messagebox.showerror("连接错误", error_message)
            
    def disconnect_from_redis(self):
        """断开Redis连接"""
        # 停止任何正在进行的加载
        self.cancel_loading = True
        
        if self.redis_client:
            try:
                self.redis_client.close()
            except:
                pass  # 忽略关闭时的错误
            self.redis_client = None
            
        if self.connection_pool:
            try:
                self.connection_pool.disconnect()
            except:
                pass
            self.connection_pool = None
            
        self.is_connected = False
        self.loading = False
        self.cancel_loading = False
        self.status_var.set("未连接")
        
        # 重置分页状态
        self.current_page = 0
        self.total_keys = 0
        self.all_keys = []
        self.update_page_info()
        
        # 更新按钮状态
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.refresh_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.add_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        self.edit_btn.config(state="disabled")
        self.clear_display_btn.config(state="disabled")
        self.query_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        
        # 清空数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 更新统计信息
        self.stats_var.set("总计: 0 个键")
    def on_query_mode_change(self):
        """查询模式改变时的处理"""
        mode = self.query_mode_var.get()
        
        if mode == "key":
            # 启用Key查询相关控件
            self.key_query_entry.config(state="normal")
            self.fuzzy_search_check.config(state="normal")
            self.query_btn.config(state="normal" if self.is_connected else "disabled")
        else:
            # 禁用Key查询相关控件
            self.key_query_entry.config(state="disabled")
            self.fuzzy_search_check.config(state="disabled")
            self.query_btn.config(state="disabled")
            
        # 清空当前显示
        self.clear_display()
    
    def on_key_query_enter(self, event):
        """在Key查询输入框按回车时执行查询"""
        if self.query_mode_var.get() == "key" and self.is_connected:
            self.execute_query()
    
    def execute_query(self):
        """执行查询"""
        if not self.is_connected or not self.redis_client or self.loading:
            return
            
        mode = self.query_mode_var.get()
        
        if mode == "all":
            # 获取所有数据
            self.refresh_data()
        elif mode == "key":
            # 按Key查询
            self.query_by_key()
    
    def query_by_key(self):
        """按Key查询数据"""
        key_pattern = self.key_query_var.get().strip()
        if not key_pattern:
            messagebox.showwarning("输入错误", "请输入要查询的Key")
            return
            
        # 重置状态
        self.cancel_loading = False
        self.current_page = 0
        
        # 获取页大小
        try:
            self.page_size = int(self.page_size_var.get())
        except ValueError:
            self.page_size = 1000
            
        # 显示加载状态
        self.status_var.set("正在查询指定Key...")
        self.loading = True
        self.refresh_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.query_btn.config(state="disabled")
        self.root.update()
        
        # 在后台线程中查询
        def query_keys_thread():
            try:
                found_keys = []
                
                if self.fuzzy_search_var.get():
                    # 模糊查询
                    pattern = f"*{key_pattern}*"
                    self.root.after(0, lambda: self.status_var.set(f"正在模糊查询: {pattern}"))
                    
                    # 使用SCAN命令进行模糊查询
                    cursor = 0
                    scan_count = 0
                    
                    while True:
                        if self.cancel_loading:
                            break
                            
                        try:
                            cursor, keys = self.redis_client.scan(cursor, match=pattern, count=1000)
                            found_keys.extend(keys)
                            scan_count += 1
                            
                            # 更新进度
                            self.root.after(0, self.update_scan_progress, len(found_keys), scan_count)
                            
                            if cursor == 0:
                                break
                                
                            # 避免过度占用CPU
                            time.sleep(0.001)
                            
                        except redis.TimeoutError:
                            self.root.after(0, self.show_scan_warning, "查询超时，正在重试...")
                            time.sleep(0.1)
                            continue
                        except Exception as e:
                            self.root.after(0, self.show_refresh_error, f"模糊查询出错: {str(e)}")
                            return
                else:
                    # 精确查询
                    self.root.after(0, lambda: self.status_var.set(f"正在精确查询: {key_pattern}"))
                    
                    try:
                        # 检查Key是否存在
                        if self.redis_client.exists(key_pattern):
                            found_keys = [key_pattern]
                        else:
                            found_keys = []
                    except Exception as e:
                        self.root.after(0, self.show_refresh_error, f"精确查询出错: {str(e)}")
                        return
                
                if self.cancel_loading:
                    self.root.after(0, self.on_loading_cancelled)
                    return
                    
                # 保存查询结果
                self.all_keys = found_keys
                self.total_keys = len(found_keys)
                
                if not found_keys:
                    self.root.after(0, self.update_data_display, [], f"未找到匹配的键: {key_pattern}")
                    return
                
                # 加载第一页数据
                self.root.after(0, self.load_page_data, 0)
                
            except Exception as e:
                self.root.after(0, self.show_refresh_error, f"查询失败: {str(e)}")
                
        # 启动查询线程
        threading.Thread(target=query_keys_thread, daemon=True).start()
    
    def clear_display(self):
        """清空数据显示"""
        # 清空TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 重置变量
        self.all_keys = []
        self.total_keys = 0
        self.current_page = 0
        
        # 更新显示
        self.update_page_info()
        self.stats_var.set("总计: 0 个键")
        
        # 禁用分页按钮
        self.prev_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        
        if self.is_connected:
            self.status_var.set("已清空显示")
        else:
            self.status_var.set("未连接")
    
    def on_local_search_change(self, event):
        """本地搜索改变时的处理"""
        search_text = self.local_search_var.get().lower()
        
        if not search_text:
            # 如果搜索框为空，显示当前页的所有数据
            self.display_current_page()
            return
        
        # 过滤当前页面显示的数据
        all_items = self.tree.get_children()
        
        for item in all_items:
            values = self.tree.item(item, 'values')
            if values and len(values) > 0:
                key = values[0].lower()
                value = values[2].lower() if len(values) > 2 else ""
                
                # 如果key或value包含搜索文本，则显示，否则隐藏
                if search_text in key or search_text in value:
                    self.tree.move(item, '', 'end')  # 确保显示
                else:
                    # 在tkinter Treeview中隐藏项目的方法是将其移动到不可见位置
                    # 这里我们重新加载数据来实现过滤效果
                    pass
        
        # 重新过滤和显示数据
        self.filter_and_display_current_page(search_text)
    
    def filter_and_display_current_page(self, search_text):
        """过滤并显示当前页数据"""
        if not self.all_keys:
            return
            
        # 获取当前页的键
        start_index = self.current_page * self.page_size
        end_index = min(start_index + self.page_size, len(self.all_keys))
        current_page_keys = self.all_keys[start_index:end_index]
        
        # 清空当前显示
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 加载并过滤数据
        def load_filtered_data():
            try:
                filtered_data = []
                
                for key in current_page_keys:
                    if self.cancel_loading:
                        break
                        
                    try:
                        # 获取key的详细信息
                        key_info = self.get_key_info(key)
                        
                        # 应用本地搜索过滤
                        if search_text:
                            key_lower = key.lower()
                            value_lower = str(key_info['value']).lower()
                            if search_text not in key_lower and search_text not in value_lower:
                                continue
                        
                        # 格式化显示数据
                        display_data = (
                            key,
                            key_info['type'],
                            self.format_value_for_display(key_info['value']),
                            self.format_ttl(key_info['ttl']),
                            self.format_size(key_info['size'])
                        )
                        filtered_data.append(display_data)
                        
                    except Exception as e:
                        print(f"处理键 {key} 时出错: {e}")
                        continue
                
                # 在主线程中更新显示
                self.root.after(0, self.update_filtered_display, filtered_data)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"过滤数据时出错: {str(e)}"))
        
        # 在后台线程中加载过滤数据
        threading.Thread(target=load_filtered_data, daemon=True).start()
    
    def update_filtered_display(self, filtered_data):
        """更新过滤后的显示"""
        for data in filtered_data:
            self.tree.insert("", "end", values=data)
        
        # 更新状态
        total_displayed = len(filtered_data)
        search_text = self.local_search_var.get()
        if search_text:
            self.status_var.set(f"本地搜索 '{search_text}': 显示 {total_displayed} 项")
        else:
            self.status_var.set(f"已加载第 {self.current_page + 1} 页数据，共 {total_displayed} 项")
    
    def clear_local_search(self):
        """清空本地搜索"""
        self.local_search_var.set("")
        self.display_current_page()
            
    def refresh_data(self):
        """刷新Redis数据"""
        if not self.is_connected or not self.redis_client or self.loading:
            return
            
        # 重置状态
        self.cancel_loading = False
        self.current_page = 0
        
        # 获取页大小
        try:
            self.page_size = int(self.page_size_var.get())
        except ValueError:
            self.page_size = 1000
            
        # 显示加载状态
        self.status_var.set("正在获取所有键...")
        self.loading = True
        self.refresh_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.query_btn.config(state="disabled")
        self.root.update()
        
        # 在后台线程中获取所有键
        def fetch_keys_thread():
            try:
                # 使用SCAN命令分批获取所有键
                all_keys = []
                cursor = 0
                scan_count = 0
                
                while True:
                    if self.cancel_loading:
                        break
                        
                    try:
                        # 使用SCAN命令，每次获取1000个键
                        cursor, keys = self.redis_client.scan(cursor, match="*", count=1000)
                        all_keys.extend(keys)
                        scan_count += 1
                        
                        # 更新进度
                        self.root.after(0, self.update_scan_progress, len(all_keys), scan_count)
                        
                        if cursor == 0:
                            break
                            
                        # 避免过度占用CPU
                        time.sleep(0.001)
                        
                    except redis.TimeoutError:
                        # 如果超时，继续尝试
                        self.root.after(0, self.show_scan_warning, "扫描超时，正在重试...")
                        time.sleep(0.1)
                        continue
                    except Exception as e:
                        self.root.after(0, self.show_refresh_error, f"扫描键时出错: {str(e)}")
                        return
                
                if self.cancel_loading:
                    self.root.after(0, self.on_loading_cancelled)
                    return
                    
                # 保存所有键
                self.all_keys = all_keys
                self.total_keys = len(all_keys)
                
                if not all_keys:
                    self.root.after(0, self.update_data_display, [], "未找到任何键")
                    return
                
                # 加载第一页数据
                self.root.after(0, self.load_page_data, 0)
                
            except Exception as e:
                self.root.after(0, self.show_refresh_error, f"获取键列表失败: {str(e)}")
                
        # 启动键获取线程
        threading.Thread(target=fetch_keys_thread, daemon=True).start()
        # 启动键获取线程
        threading.Thread(target=fetch_keys_thread, daemon=True).start()
    
    def update_scan_progress(self, keys_found, scan_count):
        """更新扫描进度"""
        self.status_var.set(f"正在扫描... 已找到 {keys_found} 个键 (扫描轮次: {scan_count})")
        
    def show_scan_warning(self, message):
        """显示扫描警告"""
        self.status_var.set(message)
        
    def load_page_data(self, page_num):
        """加载指定页的数据"""
        if not self.is_connected or not self.redis_client or self.cancel_loading:
            return
            
        self.current_page = page_num
        start_idx = page_num * self.page_size
        end_idx = start_idx + self.page_size
        page_keys = self.all_keys[start_idx:end_idx]
        
        if not page_keys:
            self.update_data_display([], f"第 {page_num + 1} 页无数据")
            return
            
        # 显示加载状态
        self.status_var.set(f"正在加载第 {page_num + 1} 页数据...")
        self.root.update()
        
        # 在后台线程中获取页面数据
        def fetch_page_data_thread():
            try:
                data_items = []
                
                # 分批处理，避免一次性处理太多
                batch_size = 50
                for i in range(0, len(page_keys), batch_size):
                    if self.cancel_loading:
                        break
                        
                    batch_keys = page_keys[i:i + batch_size]
                    
                    try:
                        # 使用pipeline批量获取数据
                        pipe = self.redis_client.pipeline(transaction=False)
                        
                        # 批量获取类型和TTL
                        for key in batch_keys:
                            pipe.type(key)
                            pipe.ttl(key)
                        
                        # 设置较长的超时时间
                        pipe.socket_timeout = 15
                        results = pipe.execute()
                        
                        # 处理结果
                        for j, key in enumerate(batch_keys):
                            if self.cancel_loading:
                                break
                                
                            try:
                                data_type = results[j * 2]
                                ttl = results[j * 2 + 1]
                                
                                if ttl == -1:
                                    ttl_text = "永不过期"
                                elif ttl == -2:
                                    ttl_text = "已过期"
                                else:
                                    ttl_text = f"{ttl}秒"
                                    
                                # 获取值预览和大小
                                value_text, size = self.get_value_preview_safe(key, data_type)
                                
                                data_items.append((key, data_type, value_text, ttl_text, size))
                                
                            except Exception as e:
                                # 单个键出错不影响其他键
                                data_items.append((key, "error", f"Error: {str(e)}", "N/A", 0))
                                continue
                        
                        # 更新进度
                        progress = min(i + batch_size, len(page_keys))
                        self.root.after(0, self.update_load_progress, progress, len(page_keys), page_num + 1)
                        
                        # 避免过度占用CPU
                        time.sleep(0.01)
                        
                    except redis.TimeoutError:
                        # 超时处理：跳过这批数据
                        for key in batch_keys:
                            data_items.append((key, "timeout", "加载超时", "N/A", 0))
                        continue
                    except Exception as e:
                        # 批次错误处理
                        for key in batch_keys:
                            data_items.append((key, "error", f"Error: {str(e)}", "N/A", 0))
                        continue
                
                if self.cancel_loading:
                    self.root.after(0, self.on_loading_cancelled)
                    return
                    
                # 在主线程中更新UI
                status_msg = f"第 {page_num + 1} 页，共 {len(data_items)} 个键"
                self.root.after(0, self.update_data_display, data_items, status_msg)
                
            except Exception as e:
                error_msg = f"加载第 {page_num + 1} 页失败: {str(e)}"
                self.root.after(0, self.show_refresh_error, error_msg)
                
        # 启动页面数据获取线程
        threading.Thread(target=fetch_page_data_thread, daemon=True).start()
    
    def display_current_page(self):
        """显示当前页数据（不重新从Redis获取）"""
        if not self.all_keys:
            return
        
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.all_keys))
        page_keys = self.all_keys[start_idx:end_idx]
        
        # 清空当前显示
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 从Redis重新获取数据并显示
        self.load_page_data(self.current_page)
    
    def get_key_info(self, key):
        """获取键的详细信息"""
        try:
            # 获取数据类型
            data_type = self.redis_client.type(key)
            
            # 获取TTL
            ttl = self.redis_client.ttl(key)
            
            # 获取值和大小
            value, size = self.get_value_preview_safe(key, data_type)
            
            return {
                'type': data_type,
                'value': value,
                'ttl': ttl,
                'size': size
            }
        except Exception as e:
            return {
                'type': 'error',
                'value': f'Error: {str(e)}',
                'ttl': -1,
                'size': 0
            }
    
    def format_value_for_display(self, value):
        """格式化值用于显示"""
        if value is None:
            return "None"
        
        value_str = str(value)
        if len(value_str) > 100:
            return value_str[:100] + "..."
        return value_str
    
    def format_ttl(self, ttl):
        """格式化TTL显示"""
        if ttl == -1:
            return "永不过期"
        elif ttl == -2:
            return "已过期"
        elif ttl > 0:
            return f"{ttl}秒"
        else:
            return "N/A"
    
    def format_size(self, size):
        """格式化大小显示"""
        if isinstance(size, int):
            if size < 1024:
                return f"{size}B"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f}KB"
            else:
                return f"{size/(1024*1024):.1f}MB"
        return str(size)
    
    def update_page_info(self):
        """更新分页信息"""
        if self.total_keys == 0:
            self.page_info_var.set("第 0 页，共 0 页")
            self.stats_var.set("总计: 0 个键")
            return
        
        total_pages = (self.total_keys + self.page_size - 1) // self.page_size
        current_page_display = self.current_page + 1
        
        self.page_info_var.set(f"第 {current_page_display} 页，共 {total_pages} 页")
        self.stats_var.set(f"总计: {self.total_keys} 个键")
        
        # 更新分页按钮状态
        self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_page < total_pages - 1 else "disabled")
    
    def update_data_display(self, data_items, status_message):
        """更新数据显示"""
        # 清空当前数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 插入新数据
        for item in data_items:
            self.tree.insert("", "end", values=item)
        
        # 更新状态和分页信息
        self.status_var.set(status_message)
        self.update_page_info()
        
        # 更新按钮状态
        self.loading = False
        self.refresh_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # 根据查询模式启用查询按钮
        if self.query_mode_var.get() == "key":
            self.query_btn.config(state="normal")
    
    def update_scan_progress(self, keys_found, scan_count):
        """更新扫描进度"""
        mode = self.query_mode_var.get()
        if mode == "all":
            self.status_var.set(f"正在扫描所有键... 已找到 {keys_found} 个键 (扫描轮次: {scan_count})")
        else:
            self.status_var.set(f"正在查询... 已找到 {keys_found} 个匹配键 (扫描轮次: {scan_count})")
        
    def show_scan_warning(self, message):
        """显示扫描警告"""
        self.status_var.set(message)
        
    def show_refresh_error(self, error_message):
        """显示刷新错误"""
        self.status_var.set(f"错误: {error_message}")
        self.loading = False
        self.refresh_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # 根据查询模式启用查询按钮
        if self.query_mode_var.get() == "key":
            self.query_btn.config(state="normal")
        
        messagebox.showerror("错误", error_message)
    
    def on_loading_cancelled(self):
        """加载取消时的处理"""
        self.loading = False
        self.cancel_loading = False
        self.refresh_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # 根据查询模式启用查询按钮
        if self.query_mode_var.get() == "key":
            self.query_btn.config(state="normal")
        
        self.status_var.set("操作已取消")
    
    def stop_loading(self):
        """停止加载"""
        self.cancel_loading = True
        self.status_var.set("正在停止...")
    
    def update_load_progress(self, current, total, page_num):
        """更新加载进度"""
        percentage = int((current / total) * 100)
        self.status_var.set(f"正在加载第 {page_num} 页... {percentage}% ({current}/{total})")
    
    def get_value_preview_safe(self, key, data_type):
        """安全获取值预览和大小"""
        try:
            if data_type == "string":
                # 只获取前100个字符作为预览
                value = self.redis_client.get(key)
                if value is None:
                    return "None", 0
                value_str = str(value)
                value_text = value_str[:100]
                if len(value_str) > 100:
                    value_text += "..."
                return value_text, len(value_str)
                
            elif data_type == "list":
                length = self.redis_client.llen(key)
                return f"List ({length} items)", length
                
            elif data_type == "set":
                length = self.redis_client.scard(key)
                return f"Set ({length} members)", length
                
            elif data_type == "zset":
                length = self.redis_client.zcard(key)
                return f"ZSet ({length} members)", length
                
            elif data_type == "hash":
                length = self.redis_client.hlen(key)
                return f"Hash ({length} fields)", length
                
            else:
                return f"Unknown type: {data_type}", 0
                
        except redis.TimeoutError:
            return "获取超时", 0
        except Exception as e:
            return f"错误: {str(e)}", 0
    
    def stop_loading(self):
        """停止加载"""
        self.cancel_loading = True
        self.status_var.set("正在停止加载...")
        
    def on_loading_cancelled(self):
        """加载取消的回调"""
        self.loading = False
        self.cancel_loading = False
        self.refresh_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("加载已取消")
    
    def update_data_display(self, data_items, status_message):
        """更新数据显示"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 添加新数据
        for item in data_items:
            self.tree.insert("", "end", values=item)
            
        # 更新状态和按钮
        self.loading = False
        self.cancel_loading = False
        self.refresh_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # 更新分页信息
        self.update_page_info()
        
        # 更新状态
        if self.total_keys > 0:
            total_pages = (self.total_keys + self.page_size - 1) // self.page_size
            self.status_var.set(f"已连接 - {status_message} (总共 {self.total_keys} 个键，共 {total_pages} 页)")
        else:
            self.status_var.set(f"已连接 - {status_message}")
    
    def update_page_info(self):
        """更新分页信息"""
        if self.total_keys > 0:
            total_pages = (self.total_keys + self.page_size - 1) // self.page_size
            self.page_info_var.set(f"第 {self.current_page + 1} 页，共 {total_pages} 页")
            
            # 更新分页按钮状态
            self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
            self.next_btn.config(state="normal" if self.current_page < total_pages - 1 else "disabled")
        else:
            self.page_info_var.set("第 0 页，共 0 页")
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 0 and not self.loading:
            self.load_page_data(self.current_page - 1)
    
    def next_page(self):
        """下一页"""
        total_pages = (self.total_keys + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1 and not self.loading:
            self.load_page_data(self.current_page + 1)
    
    def on_page_size_change(self, event):
        """页大小改变事件"""
        if not self.loading and self.total_keys > 0:
            self.refresh_data()
        
    def show_refresh_error(self, error_message):
        """显示刷新错误"""
        self.loading = False
        self.cancel_loading = False
        self.refresh_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set(f"加载失败: {error_message}")
        messagebox.showerror("错误", error_message)
            
    def add_key_dialog(self):
        """添加新键的对话框"""
        if not self.is_connected:
            return
            
        dialog = AddKeyDialog(self.root, self.redis_client)
        if dialog.result:
            self.refresh_data()
            
    def delete_selected_key(self):
        """删除选中的键"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择要删除的键")
            return
            
        # 获取选中的键
        key = self.tree.item(selected_item[0])["values"][0]
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除键 '{key}' 吗？"):
            try:
                self.redis_client.delete(key)
                messagebox.showinfo("成功", f"键 '{key}' 已删除")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
                
    def edit_selected_key(self):
        """编辑选中的键"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择要编辑的键")
            return
            
        # 获取选中的键和类型
        item_values = self.tree.item(selected_item[0])["values"]
        key = item_values[0]
        data_type = item_values[1]
        
        try:
            if data_type == "string":
                current_value = self.redis_client.get(key)
                new_value = simpledialog.askstring("编辑值", f"编辑键 '{key}' 的值:", initialvalue=current_value)
                if new_value is not None:
                    self.redis_client.set(key, new_value)
                    messagebox.showinfo("成功", "值已更新")
                    self.refresh_data()
            else:
                messagebox.showinfo("信息", f"暂不支持编辑 {data_type} 类型的数据")
                
        except Exception as e:
            messagebox.showerror("错误", f"编辑失败: {str(e)}")
            
    def on_item_double_click(self, event):
        """双击事件处理"""
        self.edit_selected_key()
        
    def on_item_single_click(self, event):
        """单击事件处理 - 显示完整值"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        # 获取选中的键和类型
        item_values = self.tree.item(selected_item[0])["values"]
        key = item_values[0]
        data_type = item_values[1]
        
        # 显示完整值
        self.show_full_value(key, data_type)
        
    def show_full_value(self, key, data_type):
        """显示键的完整值"""
        if not self.is_connected or not self.redis_client:
            return
            
        try:
            # 创建显示窗口
            value_window = tk.Toplevel(self.root)
            value_window.title(f"键值详情: {key}")
            value_window.geometry("600x400")
            value_window.resizable(True, True)
            value_window.transient(self.root)
            
            # 居中显示
            value_window.geometry("+{}+{}".format(
                self.root.winfo_rootx() + 100,
                self.root.winfo_rooty() + 100
            ))
            
            # 创建主框架
            main_frame = ttk.Frame(value_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 键信息框架
            info_frame = ttk.LabelFrame(main_frame, text="键信息", padding="5")
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            # 显示键信息
            ttk.Label(info_frame, text="键名:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            ttk.Label(info_frame, text=key, font=("", 9, "bold")).grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(info_frame, text="类型:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
            ttk.Label(info_frame, text=data_type, font=("", 9, "bold")).grid(row=0, column=3, sticky=tk.W)
            
            # TTL信息
            ttl = self.redis_client.ttl(key)
            ttl_text = "永不过期" if ttl == -1 else f"{ttl}秒" if ttl > 0 else "已过期"
            ttk.Label(info_frame, text="TTL:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
            ttl_label = ttk.Label(info_frame, text=ttl_text, font=("", 9, "bold"))
            ttl_label.grid(row=1, column=1, sticky=tk.W)
            
            # 值显示框架
            value_frame = ttk.LabelFrame(main_frame, text="值内容", padding="5")
            value_frame.pack(fill=tk.BOTH, expand=True)
            value_frame.columnconfigure(0, weight=1)
            value_frame.rowconfigure(0, weight=1)
            
            # 创建文本框和滚动条
            text_widget = tk.Text(value_frame, wrap=tk.WORD, font=("Consolas", 10))
            v_scroll = ttk.Scrollbar(value_frame, orient="vertical", command=text_widget.yview)
            h_scroll = ttk.Scrollbar(value_frame, orient="horizontal", command=text_widget.xview)
            text_widget.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            # 布局
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
            h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
            
            # 获取并显示值
            value_content = self.get_full_value_content(key, data_type)
            text_widget.insert(1.0, value_content)
            text_widget.config(state=tk.DISABLED)  # 设为只读
            
            # 按钮框架
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=(10, 0))
            
            # 复制按钮
            def copy_to_clipboard():
                value_window.clipboard_clear()
                value_window.clipboard_append(value_content)
                messagebox.showinfo("成功", "内容已复制到剪贴板")
                
            ttk.Button(btn_frame, text="复制内容", command=copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 10))
            
            # 关闭按钮
            ttk.Button(btn_frame, text="关闭", command=value_window.destroy).pack(side=tk.RIGHT)
            
            # 刷新按钮
            def refresh_value():
                try:
                    new_content = self.get_full_value_content(key, data_type)
                    text_widget.config(state=tk.NORMAL)
                    text_widget.delete(1.0, tk.END)
                    text_widget.insert(1.0, new_content)
                    text_widget.config(state=tk.DISABLED)
                    
                    # 更新TTL
                    new_ttl = self.redis_client.ttl(key)
                    new_ttl_text = "永不过期" if new_ttl == -1 else f"{new_ttl}秒" if new_ttl > 0 else "已过期"
                    ttl_label.config(text=new_ttl_text)
                    
                except Exception as e:
                    messagebox.showerror("错误", f"刷新失败: {str(e)}")
                    
            ttk.Button(btn_frame, text="刷新", command=refresh_value).pack(side=tk.RIGHT, padx=(0, 10))
            
        except Exception as e:
            messagebox.showerror("错误", f"无法显示键值: {str(e)}")
            
    def get_full_value_content(self, key, data_type):
        """获取键的完整内容"""
        try:
            # 设置较长的超时时间用于获取完整内容
            if data_type == "string":
                return str(self.redis_client.get(key))
                
            elif data_type == "list":
                # 分批获取大列表，避免超时
                length = self.redis_client.llen(key)
                if length > 10000:
                    # 大列表只显示前1000项
                    items = self.redis_client.lrange(key, 0, 999)
                    result = "\n".join([f"[{i}] {item}" for i, item in enumerate(items)])
                    result += f"\n\n... 还有 {length - 1000} 项未显示（列表过大）"
                    return result
                else:
                    items = self.redis_client.lrange(key, 0, -1)
                    return "\n".join([f"[{i}] {item}" for i, item in enumerate(items)])
                
            elif data_type == "set":
                # 分批获取大集合
                length = self.redis_client.scard(key)
                if length > 10000:
                    # 大集合只显示部分成员
                    items = list(self.redis_client.sscan_iter(key, count=1000))[:1000]
                    result = "\n".join(sorted(items))
                    result += f"\n\n... 还有约 {length - 1000} 个成员未显示（集合过大）"
                    return result
                else:
                    items = self.redis_client.smembers(key)
                    return "\n".join(sorted(items))
                
            elif data_type == "zset":
                # 分批获取大有序集合
                length = self.redis_client.zcard(key)
                if length > 10000:
                    # 大有序集合只显示前1000项
                    items = self.redis_client.zrange(key, 0, 999, withscores=True)
                    result = "\n".join([f"{member} (score: {score})" for member, score in items])
                    result += f"\n\n... 还有 {length - 1000} 项未显示（有序集合过大）"
                    return result
                else:
                    items = self.redis_client.zrange(key, 0, -1, withscores=True)
                    return "\n".join([f"{member} (score: {score})" for member, score in items])
                
            elif data_type == "hash":
                # 分批获取大哈希表
                length = self.redis_client.hlen(key)
                if length > 10000:
                    # 大哈希表只显示部分字段
                    items = {}
                    count = 0
                    for field, value in self.redis_client.hscan_iter(key, count=1000):
                        items[field] = value
                        count += 1
                        if count >= 1000:
                            break
                    result = "\n".join([f"{field}: {value}" for field, value in items.items()])
                    result += f"\n\n... 还有约 {length - count} 个字段未显示（哈希表过大）"
                    return result
                else:
                    items = self.redis_client.hgetall(key)
                    return "\n".join([f"{field}: {value}" for field, value in items.items()])
                
            else:
                return f"不支持显示类型: {data_type}"
                
        except redis.TimeoutError:
            return f"获取值时超时 - 数据可能过大\n\n建议：\n1. 检查网络连接\n2. 该键可能包含大量数据\n3. 尝试刷新或使用更小的数据集"
        except redis.ConnectionError:
            return "连接已断开，请重新连接Redis服务器"
        except Exception as e:
            return f"获取值时出错: {str(e)}\n\n建议：\n1. 检查键是否仍然存在\n2. 检查网络连接\n3. 尝试刷新数据"
        
    def on_search_change(self, event):
        """搜索框内容变化时的处理"""
        # 延迟搜索以避免频繁查询
        if hasattr(self, 'search_timer'):
            self.root.after_cancel(self.search_timer)
        self.search_timer = self.root.after(1000, self.refresh_data)  # 增加延迟到1秒
        
    def clear_search(self):
        """清空搜索"""
        self.search_var.set("")
        if not self.loading:
            self.refresh_data()


class AddKeyDialog:
    def __init__(self, parent, redis_client):
        self.redis_client = redis_client
        self.result = False
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加新键")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 键名
        ttk.Label(main_frame, text="键名:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(main_frame, textvariable=self.key_var, width=40)
        self.key_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 数据类型
        ttk.Label(main_frame, text="类型:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.type_var = tk.StringVar(value="string")
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                  values=["string", "list", "set", "hash"], 
                                  state="readonly", width=15)
        type_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        type_combo.bind("<<ComboboxSelected>>", self.on_type_change)
        
        # 值
        ttk.Label(main_frame, text="值:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        self.value_text = tk.Text(main_frame, width=40, height=8)
        self.value_text.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # TTL设置
        ttl_frame = ttk.Frame(main_frame)
        ttl_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.ttl_var = tk.BooleanVar()
        ttl_check = ttk.Checkbutton(ttl_frame, text="设置过期时间", variable=self.ttl_var)
        ttl_check.pack(side=tk.LEFT)
        
        self.ttl_seconds_var = tk.StringVar(value="3600")
        ttl_entry = ttk.Entry(ttl_frame, textvariable=self.ttl_seconds_var, width=10)
        ttl_entry.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(ttl_frame, text="秒").pack(side=tk.LEFT)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT)
        
        # 设置初始焦点
        self.key_entry.focus()
        
    def on_type_change(self, event):
        """类型改变时更新值输入框的提示"""
        data_type = self.type_var.get()
        self.value_text.delete(1.0, tk.END)
        
        if data_type == "string":
            self.value_text.insert(1.0, "输入字符串值")
        elif data_type == "list":
            self.value_text.insert(1.0, "每行一个列表元素")
        elif data_type == "set":
            self.value_text.insert(1.0, "每行一个集合元素")
        elif data_type == "hash":
            self.value_text.insert(1.0, "每行一个field:value对，用冒号分隔")
            
    def on_ok(self):
        """确定按钮处理"""
        key = self.key_var.get().strip()
        if not key:
            messagebox.showerror("错误", "请输入键名")
            return
            
        value_content = self.value_text.get(1.0, tk.END).strip()
        if not value_content:
            messagebox.showerror("错误", "请输入值")
            return
            
        try:
            data_type = self.type_var.get()
            
            if data_type == "string":
                self.redis_client.set(key, value_content)
                
            elif data_type == "list":
                # 清空可能存在的key
                self.redis_client.delete(key)
                # 添加列表元素
                for line in value_content.split('\n'):
                    if line.strip():
                        self.redis_client.rpush(key, line.strip())
                        
            elif data_type == "set":
                # 清空可能存在的key
                self.redis_client.delete(key)
                # 添加集合元素
                for line in value_content.split('\n'):
                    if line.strip():
                        self.redis_client.sadd(key, line.strip())
                        
            elif data_type == "hash":
                # 清空可能存在的key
                self.redis_client.delete(key)
                # 添加哈希字段
                for line in value_content.split('\n'):
                    if line.strip() and ':' in line:
                        field, value = line.split(':', 1)
                        self.redis_client.hset(key, field.strip(), value.strip())
                        
            # 设置TTL
            if self.ttl_var.get():
                try:
                    ttl_seconds = int(self.ttl_seconds_var.get())
                    self.redis_client.expire(key, ttl_seconds)
                except ValueError:
                    messagebox.showwarning("警告", "TTL值无效，将使用默认设置")
                    
            self.result = True
            self.dialog.destroy()
            messagebox.showinfo("成功", f"键 '{key}' 已添加")
            
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")
            
    def on_cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = AzureRedisManager(root)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap("redis.ico")
    except:
        pass
        
    # 处理窗口关闭事件
    def on_closing():
        if app.is_connected:
            app.disconnect_from_redis()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
