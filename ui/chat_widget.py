"""
ChatWidget - Component chat box
"""
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class ChatWidget(tk.Frame):
    """
    UI component chat box đơn giản.

    Tính năng:
    - Hiển thị tin nhắn với auto-scroll
    - Input box với nút Send
    - Hỗ trợ Enter để gửi
    - Thread-safe với Tkinter
    """

    def __init__(self, master, on_send=None, max_lines=200, **kwargs):
        """
        Args:
            master: Widget cha
            on_send: Callback khi gửi tin nhắn (nhận text làm tham số)
            max_lines: Số dòng tối đa hiển thị (tự động xóa dòng cũ)
        """
        super().__init__(master, **kwargs)
        self.on_send = on_send
        self.max_lines = max_lines

        self._create_widgets()

    def _create_widgets(self):
        """Tạo các widget"""
        # Message display (read-only)
        self.messages = ScrolledText(
            self,
            wrap='word',
            state='disabled',
            height=8,
            font=('Arial', 9),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        self.messages.pack(fill='both', expand=True, padx=4, pady=(4, 2))

        # Input area
        input_frame = tk.Frame(self, bg='#34495E')
        input_frame.pack(fill='x', padx=4, pady=(0, 4))

        self.entry = tk.Entry(
            input_frame,
            font=('Arial', 9),
            bg='#FFF'
        )
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 4))
        self.entry.bind('<Return>', self._on_return)

        self.send_btn = tk.Button(
            input_frame,
            text='Gửi',
            command=self._on_send_clicked,
            bg='#3498DB',
            fg='white',
            font=('Arial', 9, 'bold'),
            cursor='hand2'
        )
        self.send_btn.pack(side='right')

    def set_on_send(self, callback):
        """Đặt callback khi gửi tin nhắn"""
        self.on_send = callback

    def _on_return(self, event):
        """Xử lý phím Enter"""
        self._on_send_clicked()
        return 'break'

    def _on_send_clicked(self):
        """Xử lý khi click nút Send"""
        text = self.entry.get().strip()
        if not text:
            return

        # Hiển thị tin nhắn của mình
        self.add_message('Bạn', text)

        # Xóa input
        self.entry.delete(0, 'end')

        # Gọi callback để gửi qua network
        if callable(self.on_send):
            try:
                self.on_send(text)
            except Exception as e:
                print(f"Error sending message: {e}")

    def add_message(self, sender, message):
        """
        Thêm tin nhắn vào display.
        Thread-safe: Có thể gọi từ thread khác bằng cách dùng root.after(0, ...)

        Args:
            sender: Tên người gửi
            message: Nội dung tin nhắn
        """
        # Schedule update trong main thread
        self.after(0, self._append_message, sender, message)

    def _append_message(self, sender, message):
        """Append tin nhắn vào text widget (phải gọi từ main thread)"""
        self.messages.configure(state='normal')

        # Format tin nhắn
        formatted = f"{sender}: {message}\n"
        self.messages.insert('end', formatted)
        self.messages.see('end')  # Auto-scroll to bottom

        # Trim old lines nếu quá nhiều
        try:
            total_lines = int(self.messages.index('end-1c').split('.')[0])
            if total_lines > self.max_lines:
                to_remove = total_lines - self.max_lines
                self.messages.delete('1.0', f'{to_remove + 1}.0')
        except Exception:
            pass

        self.messages.configure(state='disabled')

    def clear(self):
        """Xóa tất cả tin nhắn"""
        self.messages.configure(state='normal')
        self.messages.delete('1.0', 'end')
        self.messages.configure(state='disabled')

