"""弹窗组件模块"""

import json

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical, Center
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static, Checkbox, Collapsible
import logging
import pyperclip

from ..data_models import ChatSession, SessionManager


class ToolsListModal(ModalScreen):
    """工具列表弹窗（支持选择启用的工具）"""

    class ToolsSaved(Message):
        def __init__(self, selected_tools: list[str]):
            super().__init__()
            self.selected_tools = selected_tools

    def __init__(self, enabled_tools: set[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._enabled_tools = set(enabled_tools or [])
        self._tool_names: list[str] = []
        # 记录每个复选框对应的行容器，便于动态切换选中样式
        self._row_by_checkbox_id: dict[str, Container] = {}

    def compose(self) -> ComposeResult:
        """构建工具列表UI"""
        with Container(id="tools-modal", classes="tools-modal"):
            with Vertical(classes="tools-content"):
                yield Label("可用工具（勾选以启用）", classes="modal-title")
                yield ScrollableContainer(classes="tools-list", id="tools-list")
                with Horizontal(classes="modal-buttons"):
                    yield Button("保存", id="save-button", variant="primary")
                    yield Button("关闭", id="close-button", variant="default")

    def on_mount(self) -> None:
        """弹窗挂载后添加工具列表内容"""
        tools_list = self.query_one("#tools-list", ScrollableContainer)
        
        # 获取可用工具
        from ketacli.sdk.ai.function_call import function_registry
        tools = function_registry.get_openai_tools_format() or []
        # 将已选中的工具排在前面（保持原始顺序，只调整分组）
        enabled_defs = []
        disabled_defs = []
        for tool in tools:
            func_info = tool.get('function', {})
            name = func_info.get('name', '')
            if not name:
                continue
            if name in self._enabled_tools:
                enabled_defs.append(tool)
            else:
                disabled_defs.append(tool)

        ordered_tools = enabled_defs + disabled_defs
        self._tool_names = []
        for tool in ordered_tools:
            func_info = tool.get('function', {})
            name = func_info.get('name', '')
            desc = func_info.get('description') or '(无描述)'
            params = func_info.get('parameters', {})
            if not name:
                continue
            self._tool_names.append(name)
            # 复选框行
            row = Container(classes="tool-item")
            # 先将行容器挂载到滚动容器，再挂载子组件，避免挂载顺序错误
            tools_list.mount(row)
            # 标题行：复选框 + 名称
            header = Horizontal(classes="tool-item-header")
            row.mount(header)
            checkbox = Checkbox(label="", value=(name in self._enabled_tools), compact=True)
            checkbox.id = f"tool-checkbox-{name}"
            # 建立映射，便于在复选框状态改变时更新行样式
            self._row_by_checkbox_id[checkbox.id] = row
            name_label = Static(name, classes="tool-item-title", markup=False)
            header.mount(checkbox)
            header.mount(name_label)
            # 描述固定展示
            desc_widget = Static(
                desc,
                classes="tool-item-desc",
                markup=False
            )
            row.mount(desc_widget)
            # 参数默认收起，放入折叠容器
            params_widget = Static(
                f"[dim]{json.dumps(params, indent=2, ensure_ascii=False)}[/dim]",
                classes="tool-item-params",
                markup=True
            )
            details = Collapsible(
                params_widget,
                title="参数",
                collapsed=True,
                classes="tool-item-details",
            )
            row.mount(details)

            # 初始状态：若已启用则给行容器加选中样式
            try:
                if checkbox.value:
                    row.add_class("tool-item-selected")
            except Exception:
                pass

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """切换复选框时更新工具项的选中样式（绿色边框）"""
        try:
            cb = getattr(event, "checkbox", None) or getattr(event, "sender", None)
            if isinstance(cb, Checkbox):
                row = self._row_by_checkbox_id.get(cb.id)
                if row:
                    if cb.value:
                        row.add_class("tool-item-selected")
                    else:
                        row.remove_class("tool-item-selected")
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "close-button":
            self.dismiss()
        elif event.button.id == "save-button":
            # 收集选中的工具
            selected: list[str] = []
            for name in self._tool_names:
                cb = self.query_one(f"#tool-checkbox-{name}", Checkbox)
                if cb.value:
                    selected.append(name)
            # 发出保存事件
            self.post_message(self.ToolsSaved(selected_tools=selected))
            self.dismiss()

    def on_key(self, event) -> None:
        """支持 ESC 关闭弹窗"""
        if getattr(event, "key", None) == "escape":
            self.dismiss()
            try:
                event.prevent_default()
            except Exception:
                pass


class ContextWindowModal(ModalScreen):
    """上下文查看弹窗
    
    展示当前会话的完整上下文（包含用户、助手消息与工具调用结果）。
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._copy_text = ""

    def compose(self) -> ComposeResult:
        with Container(id="context-modal", classes="context-modal"):
            with Vertical(classes="context-content"):
                yield Label("上下文窗口", classes="modal-title")
                yield ScrollableContainer(classes="context-sections", id="context-content")
                with Horizontal(classes="modal-buttons"):
                    yield Button("复制全部", id="copy-button", variant="primary")
                    yield Button("关闭", id="close-button", variant="default")

    def on_mount(self) -> None:
        content = self.query_one("#context-content", ScrollableContainer)

        prepared_lines: list[str] = []

        # 优先从聊天历史UI组装完整上下文（包含工具调用）
        chat_history = None
        try:
            from .chat_history_widget import ChatHistoryWidget
            chat_history = self.app.query_one("#chat-history", ChatHistoryWidget)
        except Exception:
            chat_history = None

        if chat_history:
            try:
                from .message_widget import MessageWidget, StreamingMessageWidget, ToolCallWidget
            except Exception:
                MessageWidget = StreamingMessageWidget = ToolCallWidget = None

            for child in list(chat_history.children):
                # 用户/助手消息
                if MessageWidget and isinstance(child, MessageWidget):
                    role = getattr(child, "role", "")
                    text = (getattr(child, "content", "") or "").strip()
                    role_label = "用户" if role == "user" else "助手"
                    from textual.containers import Container as TContainer
                    item = TContainer(classes=f"message-container {'user-message' if role == 'user' else 'assistant-message'}")
                    content.mount(item)
                    item.mount(Static(role_label, classes="message-header", markup=False))
                    if role == "assistant":
                        try:
                            from textual.widgets import Markdown
                            item.mount(Markdown(text, classes="message-content"))
                        except Exception:
                            item.mount(Static(text, classes="message-content", markup=False))
                    else:
                        item.mount(Static(text, classes="message-content", markup=False))
                    prepared_lines.append(f"[{role_label}] {text}")
                    continue

                # 流式消息（可能尚未完成）
                if StreamingMessageWidget and isinstance(child, StreamingMessageWidget):
                    role = getattr(child, "role", "")
                    role_label = "用户" if role == "user" else "助手"
                    try:
                        text = child.get_final_content()
                    except Exception:
                        text = ""
                    from textual.containers import Container as TContainer
                    item = TContainer(classes=f"message-container {'user-message' if role == 'user' else 'assistant-message'}")
                    content.mount(item)
                    item.mount(Static(role_label, classes="message-header", markup=False))
                    if role == "assistant":
                        try:
                            from textual.widgets import Markdown
                            item.mount(Markdown(text, classes="message-content"))
                        except Exception:
                            item.mount(Static(text, classes="message-content", markup=False))
                    else:
                        item.mount(Static(text, classes="message-content", markup=False))
                    prepared_lines.append(f"[{role_label}] {text}")
                    continue

                # 工具调用
                if ToolCallWidget and isinstance(child, ToolCallWidget):
                    name = getattr(child, "tool_name", "")
                    args = getattr(child, "arguments", "")
                    result = getattr(child, "result", None)
                    result_obj = getattr(child, "result_obj", None)
                    success = getattr(child, "success", True)
                    status = "✓" if success else "✗"
                    from textual.containers import Container as TContainer
                    from textual.widget import Widget as _TWidget
                    # 以“助手消息”样式展示工具调用，保持与普通消息一致
                    wrapper = TContainer(classes="message-container assistant-message")
                    content.mount(wrapper)
                    # 头部沿用助手标签
                    wrapper.mount(Static("助手", classes="message-header", markup=False))
                    try:
                        args_text = json.dumps(args, ensure_ascii=False) if isinstance(args, (dict, list)) else str(args)
                    except Exception:
                        args_text = str(args)
                    # 正文包含工具名与状态、参数与结果
                    wrapper.mount(Static(f"🔧 调用工具: {name} {status}", classes="message-content", markup=False))
                    wrapper.mount(Static(f"参数: {args_text}", classes="message-content", markup=False))
                    if isinstance(result_obj, _TWidget) or isinstance(result, _TWidget):
                        wrapper.mount(Static("结果: 可视化组件（已在对话中显示）", classes="message-content", markup=False))
                        prepared_lines.append(f"[助手] 🔧 {name} {status} | 参数: {args_text} | 结果: 可视化组件")
                    elif result is not None:
                        try:
                            result_text = json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)
                        except Exception:
                            result_text = str(result)
                        wrapper.mount(Static(f"结果: {result_text}", classes="message-content", markup=False))
                        prepared_lines.append(f"[助手] 🔧 {name} {status} | 参数: {args_text} | 结果: {result_text}")
                    else:
                        wrapper.mount(Static("结果: (无)", classes="message-content", markup=False))
                        prepared_lines.append(f"[助手] 🔧 {name} {status} | 参数: {args_text} | 结果: (无)")

            if not prepared_lines:
                content.mount(Static("暂无对话内容", classes="empty-message", markup=False))
                self._copy_text = ""
                return

            self._copy_text = "\n".join(prepared_lines)
            return

        # 回退：使用内存中的会话记录（可能不包含工具调用）
        try:
            raw_messages = list(self.app.conversation_history or [])
        except Exception:
            raw_messages = []
        conv_messages = [m for m in raw_messages if m.get("role") in ("user", "assistant", "tool")]
        if not conv_messages:
            content.mount(Static("暂无对话内容", classes="empty-message", markup=False))
            self._copy_text = ""
            return
        for msg in conv_messages:
            role = msg.get("role")
            text = (msg.get("content", "") or "").strip()
            role_label = "用户" if role == "user" else ("助手" if role == "assistant" else "工具")
            from textual.containers import Container as TContainer
            item = TContainer(classes=f"message-container {'user-message' if role == 'user' else 'assistant-message'}")
            content.mount(item)
            item.mount(Static(role_label, classes="message-header", markup=False))
            item.mount(Static(text, classes="message-content", markup=False))
            prepared_lines.append(f"[{role_label}] {text}")
        self._copy_text = "\n".join(prepared_lines)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-button":
            self.dismiss()
        elif event.button.id == "copy-button":
            try:
                if not self._copy_text:
                    self.app.notify("暂无可复制的对话内容", severity="warning")
                    return
                pyperclip.copy(self._copy_text)
                self.app.notify("已复制全部对话内容到剪贴板", severity="success")
            except Exception as e:
                try:
                    self.app.notify(f"复制失败: {str(e)}", severity="error")
                except Exception:
                    pass


class SessionHistoryModal(ModalScreen):
    """历史会话列表弹窗"""
    
    class SessionSelected(Message):
        """会话选择事件"""
        def __init__(self, session: ChatSession):
            super().__init__()
            self.session = session
    
    def __init__(self, session_manager: SessionManager, **kwargs):
        super().__init__(**kwargs)
        self.session_manager = session_manager
        self.sessions = []
    
    def compose(self) -> ComposeResult:
        """构建历史会话列表UI"""
        with Container(id="session-history-modal", classes="session-history-modal"):
            with Vertical(classes="session-history-content"):
                yield Label("历史会话", classes="modal-title")
                yield ScrollableContainer(classes="session-list", id="session-list")
                with Horizontal(classes="modal-buttons"):
                    yield Button("关闭", id="close-button", variant="default")
    
    def on_mount(self) -> None:
        """弹窗挂载后加载历史会话"""
        self._load_sessions()
        # 设置初始焦点到第一个会话项
        self.call_after_refresh(self._focus_first_session)
    
    def _focus_first_session(self):
        """将焦点设置到第一个会话项"""
        session_list = self.query_one("#session-list", ScrollableContainer)
        session_widgets = session_list.query(SessionItemWidget)
        if session_widgets:
            first_widget = session_widgets.first()
            first_widget.focus()
    
    def on_focus(self, event) -> None:
        """监听焦点变化"""
        pass
    
    def on_key(self, event) -> None:
        """处理键盘事件"""
        if event.key == "up":
            self._navigate_sessions(-1)
            event.prevent_default()
        elif event.key == "down":
            self._navigate_sessions(1)
            event.prevent_default()
        elif event.key == "enter":
            self._select_focused_session()
            event.prevent_default()
        elif event.key == "delete" or event.key == "d":
            self._delete_focused_session()
            event.prevent_default()
        elif event.key == "escape":
            self.dismiss()
            event.prevent_default()
    
    def _navigate_sessions(self, direction: int):
        """在会话之间导航"""
        session_list = self.query_one("#session-list", ScrollableContainer)
        session_widgets = list(session_list.query(SessionItemWidget))
        
        if not session_widgets:
            return
        
        # 找到当前焦点的会话
        focused_widget = self.focused
        if not isinstance(focused_widget, SessionItemWidget):
            # 如果没有焦点在会话项上，设置到第一个
            session_widgets[0].focus()
            return
        
        # 找到当前焦点会话的索引
        try:
            current_index = session_widgets.index(focused_widget)
        except ValueError:
            session_widgets[0].focus()
            return
        
        # 计算新的索引
        new_index = current_index + direction
        if 0 <= new_index < len(session_widgets):
            session_widgets[new_index].focus()
    
    def _select_focused_session(self):
        """选择当前焦点的会话"""
        focused_widget = self.focused
        if isinstance(focused_widget, SessionItemWidget):
            # 触发会话选择
            self.post_message(self.SessionSelected(focused_widget.session))
            self.dismiss()

    def on_key(self, event) -> None:
        """处理键盘事件"""
        if event.key == "up":
            self._navigate_sessions(-1)
            event.prevent_default()
        elif event.key == "down":
            self._navigate_sessions(1)
            event.prevent_default()
        elif event.key == "enter":
            self._select_focused_session()
            event.prevent_default()
        elif event.key == "delete" or event.key == "d":
            self._delete_focused_session()
            event.prevent_default()
        elif event.key == "escape":
            self.dismiss()
            event.prevent_default()

    def _load_sessions(self):
        """加载历史会话列表"""
        session_list = self.query_one("#session-list", ScrollableContainer)
        
        # 清空现有内容
        for child in list(session_list.children):
            child.remove()
        
        # 获取历史会话
        self.sessions = self.session_manager.list_sessions()
        
        if not self.sessions:
            empty_widget = Static(
                "[dim]暂无历史会话[/dim]",
                classes="empty-message"
            )
            session_list.mount(empty_widget)
            return
        
        # 显示会话列表
        for session in self.sessions:
            session_widget = SessionItemWidget(session)
            session_list.mount(session_widget)

    def _navigate_sessions(self, direction: int):
        """在会话列表中导航"""
        session_list = self.query_one("#session-list", ScrollableContainer)
        items = [w for w in session_list.children if isinstance(w, SessionItemWidget)]
        if not items:
            return
        focused = None
        for idx, item in enumerate(items):
            if item.has_class("focused"):
                focused = idx
                break
        if focused is None:
            items[0].focus()
            items[0].add_class("focused")
            return
        new_idx = max(0, min(len(items) - 1, focused + direction))
        if new_idx != focused:
            items[focused].remove_class("focused")
            items[new_idx].focus()
            items[new_idx].add_class("focused")

    def _select_focused_session(self):
        """选择当前焦点的会话"""
        focused_widget = self.focused
        if isinstance(focused_widget, SessionItemWidget):
            # 触发会话选择
            self.post_message(self.SessionSelected(focused_widget.session))
            self.dismiss()

    def _delete_focused_session(self):
        """删除当前焦点的会话"""
        focused_widget = self.focused
        if isinstance(focused_widget, SessionItemWidget):
            try:
                self.session_manager.delete_session(focused_widget.session.id)
                focused_widget.remove()
            except Exception as e:
                try:
                    self.app.notify(f"删除失败: {str(e)}", severity="error")
                except Exception:
                    pass

    def on_session_item_widget_session_clicked(self, message) -> None:
        """处理会话项点击事件"""
        self.post_message(self.SessionSelected(message.session))
        self.dismiss()
    

    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "close-button":
            self.dismiss()
    

    
    def _delete_focused_session(self):
        """删除当前焦点的会话"""
        session_list = self.query_one("#session-list", ScrollableContainer)
        target_widget = None
        
        # 检查当前焦点
        focused_widget = self.focused
        if isinstance(focused_widget, SessionItemWidget):
            target_widget = focused_widget
        else:
            # 查找有焦点样式的会话项
            for widget in session_list.query(SessionItemWidget):
                if widget.has_class("focused"):
                    target_widget = widget
                    break
        
        if not target_widget:
            self.notify("请先选择要删除的会话", severity="warning")
            return
        
        session = target_widget.session
        if self.session_manager.delete_session(session.session_id):
            self.notify(f"已删除会话: {session.title}", severity="success")
            self._load_sessions()  # 重新加载列表
            # 重新设置焦点到第一个会话
            self.call_after_refresh(self._focus_first_session)
        else:
            self.notify("删除失败", severity="error")


class SessionItemWidget(Static):
    """会话项组件"""
    
    # 允许接收焦点
    can_focus = True
    
    class SessionClicked(Message):
        """会话点击事件"""
        def __init__(self, session: ChatSession):
            super().__init__()
            self.session = session
    
    def __init__(self, session: ChatSession, **kwargs):
        super().__init__(**kwargs)
        self.session = session
        self.last_click_time = 0

    def compose(self) -> ComposeResult:
        """构建会话项UI"""
        title = self.session.get_display_title()
        created_time = self.session.created_at
        message_count = len(self.session.messages)
        
        content = f"[bold]{title}[/bold]\n"
        content += f"[dim]创建时间: {created_time}[/dim]\n"
        content += f"[dim]消息数: {message_count}[/dim]"
        
        yield Static(content, classes="session-item-content", id="content")
    
    def on_click(self, event) -> None:
        """处理点击事件 - 支持双击检测"""
        import time
        current_time = time.time()
        
        # 双击检测：如果两次点击间隔小于0.5秒，认为是双击
        if current_time - self.last_click_time < 0.5:
            # 双击 - 加载会话
            self.post_message(self.SessionClicked(self.session))
        
        self.last_click_time = current_time

    def on_key(self, event) -> None:
        """处理键盘事件"""
        if event.key == "enter":
            # Enter键加载会话
            self.post_message(self.SessionClicked(self.session))
            # 阻止事件冒泡到父级，以避免父Modal同时处理Enter导致重复触发
            event.prevent_default()
            try:
                event.stop()
            except Exception:
                # 某些环境下event可能不支持stop，忽略即可
                pass
    

    
    def on_focus(self) -> None:
        """获得焦点时的处理"""
        self.add_class("focused")
    
    def on_blur(self) -> None:
        """失去焦点时的处理"""
        self.remove_class("focused")


class SPLFixDialog(ModalScreen):
    class SPLFixSubmitted(Message):
        def __init__(self, new_spl: str):
            super().__init__()
            self.new_spl = new_spl

    def __init__(self, original_spl: str = "", error_summary: str = "", **kwargs):
        super().__init__(**kwargs)
        self._original_spl = original_spl or ""
        self._error_summary = error_summary or ""
        self._input_id = "spl-fix-input"

    def compose(self) -> ComposeResult:
        with Center():
            with Container(id="spl-fix-modal", classes="spl-fix-modal"):
                with Vertical(classes="spl-fix-content"):
                    yield Label("修复SPL并重试", classes="modal-title")
                    if self._error_summary:
                        yield Static(self._error_summary, classes="error-summary", markup=False)
                    from textual.widgets import TextArea
                    ta = TextArea()
                    ta.id = self._input_id
                    try:
                        ta.value = self._original_spl
                    except Exception:
                        pass
                    try:
                        ta.text = self._original_spl
                    except Exception:
                        pass
                    yield ta
                    with Horizontal(classes="modal-buttons"):
                        yield Button("修复并重试", id="submit-button", variant="primary")
                        yield Button("取消", id="cancel-button", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-button":
            self.dismiss()
        elif event.button.id == "submit-button":
            try:
                from textual.widgets import TextArea
                ta = self.query_one(f"#{self._input_id}", TextArea)
                txt = (getattr(ta, "value", "") or "").strip()
            except Exception:
                txt = ""
            if txt:
                self.post_message(self.SPLFixSubmitted(new_spl=txt))
            self.dismiss()

    def on_key(self, event) -> None:
        if getattr(event, "key", None) == "escape":
            self.dismiss()
            try:
                event.prevent_default()
            except Exception:
                pass

    def on_mount(self) -> None:
        try:
            modal = self.query_one("#spl-fix-modal")
            modal.styles.width = 100
            modal.styles.max_height = 30
            modal.styles.margin = (2, 2)
            from textual.widgets import TextArea
            ta = self.query_one(f"#{self._input_id}", TextArea)
            ta.styles.min_height = 10
            try:
                ta.text = str(self._original_spl or "")
            except Exception:
                pass
        except Exception:
            pass

class ToolArgsEditDialog(ModalScreen):
    class ToolArgsSubmitted(Message):
        def __init__(self, tool_name: str, new_args_text: str):
            super().__init__()
            self.tool_name = tool_name
            self.new_args_text = new_args_text

    def __init__(self, tool_name: str, original_args: object = None, error_summary: str = "", **kwargs):
        super().__init__(**kwargs)
        self._tool_name = tool_name
        self._original_args = original_args
        self._error_summary = error_summary or ""
        self._input_id = "tool-args-input"

    def compose(self) -> ComposeResult:
        with Center():
            with Container(id="tool-args-modal", classes="tool-args-modal"):
                with Vertical(classes="tool-args-content"):
                    yield Label("编辑工具参数并重试", classes="modal-title")
                    if self._error_summary:
                        yield Static(self._error_summary, classes="error-summary", markup=False)
                    from textual.widgets import TextArea
                    import json as _json
                    ta = TextArea()
                    ta.id = self._input_id
                    try:
                        if isinstance(self._original_args, dict):
                            ta.value = _json.dumps(self._original_args, ensure_ascii=False, indent=2)
                        else:
                            ta.value = str(self._original_args or "")
                    except Exception:
                        try:
                            ta.text = str(self._original_args or "")
                        except Exception:
                            pass
                    yield ta
                    with Horizontal(classes="modal-buttons"):
                        yield Button("重试", id="submit-button", variant="primary")
                        yield Button("取消", id="cancel-button", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-button":
            self.dismiss()
        elif event.button.id == "submit-button":
            try:
                from textual.widgets import TextArea
                ta = self.query_one(f"#{self._input_id}", TextArea)
                txt = ""
                try:
                    txt = getattr(ta, "text")
                except Exception:
                    pass
                if not txt:
                    try:
                        txt = getattr(ta, "value")
                    except Exception:
                        pass
                if not txt:
                    try:
                        doc = getattr(ta, "document", None)
                        txt = getattr(doc, "text", "") if doc else ""
                    except Exception:
                        txt = ""
                txt = (txt or "").strip()
            except Exception:
                txt = ""
            if txt:
                import json as _json
                try:
                    obj = _json.loads(txt)
                    if not isinstance(obj, dict):
                        try:
                            self.app.notify("参数需要为JSON对象，如 {\"key\": \"value\"}", severity="warning")
                        except Exception:
                            pass
                        return
                    txt = _json.dumps(obj, ensure_ascii=False)
                    try:
                        prev = txt if len(txt) <= 200 else (txt[:200] + "...")
                        self.app.notify(f"参数已解析：{prev}", severity="success")
                    except Exception:
                        pass
                except Exception:
                    try:
                        self.app.notify("参数不是合法的JSON对象，请检查格式", severity="error")
                    except Exception:
                        pass
                    return
                self.post_message(self.ToolArgsSubmitted(tool_name=self._tool_name, new_args_text=txt))
            self.dismiss()

    def on_key(self, event) -> None:
        if getattr(event, "key", None) == "escape":
            self.dismiss()
            try:
                event.prevent_default()
            except Exception:
                pass

    def on_mount(self) -> None:
        try:
            modal = self.query_one("#tool-args-modal")
            modal.styles.width = 100
            modal.styles.max_height = 30
            modal.styles.margin = (2, 2)
            from textual.widgets import TextArea
            ta = self.query_one(f"#{self._input_id}", TextArea)
            ta.styles.min_height = 12
            import json as _json
            try:
                if isinstance(self._original_args, dict):
                    prefill = _json.dumps(self._original_args, ensure_ascii=False, indent=2)
                else:
                    prefill = str(self._original_args or "")
                ta.text = prefill
            except Exception:
                pass
        except Exception:
            pass
