import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
# from googletrans import Translator
import json
import requests
from pathlib import Path
# import argostranslate.package, argostranslate.translate
from pathlib import Path
import requests
import baidu_translate as fanyi  # 确保该模块可用

# 下载并安装语言包
# pkg_url = "https://www.argosopentech.com/argospm/packages/en_zh.argosmodel"
# pkg_path = Path("en_zh.argosmodel")
# if not pkg_path.exists():
#     r = requests.get(pkg_url)
#     pkg_path.write_bytes(r.content)

# argostranslate.package.install_from_path(str(pkg_path))


LC_DB_PATH = "/Users/ivcylc_lca/Desktop/papers/lc_paper_list.db"
NIPS_DB_PATHS = {
    # neurips
    "neurips2022": ("/Users/ivcylc_lca/Desktop/papers/nips2022.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/nips/nips2022.json"),
    "neurips2023": ("/Users/ivcylc_lca/Desktop/papers/nips2023.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/nips/nips2023.json"),
    "neurips2024": ("/Users/ivcylc_lca/Desktop/papers/nips2024.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/nips/nips2024.json"),

    # aaai
    "aaai2023": ("/Users/ivcylc_lca/Desktop/papers/aaai2023.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/aaai/aaai2023.json"),
    "aaai2024": ("/Users/ivcylc_lca/Desktop/papers/aaai2024.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/aaai/aaai2024.json"),
    "aaai2025": ("/Users/ivcylc_lca/Desktop/papers/aaai2025.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/aaai/aaai2025.json"),

    # iclr
    "iclr2023": ("/Users/ivcylc_lca/Desktop/papers/iclr2023.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/iclr/iclr2023.json"),
    "iclr2024": ("/Users/ivcylc_lca/Desktop/papers/iclr2024.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/iclr/iclr2024.json"),
    "iclr2025": ("/Users/ivcylc_lca/Desktop/papers/iclr2025.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/iclr/iclr2025.json"),

    # icml
    "icml2023": ("/Users/ivcylc_lca/Desktop/papers/icml2023.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/icml/icml2023.json"),
    "icml2024": ("/Users/ivcylc_lca/Desktop/papers/icml2024.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/icml/icml2024.json"),
    "icml2025": ("/Users/ivcylc_lca/Desktop/papers/icml2025.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/icml/icml2025.json"),

    # ijcai
    "ijcai2023": ("/Users/ivcylc_lca/Desktop/papers/ijcai2023.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/ijcai/ijcai2023.json"),
    "ijcai2024": ("/Users/ivcylc_lca/Desktop/papers/ijcai2024.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/ijcai/ijcai2024.json"),

    # cvpr
    "cvpr2023": ("/Users/ivcylc_lca/Desktop/papers/cvpr2023.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/cvpr/cvpr2023.json"),
    "cvpr2024": ("/Users/ivcylc_lca/Desktop/papers/cvpr2024.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/cvpr/cvpr2024.json"),
    "cvpr2025": ("/Users/ivcylc_lca/Desktop/papers/cvpr2025.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/cvpr/cvpr2025.json"),

    # iccv
    "iccv2023": ("/Users/ivcylc_lca/Desktop/papers/iccv2023.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/iccv/iccv2023.json"),
    # "iccv2025": ("iccv2025.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/iccv/iccv2025.json"),

    # eccv
    # "eccv2022": ("eccv2022.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/eccv/eccv2022.json"),
    "eccv2024": ("/Users/ivcylc_lca/Desktop/papers/eccv2024.json", "https://raw.githubusercontent.com/papercopilot/paperlists/main/eccv/eccv2024.json"),
}

# 下载 neuripsJSON 并导入数据库
def ensure_nips_data():
    for year, (json_file_name, json_url) in NIPS_DB_PATHS.items():
        json_file = Path(json_file_name)
        if not json_file.exists():
            print(f"🔍 正在下载 {year} JSON...")
            response = requests.get(json_url)
            response.raise_for_status()
            json_file.write_text(response.text, encoding="utf-8")
            print(f"✅ {year} 下载完成。")

        with open(json_file, "r", encoding="utf-8") as f:
            papers = json.load(f)

        db_path = f"/Users/ivcylc_lca/Desktop/papers/papers_{year}.db"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                title TEXT PRIMARY KEY,
                status TEXT,
                pdf_url TEXT,
                abstract TEXT,
                is_read INTEGER DEFAULT 0,
                summary TEXT DEFAULT ''
            )
        ''')
        for paper in papers:
            c.execute('''
                INSERT OR IGNORE INTO papers (title, status, pdf_url, abstract)
                VALUES (?, ?, ?, ?)
            ''', (
                paper.get("title", ""),
                paper.get("status", ""),
                paper.get("pdf", ""),
                paper.get("abstract", "")
            ))
        conn.commit()
        conn.close()

# 初始化数据库

def init_lc_paper_list():
    conn = sqlite3.connect(LC_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS lc_papers (
            title TEXT PRIMARY KEY,
            status TEXT,
            pdf_url TEXT,
            abstract TEXT,
            is_read INTEGER DEFAULT 0,
            summary TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    return conn

# 主 UI 应用
class PaperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("\U0001f4da Paper Viewer")
        self.geometry("1100x750")
        self.db_mode = tk.StringVar(value="LC库")
        self.conn = init_lc_paper_list()
        self.current_title = None
        self.current_pdf_url = None

        self.search_frame = tk.Frame(self)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.random_button = tk.Button(self.search_frame, text="🎲 随机一篇论文", command=self.pick_random_lc_paper)
        self.random_button.pack(side=tk.RIGHT, padx=10)


        tk.Label(self.search_frame, text="🔍 搜索关键词:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", self.perform_search)

        self.search_button = tk.Button(self.search_frame, text="搜索", command=self.perform_search)
        self.search_button.pack(side=tk.LEFT)

        self.show_unread_only = tk.BooleanVar()
        self.unread_toggle = tk.Checkbutton(self.search_frame, text="📖 仅显示未读", variable=self.show_unread_only, command=self.perform_search)
        self.unread_toggle.pack(side=tk.LEFT, padx=10)

        self.source_menu = ttk.Combobox(self.search_frame, textvariable=self.db_mode, values=["LC库", 
                "neurips2023", "neurips2024",
                "aaai2023", "aaai2024", "aaai2025",
                "iclr2023", "iclr2024", "iclr2025",
                "icml2023", "icml2024", "icml2025",
                "ijcai2023", "ijcai2024",
                "cvpr2023", "cvpr2024", "cvpr2025",
                "iccv2023", 
                "eccv2024"], state="readonly")
        self.source_menu.pack(side=tk.LEFT, padx=10)
        self.source_menu.bind("<<ComboboxSelected>>", self.reload_database)

        self.add_lc_button = tk.Button(self.search_frame, text="➕ 手动添加LC论文", command=self.add_lc_paper_popup)
        self.add_lc_button.pack(side=tk.RIGHT, padx=10)

        self.paper_list = tk.Listbox(self, width=90, height=35, font=("Arial", 22), selectbackground="#d0e0ff", activestyle="none", exportselection=False)
        self.paper_list.pack(side=tk.LEFT, padx=30, pady=30, fill=tk.BOTH, expand=False)
        self.paper_list.bind("<<ListboxSelect>>", self.on_select)

        self.detail_frame = tk.Frame(self)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.status_label = tk.Label(self.detail_frame, text="Status:", font=("Arial", 14))
        self.status_label.pack(anchor="w")

        self.pdf_label = tk.Label(self.detail_frame, text="PDF 链接：", font=("Arial", 12))
        self.pdf_label.pack(anchor="w")

        self.pdf_link = tk.Label(self.detail_frame, text="", fg="blue", cursor="hand2", font=("Arial", 12))
        self.pdf_link.pack(anchor="w", pady=(0, 10))
        self.pdf_link.bind("<Button-1>", lambda e: self.open_pdf_url())
        self.pdf_label.bind("<Button-1>", lambda e: self.open_pdf_url())

        self.pdf_hint = tk.Label(self.detail_frame, text="👉 可复制链接并粘贴至 PDF 阅读器打开", font=("Arial", 10), fg="gray")
        self.pdf_hint.pack(anchor="w")

        self.read_var = tk.BooleanVar()
        self.read_check = tk.Checkbutton(self.detail_frame, text="✅ 已读", variable=self.read_var, command=self.toggle_read_status)
        self.read_check.pack(anchor="w", pady=5)

        self.count_label = tk.Label(self.search_frame, text="📄 总论文数: 0", font=("Arial", 11))
        self.count_label.pack(side=tk.LEFT, padx=10)

        tk.Label(self.detail_frame, text="✏️ 总结:", font=("Arial", 14)).pack(anchor="w")
        self.summary_text = tk.Text(self.detail_frame, height=25, width=100, font=("Arial", 13), wrap=tk.WORD)
        self.summary_text.pack(anchor="w", fill=tk.BOTH, expand=True)

        self.star_button = tk.Button(self.detail_frame, text="⭐ 加入LC阅读列表", command=self.add_to_lc_list)
        self.star_button.pack(anchor="e", pady=5)

        self.delete_button = tk.Button(self.detail_frame, text="🗑️ 从LC阅读列表中删除", command=self.delete_from_lc_list)
        self.delete_button.pack(anchor="e", pady=5)

        self.save_button = tk.Button(self.detail_frame, text="📅 保存总结", command=self.save_summary)
        self.save_button.pack(anchor="e", pady=5)

        self.load_titles()
        self.unread_toggle.invoke()

        # self.paper_list.bind("<<ListboxSelect>>", self.on_select)
        # self.paper_list.bind("<Double-Button-1>", self.copy_title_to_clipboard)  # 新增行
        self.paper_list.bind("<Double-Button-1>", self.copy_title_to_clipboard)
        # self.paper_list.bind("<Triple-Button-1>", self.translate_abstract_popup)
        self.paper_list.bind("<Triple-Button-1>", self.show_abstract_popup)

    def show_abstract_popup(self, event):
        # import baidu_translate as fanyi

        idx = self.paper_list.curselection()
        if not idx:
            return
        title = self.paper_list.get(idx[0])
        table = "lc_papers" if self.db_mode.get() == "LC库" else "papers"
        c = self.conn.cursor()
        c.execute(f"SELECT abstract FROM {table} WHERE title=?", (title,))
        row = c.fetchone()
        if not row or not row[0].strip():
            return

        abstract = row[0]
        current_mode = {"is_translated": False}

        popup = tk.Toplevel(self)
        # popup.title("📄 摘要查看")
        popup.title(f"📄 {title}")
        popup.geometry("900x600")

        def toggle_translation():
            if not current_mode["is_translated"]:
                try:
                    translated = fanyi.translate_text(abstract, to=fanyi.Lang.ZH)
                except Exception as e:
                    translated = f"[翻译失败] {e}"
                text_widget.config(state=tk.NORMAL)
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, translated)
                text_widget.config(state=tk.DISABLED)
                current_mode["is_translated"] = True
                title_label.config(text="中文翻译：")
                toggle_button.config(text="显示原文")
            else:
                text_widget.config(state=tk.NORMAL)
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, abstract)
                text_widget.config(state=tk.DISABLED)
                current_mode["is_translated"] = False
                title_label.config(text="英文摘要：")
                toggle_button.config(text="🌐 翻译成中文")

        # ✅ 先放按钮
        toggle_button = tk.Button(popup, text="🌐 翻译成中文", command=toggle_translation)
        toggle_button.pack(anchor="ne", padx=10, pady=10)

        title_label = tk.Label(popup, text="英文摘要：", font=("Arial", 11, "bold"))
        title_label.pack(anchor="w", padx=10, pady=(0, 0))

        text_widget = tk.Text(popup, wrap=tk.WORD, font=("Arial", 20), bg="#f8f8f8")
        text_widget.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=True)
        text_widget.insert(tk.END, abstract)
        text_widget.config(state=tk.DISABLED)


    def pick_random_lc_paper(self):
        if self.db_mode.get() != "LC库":
            messagebox.showinfo("提示", "仅支持在 LC 阅读库中随机抽取")
            return

        c = self.conn.cursor()
        c.execute("SELECT title FROM lc_papers")
        rows = c.fetchall()
        if not rows:
            messagebox.showwarning("空库", "LC 阅读库中没有论文")
            return

        import random
        random_title = random.choice(rows)[0]
        
        # 设置选中项
        titles = [self.paper_list.get(idx) for idx in range(self.paper_list.size())]
        if random_title in titles:
            target_index = titles.index(random_title)
            self.paper_list.selection_clear(0, tk.END)
            self.paper_list.selection_set(target_index)
            self.paper_list.see(target_index)
            self.on_select(None)  # 触发显示详情


    def copy_title_to_clipboard(self, event):
        idx = self.paper_list.curselection()
        if not idx:
            return
        title = self.paper_list.get(idx[0])
        self.clipboard_clear()
        self.clipboard_append(title)
        self.update()  # 确保复制立即生效

    def reload_database(self, event=None):
        mode = self.db_mode.get()
        if mode == "LC库":
            self.conn = init_lc_paper_list()
        # elif "neurips" in mode:
        else:
            year = mode#.split()
            # import pdb; pdb.set_trace()
            ensure_nips_data()  # 确保表存在
            self.conn = sqlite3.connect(f"/Users/ivcylc_lca/Desktop/papers/papers_{year}.db")
        self.load_titles()

    def load_titles(self, filtered_titles=None):
        self.paper_list.delete(0, tk.END)
        table = "lc_papers" if self.db_mode.get() == "LC库" else "papers"
        c = self.conn.cursor()
        if filtered_titles is None:
            c.execute(f"SELECT title FROM {table} ORDER BY title")
            titles = [row[0] for row in c.fetchall()]
        else:
            titles = filtered_titles
        for idx, title in enumerate(titles):
            bg = "#ffffff" if idx % 2 == 0 else "#f0f0f0"
            truncated_title = title# [:100] + "..." if len(title) > 100 else title
            self.paper_list.insert(tk.END, truncated_title)
            self.paper_list.itemconfig(tk.END, {'bg': bg})
        self.count_label.config(text=f"📄 总论文数: {len(titles)}")

    def on_select(self, event):
        idx = self.paper_list.curselection()
        if not idx:
            return
        index = idx[0]
        title = self.paper_list.get(index)
        self.current_title = title
        table = "lc_papers" if self.db_mode.get() == "LC库" else "papers"
        c = self.conn.cursor()
        c.execute(f"SELECT status, is_read, summary, pdf_url FROM {table} WHERE title=?", (title,))
        row = c.fetchone()
        if row:
            status, is_read, summary, pdf_url = row
            self.status_label.config(text=f"Status: {status}")
            self.read_var.set(bool(is_read))
            self.summary_text.delete("1.0", tk.END)
            display_link = pdf_url if pdf_url else title
            self.pdf_link.config(text=display_link, fg="blue" if pdf_url else "gray")
            self.current_pdf_url = pdf_url or title
            if not is_read and not summary:
                self.summary_text.insert(tk.END, f"请根据以下链接生成详细，完整的论文解读。要求充分的关于动机，以往方法，本文方法非常详细地介绍介绍以及简略的测试数据集介绍：{display_link or ''}")
            else:
                self.summary_text.insert(tk.END, summary)
            # self.pdf_link.config(text=pdf_url or "", fg="blue" if pdf_url else "gray")
            # self.current_pdf_url = pdf_url
            # 如果 pdf_url 为空，则 fallback 为 title

    def toggle_read_status(self):
        if not self.current_title:
            return
        table = "lc_papers" if self.db_mode.get() == "LC库" else "papers"
        c = self.conn.cursor()
        c.execute(f"UPDATE {table} SET is_read=? WHERE title=?", (int(self.read_var.get()), self.current_title))
        self.conn.commit()

    def add_to_lc_list(self):
        if not self.current_title or not (self.db_mode.get().startswith("neurips") or self.db_mode.get().startswith("aaai")  or self.db_mode.get().startswith("icml") or self.db_mode.get().startswith("iccv") or self.db_mode.get().startswith("eccv")  or self.db_mode.get().startswith("iclr") or self.db_mode.get().startswith("ijcai") or self.db_mode.get().startswith("cvpr")):
            return

        c = self.conn.cursor()
        c.execute("SELECT title, status, pdf_url, abstract FROM papers WHERE title=?", (self.current_title,))
        row = c.fetchone()
        if row:
            title, status, pdf_url, abstract = row
            conn_lc = init_lc_paper_list()
            c_lc = conn_lc.cursor()
            c_lc.execute(
                "INSERT OR IGNORE INTO lc_papers (title, status, pdf_url, abstract) VALUES (?, ?, ?, ?)",
                (title, status, pdf_url, abstract)
            )
            conn_lc.commit()
            conn_lc.close()
            messagebox.showinfo("已加入", f"⭐ 已将论文加入 LC 阅读列表：{title}")

    def delete_from_lc_list(self):
        if not self.current_title or self.db_mode.get() != "LC库":
            return
        confirm = messagebox.askyesno("确认删除", f"是否从 LC 阅读库中删除：{self.current_title}？")
        if not confirm:
            return
        c = self.conn.cursor()
        c.execute("DELETE FROM lc_papers WHERE title=?", (self.current_title,))
        self.conn.commit()
        self.current_title = None
        self.summary_text.delete("1.0", tk.END)
        self.read_var.set(False)
        self.status_label.config(text="Status:")
        self.load_titles()
        messagebox.showinfo("删除成功", "✅ 已从 LC 阅读库中删除该论文")

    def open_pdf_url(self):
        import webbrowser
        if hasattr(self, 'current_pdf_url') and self.current_pdf_url:
            webbrowser.open(self.current_pdf_url)

    def save_summary(self):
        if not self.current_title:
            return
        summary = self.summary_text.get("1.0", tk.END).strip()
        table = "lc_papers" if self.db_mode.get() == "LC库" else "papers"
        c = self.conn.cursor()
        c.execute(f"UPDATE {table} SET summary=? WHERE title=?", (summary, self.current_title))
        self.conn.commit()
        messagebox.showinfo("保存成功", f"✅ 已保存摘要：{self.current_title}")

    # def perform_search(self, event=None):
    #     keyword = self.search_var.get().strip().lower()
    #     only_unread = self.show_unread_only.get()
    #     table = "lc_papers" if self.db_mode.get() == "LC库" else "papers"
    #     c = self.conn.cursor()
    #     base_query = f"SELECT title FROM {table} WHERE 1=1"
    #     params = []

    #     if keyword:
    #         base_query += " AND (LOWER(title) LIKE ? OR LOWER(summary) LIKE ? OR LOWER(abstract) LIKE ?)"
    #         params.extend([f"%{keyword}%"] * 3)

    #     if only_unread:
    #         base_query += " AND is_read=0"

    #     c.execute(base_query, tuple(params))
    #     matches = [row[0] for row in c.fetchall()]
    #     self.load_titles(matches)

    # def copy_title_to_clipboard(self, event):
    #     idx = self.paper_list.curselection()
    #     if not idx:
    #         return
    #     title = self.paper_list.get(idx[0])
    #     self.clipboard_clear()
    #     self.clipboard_append(title)
    #     self.update()  # 更新剪贴板内容
    #     messagebox.showinfo("已复制", f"📋 已复制论文标题：\n{title}")


    def perform_search(self, event=None):
        keyword = self.search_var.get().strip().lower()
        only_unread = self.show_unread_only.get()
        table = "lc_papers" if self.db_mode.get() == "LC库" else "papers"
        c = self.conn.cursor()
        base_query = f"SELECT title FROM {table} WHERE 1=1"
        params = []

        if keyword:
            # 用 + 分割后去除每个关键词前后的空格
            keywords = [kw.strip() for kw in keyword.split('+') if kw.strip()]
            for kw in keywords:
                base_query += " AND (LOWER(title) LIKE ? OR LOWER(summary) LIKE ? OR LOWER(abstract) LIKE ?)"
                params.extend([f"%{kw}%"] * 3)

        if only_unread:
            base_query += " AND is_read=0"

        c.execute(base_query, tuple(params))
        matches = [row[0] for row in c.fetchall()]
        self.load_titles(matches)


    def add_lc_paper_popup(self):
        popup = tk.Toplevel(self)
        popup.title("➕ 添加 LC 阅读论文")

        tk.Label(popup, text="论文标题:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        title_var = tk.StringVar()
        title_entry = tk.Entry(popup, textvariable=title_var, width=50)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(popup, text="PDF 链接:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        pdf_var = tk.StringVar()
        pdf_entry = tk.Entry(popup, textvariable=pdf_var, width=50)
        pdf_entry.grid(row=1, column=1, padx=10, pady=5)

        def submit():
            title = title_var.get().strip()
            pdf_url = pdf_var.get().strip()
            if title and pdf_url:
                conn = init_lc_paper_list()
                c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO lc_papers (title, status, pdf_url, abstract) VALUES (?, ?, ?, '')",
                          (title, "Manual", pdf_url))
                conn.commit()
                conn.close()
                popup.destroy()
                messagebox.showinfo("已添加", f"⭐ 已添加 LC 论文：{title}")
            else:
                messagebox.showwarning("字段为空", "请填写完整的标题和 PDF 链接")

        submit_btn = tk.Button(popup, text="添加", command=submit)
        submit_btn.grid(row=2, column=1, sticky="e", padx=10, pady=10)

import tkinter as tk
from tkinter import simpledialog, messagebox

import hashlib
PASSWORD_HASH = "f5266e32fc9bfe3bbed922f93a79f5a99355e95b119798c4d3398e1b952bff17"

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def require_password():
    import tkinter as tk
    from tkinter import simpledialog, messagebox

    root = tk.Tk()
    root.withdraw()
    while True:
        password = simpledialog.askstring("🔒 密码验证", "请输入访问密码：", show="*")
        if password is None:
            exit(0)
        elif hash_password(password) == PASSWORD_HASH:
            break
        else:
            messagebox.showerror("密码错误", "密码错误，请重试")
    root.destroy()

if __name__ == "__main__":
    # require_password("lichang0928") 
    # require_password()
    app = PaperApp()
    app.mainloop()
