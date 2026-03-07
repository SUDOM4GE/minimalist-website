import tkinter as tk
from tkinter import ttk, messagebox
import os
import webbrowser
import subprocess
import threading
import concurrent.futures

class Minimalist:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimalist")
        self.root.version = "0.1"
        self.root.geometry("800x550")
        self.root.configure(bg="#000000")  # black

        # ===================== STYLING =====================
        style = ttk.Style()
        style.theme_use("clam")  # modern Look

        # Buttons
        style.configure("Cyber.TButton",
                        font=("Consolas", 12, "bold"),
                        padding=10,
                        background="#000000",
                        foreground="#00ff00",
                        borderwidth=2)
        style.map("Cyber.TButton",
                  background=[('active', '#00ff00')],
                  foreground=[('active', '#0f0f0f')])

        # Labels
        style.configure("Cyber.TLabel",
                        font=("Consolas", 14),
                        background="#000000",
                        foreground="#00ff00")

        # Entry
        style.configure("Cyber.TEntry",
                        font=("Consolas", 12),
                        fieldbackground="#000000",
                        foreground="#00ff00")

        # Scrollbar
        style.configure("Vertical.TScrollbar",
                        background="#000000",
                        troughcolor="#000000",
                        bordercolor="#00ff00",
                        arrowcolor="#00ff00")

        # ===================== TITLE =====================
        self.title_label = ttk.Label(root, text="minimalist .", style="Cyber.TLabel", font=("Consolas", 24, "bold"))
        self.title_label.pack(pady=5)

        # ===================== VERSION =====================
        self.version_label = ttk.Label(root, text=f"v{self.root.version}", style="Cyber.TLabel", font=("Consolas", 12))
        self.version_label.pack(pady=0)

        # ===================== ENTRY =====================
        self.entry = ttk.Entry(root, width=60, style="Cyber.TEntry")
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda e: self.quick_search())  # Enter Key Shortcut

        # ===================== BUTTONS =====================
        self.button_frame = tk.Frame(root, bg="#000000")
        self.button_frame.pack(pady=10)

        self.quick_button = ttk.Button(self.button_frame, text="quick search", style="Cyber.TButton", command=self.quick_search)
        self.quick_button.pack(side=tk.LEFT, padx=15)

        self.deep_button = ttk.Button(self.button_frame, text="Deep Search", style="Cyber.TButton", command=self.deep_search)
        self.deep_button.pack(side=tk.LEFT, padx=15)

        # ===================== RESULT TEXT =====================
        self.text_frame = tk.Frame(root, bg="#0f0f0f")
        self.text_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(self.text_frame,
                                   height=20,
                                   width=90,
                                   font=("Consolas", 11),
                                   bg="#000000",
                                   fg="#00ff00",
                                   insertbackground="#00ff00")
        self.scrollbar = ttk.Scrollbar(self.text_frame, command=self.result_text.yview, style="Vertical.TScrollbar")
        self.result_text.config(yscrollcommand=self.scrollbar.set)

        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ===================== APP ALIASES =====================
        self.aliases = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "opera": "C:\\Program Files\\Opera\\launcher.exe",
            "opera GX": "C:\\Program Files\\Opera GX\\launcher.exe",
            "edge":"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE"
        }

    # ===================== SEARCH METHODS =====================
    def quick_search(self):
        query = self.entry.get().strip().lower()
        if not query:
            messagebox.showwarning("Enter Warning", "Please enter something.")
            return
        if query in self.aliases:
            self.open_app(self.aliases[query])
        else:
            self.search_files(query, max_depth=2)

    def deep_search(self):
        query = self.entry.get().strip().lower()
        if not query:
            messagebox.showwarning("Please Enter Something", "Please enter something.")
            return
        if query in self.aliases:
            self.open_app(self.aliases[query])
        else:
            self.search_files(query, max_depth=5)

    def open_app(self, target):
        try:
            if target.startswith("http"):
                webbrowser.open(target)
                self.result_text.insert(tk.END, f"open {target} in Browser...\n")
            else:
                subprocess.Popen(target)
                self.result_text.insert(tk.END, f"open {target}...\n")
        except Exception as e:
            self.result_text.insert(tk.END, f"didn't work: {e}\n")

    def search_files(self, query, max_depth=None):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"searching for files '{query}'...\n")
        threading.Thread(target=self._perform_search, args=(query, max_depth)).start()

    def _perform_search(self, query, max_depth=None):
        user_home = os.path.expanduser("~")
        search_paths = [user_home, os.path.join(user_home, "Desktop"),
                        os.path.join(user_home, "Documents"), os.path.join(user_home, "Downloads"),
                        "C:\\Program Files"]
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._walk_and_search, path, query, max_depth, 0) for path in search_paths if os.path.exists(path)]
            for future in concurrent.futures.as_completed(futures):
                partial_results = future.result()
                results.extend(partial_results)
                if len(results) >= 20:
                    break
        results = results[:20]
        self.root.after(0, lambda: self._update_results(results))

    def _walk_and_search(self, path, query, max_depth, current_depth):
        results = []
        if max_depth is not None and current_depth > max_depth:
            return results
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if len(results) >= 20:
                        break
                    if entry.is_file() and query in entry.name.lower():
                        results.append(entry.path)
                    elif entry.is_dir():
                        sub_results = self._walk_and_search(entry.path, query, max_depth, current_depth + 1)
                        results.extend(sub_results)
                        if len(results) >= 20:
                            break
        except PermissionError:
            pass
        return results

    def _update_results(self, results):
        if results:
            self.result_text.insert(tk.END, "Found files:\n")
            for res in results:
                self.result_text.insert(tk.END, res + "\n")
        else:
            self.result_text.insert(tk.END, "No files found.\n")

# ===================== no terminal popup =====================
if os.name == "nt":
    import ctypes
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd:
        ctypes.windll.user32.ShowWindow(whnd, 0)  # 0 = SW_HIDE

# ===================== MAIN =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = Minimalist(root)
    root.mainloop()