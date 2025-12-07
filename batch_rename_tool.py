import os
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import re

class BatchRenameTool:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文件重命名工具")
        self.root.geometry("650x580")  # 增加窗口高度
        self.root.resizable(False, False)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Microsoft YaHei', 10))
        self.style.configure('TButton', font=('Microsoft YaHei', 10))
        self.style.configure('TEntry', font=('Microsoft YaHei', 10))
        self.style.configure('TCombobox', font=('Microsoft YaHei', 10))
        
        # 变量
        self.folder_path = tk.StringVar()
        self.prefix = tk.StringVar()
        self.suffix = tk.StringVar()
        self.sort_method = tk.StringVar(value="文件名")
        self.number_style = tk.StringVar(value="1,2,3")
        
        self.create_widgets()
        
        # 绑定变量变化事件
        self.folder_path.trace('w', self.on_parameter_change)
        self.prefix.trace('w', self.on_parameter_change)
        self.suffix.trace('w', self.on_parameter_change)
        self.sort_method.trace('w', self.on_parameter_change)
        self.number_style.trace('w', self.on_parameter_change)
    
    def create_widgets(self):
        # 主框架 - 增加底部内边距
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主框架的行列权重，让内容更好地分布
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 文件夹选择
        ttk.Label(main_frame, text="选择文件夹：").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        folder_entry = ttk.Entry(main_frame, textvariable=self.folder_path, width=50)
        folder_entry.grid(row=0, column=1, pady=(0, 5), padx=5, sticky=tk.EW)
        browse_btn = ttk.Button(main_frame, text="浏览...", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, pady=(0, 5))
        
        # 前缀设置
        ttk.Label(main_frame, text="文件名前缀：").grid(row=1, column=0, sticky=tk.W, pady=5)
        prefix_entry = ttk.Entry(main_frame, textvariable=self.prefix, width=50)
        prefix_entry.grid(row=1, column=1, columnspan=2, pady=5, padx=5, sticky=tk.EW)
        
        # 后缀设置
        ttk.Label(main_frame, text="文件名后缀：").grid(row=2, column=0, sticky=tk.W, pady=5)
        suffix_entry = ttk.Entry(main_frame, textvariable=self.suffix, width=50)
        suffix_entry.grid(row=2, column=1, columnspan=2, pady=5, padx=5, sticky=tk.EW)
        
        # 排序方式
        ttk.Label(main_frame, text="排序方式：").grid(row=3, column=0, sticky=tk.W, pady=5)
        sort_combo = ttk.Combobox(main_frame, textvariable=self.sort_method, width=47, state="readonly")
        sort_combo['values'] = ('文件名', '修改时间', '创建时间', '文件大小')
        sort_combo.grid(row=3, column=1, columnspan=2, pady=5, padx=5, sticky=tk.W)
        
        # 编号样式
        ttk.Label(main_frame, text="编号样式：").grid(row=4, column=0, sticky=tk.W, pady=5)
        number_combo = ttk.Combobox(main_frame, textvariable=self.number_style, width=47, state="readonly")
        number_combo['values'] = ('1,2,3', '01,02,03', '001,002,003', '一、二、三', 'Ⅰ,Ⅱ,Ⅲ', 'a,b,c', 'A,B,C')
        number_combo.grid(row=4, column=1, columnspan=2, pady=5, padx=5, sticky=tk.W)
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 10))
        
        # 预览区域标题
        preview_label = ttk.Label(main_frame, text="重命名预览：", font=('Microsoft YaHei', 11, 'bold'))
        preview_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        # 预览文本框框架 - 增加底部间距
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=7, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))
        preview_frame.columnconfigure(0, weight=1)
        
        # 预览文本框
        self.preview_text = tk.Text(preview_frame, width=75, height=12, font=('Microsoft YaHei', 9))
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.rowconfigure(0, weight=1)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="请选择文件夹开始预览", font=('Microsoft YaHei', 9))
        self.status_label.grid(row=8, column=0, columnspan=3, pady=(0, 20))
        
        # 按钮框架 - 增加底部间距
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=(0, 30))  # 增加底部间距到30
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        # 按钮样式 - 增加内边距和宽度
        button_style = {'width': 15, 'padding': 8}
        
        self.preview_btn = ttk.Button(button_frame, text="🔄 刷新预览", command=self.preview_rename, **button_style)
        self.preview_btn.grid(row=0, column=0, padx=10, sticky=tk.EW)
        
        self.execute_btn = ttk.Button(button_frame, text="✅ 执行重命名", command=self.execute_rename, state=tk.DISABLED, **button_style)
        self.execute_btn.grid(row=0, column=1, padx=10, sticky=tk.EW)
        
        exit_btn = ttk.Button(button_frame, text="❌ 退出", command=self.root.quit, **button_style)
        exit_btn.grid(row=0, column=2, padx=10, sticky=tk.EW)
        
        # 设置窗口最小大小
        self.root.minsize(650, 580)
        
        # 初始化提示
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = """欢迎使用批量文件重命名工具！

使用步骤：
1. 点击"浏览..."选择要重命名的文件夹
2. 设置文件名前缀和后缀（可选）
3. 选择排序方式和编号样式
4. 点击"刷新预览"查看重命名效果
5. 确认无误后点击"执行重命名"

注意：重命名操作不可撤销，请谨慎操作！"""
        
        self.preview_text.insert(tk.END, welcome_text)
        self.preview_text.config(state=tk.DISABLED)
    
    def on_parameter_change(self, *args):
        """参数变化时的回调函数"""
        if self.folder_path.get():
            self.status_label.config(text="参数已更改，点击刷新预览查看效果")
            self.preview_btn.config(state=tk.NORMAL)
    
    def browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory(title="选择要重命名文件的文件夹")
        if folder:
            self.folder_path.set(folder)
            self.status_label.config(text="文件夹已选择，点击刷新预览")
            self.preview_btn.config(state=tk.NORMAL)
            # 自动刷新预览
            self.root.after(100, self.preview_rename)
    
    def get_file_list(self):
        """获取文件列表"""
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            return []
        
        try:
            files = glob.glob(os.path.join(folder, "*"))
            files = [f for f in files if os.path.isfile(f)]
            
            # 根据排序方式排序
            sort_method = self.sort_method.get()
            if sort_method == "文件名":
                files.sort(key=lambda x: os.path.basename(x).lower())
            elif sort_method == "修改时间":
                files.sort(key=lambda x: os.path.getmtime(x))
            elif sort_method == "创建时间":
                files.sort(key=lambda x: os.path.getctime(x))
            elif sort_method == "文件大小":
                files.sort(key=lambda x: os.path.getsize(x))
            
            return files
        except Exception as e:
            messagebox.showerror("错误", f"获取文件列表失败：{str(e)}")
            return []
    
    def get_number_string(self, index, total):
        """获取编号字符串"""
        style = self.number_style.get()
        if style == "1,2,3":
            return str(index + 1)
        elif style == "01,02,03":
            return f"{index + 1:02d}"
        elif style == "001,002,003":
            return f"{index + 1:03d}"
        elif style == "一、二、三":
            chinese_nums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                           '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']
            if index < len(chinese_nums):
                return chinese_nums[index]
            else:
                return str(index + 1)
        elif style == "Ⅰ,Ⅱ,Ⅲ":
            roman_numerals = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ',
                             'Ⅺ', 'Ⅻ', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX']
            if index < len(roman_numerals):
                return roman_numerals[index]
            else:
                return str(index + 1)
        elif style == "a,b,c":
            return chr(ord('a') + index)
        elif style == "A,B,C":
            return chr(ord('A') + index)
        else:
            return str(index + 1)
    
    def generate_new_name(self, old_name, index, total):
        """生成新文件名"""
        folder = self.folder_path.get()
        prefix = self.prefix.get()
        suffix = self.suffix.get()
        
        # 获取文件扩展名
        name_part, ext = os.path.splitext(os.path.basename(old_name))
        
        # 生成编号
        number_str = self.get_number_string(index, total)
        
        # 组合新文件名
        new_name = f"{prefix}{number_str}{suffix}{ext}"
        
        return new_name
    
    def preview_rename(self):
        """预览重命名结果"""
        # 启用文本框编辑
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        files = self.get_file_list()
        if not files:
            self.preview_text.insert(tk.END, "❌ 请先选择有效的文件夹！")
            self.status_label.config(text="请选择文件夹")
            self.execute_btn.config(state=tk.DISABLED)
            self.preview_text.config(state=tk.DISABLED)
            return
        
        if len(files) == 0:
            self.preview_text.insert(tk.END, "❌ 所选文件夹中没有文件！")
            self.status_label.config(text="文件夹中没有文件")
            self.execute_btn.config(state=tk.DISABLED)
            self.preview_text.config(state=tk.DISABLED)
            return
        
        # 显示预览信息
        self.preview_text.insert(tk.END, f"📁 文件夹：{self.folder_path.get()}\n")
        self.preview_text.insert(tk.END, f"📊 文件总数：{len(files)} 个\n")
        self.preview_text.insert(tk.END, f"🔄 排序方式：{self.sort_method.get()}\n")
        self.preview_text.insert(tk.END, f"🔢 编号样式：{self.number_style.get()}\n")
        self.preview_text.insert(tk.END, "=" * 80 + "\n\n")
        
        # 显示重命名预览
        for i, file_path in enumerate(files):
            old_name = os.path.basename(file_path)
            new_name = self.generate_new_name(file_path, i, len(files))
            self.preview_text.insert(tk.END, f"{i+1:3d}. {old_name}\n")
            self.preview_text.insert(tk.END, f"     → {new_name}\n\n")
        
        # 禁用文本框编辑
        self.preview_text.config(state=tk.DISABLED)
        
        # 更新状态
        self.status_label.config(text=f"预览完成，共 {len(files)} 个文件")
        self.execute_btn.config(state=tk.NORMAL)
    
    def execute_rename(self):
        """执行重命名操作"""
        files = self.get_file_list()
        if not files:
            messagebox.showerror("错误", "请先选择有效的文件夹！")
            return
        
        # 确认对话框
        result = messagebox.askyesno("确认重命名", 
                                   f"确定要重命名 {len(files)} 个文件吗？\n\n此操作不可撤销！")
        if not result:
            return
        
        success_count = 0
        error_count = 0
        error_messages = []
        
        for i, file_path in enumerate(files):
            try:
                old_name = os.path.basename(file_path)
                new_name = self.generate_new_name(file_path, i, len(files))
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                
                # 检查文件是否已存在
                if os.path.exists(new_path) and new_path != file_path:
                    error_messages.append(f"文件已存在，跳过：{new_name}")
                    error_count += 1
                    continue
                
                # 执行重命名
                os.rename(file_path, new_path)
                success_count += 1
                
            except Exception as e:
                error_messages.append(f"重命名失败：{old_name} - {str(e)}")
                error_count += 1
        
        # 显示结果
        message = f"🎉 重命名完成！\n\n✅ 成功：{success_count} 个文件"
        if error_count > 0:
            message += f"\n❌ 失败：{error_count} 个文件"
        
        if error_messages:
            message += f"\n\n错误详情（显示前5个）：\n" + "\n".join(error_messages[:5])
            if len(error_messages) > 5:
                message += f"\n... 还有 {len(error_messages) - 5} 个错误"
        
        messagebox.showinfo("重命名结果", message)
        
        # 刷新预览
        self.preview_rename()

if __name__ == "__main__":
    root = tk.Tk()
    # 设置窗口图标（如果有的话）
    try:
        # 尝试设置窗口图标，如果没有图标文件会跳过
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = BatchRenameTool(root)
    root.mainloop()