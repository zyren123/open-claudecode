import json
system_reminder = """<system-reminder> As you answer the user's questions, you can use the following context: # important-instruction-reminders Do what has been asked; nothing more, nothing less. NEVER create files unless they're absolutely necessary for achieving your goal. ALWAYS prefer editing an existing file to creating a new one. NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
  IMPORTANT: this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task.
</system-reminder>"""

todo_list_reminder="""<system-reminder>This is a reminder that your todo list is currently empty. DO NOT mention this to the user explicitly because they are already aware. If you are working on tasks that would benefit from a todo list please use the TodoWrite tool to create one. If not, please feel free to ignore. Again do not mention this message to the user.</system-reminder>"""
todo_list_changed_reminder="""<system-reminder>
Your todo list has changed. DO NOT mention this explicitly to the user. Here are the latest contents of your todo list:
{todo_list}
Continue on with the tasks at hand if applicable.
</system-reminder>"""

def get_todo_list_changed_reminder(todo_list: list[dict]) -> str:
    return todo_list_changed_reminder.format(todo_list=json.dumps(todo_list,ensure_ascii=False))