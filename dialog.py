import tkinter as tk
from tkinter import simpledialog


class ExcludePathHelpDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(
            master, text="Exclude Paths - Hướng dẫn:", font=("Arial", 10, "bold")
        ).pack(pady=5)
        tk.Label(
            master,
            text="Sử dụng để loại trừ các thư mục/file theo mẫu:",
            anchor="w",
            justify="left",
        ).pack(fill="x")

        tk.Label(master, text="Ví dụ:", fg="blue", anchor="w", justify="left").pack(
            fill="x"
        )
        tk.Label(
            master,
            text="- 'test*': Loại trừ tất cả thư mục/file bắt đầu bằng 'test'",
            anchor="w",
            justify="left",
        ).pack(fill="x")
        tk.Label(
            master,
            text="- '*_test': Loại trừ tất cả thư mục/file kết thúc bằng '_test'",
            anchor="w",
            justify="left",
        ).pack(fill="x")
        tk.Label(
            master,
            text="- 'file.txt path/to/folder': Loại trừ các tệp và thư mục cụ thể",
            anchor="w",
            justify="left",
        ).pack(fill="x")

        return None

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE).pack(
            pady=8
        )
        self.bind("<Return>", self.ok)
        box.pack()


class ExcludeExtensionHelpDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(
            master, text="\nExclude Extensions - Hướng dẫn:", font=("Arial", 10, "bold")
        ).pack(pady=5)
        tk.Label(
            master,
            text="Nhập các phần mở rộng file bạn muốn bỏ qua:",
            anchor="w",
            justify="left",
        ).pack(fill="x")
        tk.Label(master, text="Ví dụ:", fg="blue", anchor="w", justify="left").pack(
            fill="x"
        )
        tk.Label(
            master,
            text="- '.log .tmp .cache': Bỏ qua các file log, tạm thời và cache",
            anchor="w",
            justify="left",
        ).pack(fill="x")

        return None

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE).pack(
            pady=8
        )
        self.bind("<Return>", self.ok)
        box.pack()
