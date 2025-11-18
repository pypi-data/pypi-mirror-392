#!/usr/bin/env python3
"""Form Generator Demo"""

from typing import Optional
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field
from fstui import create_model, update_model, show_changes
from rich import print, print_json


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    title: str = Field(..., description="任務標題")
    description: Optional[str] = Field(None, description="詳細說明")
    priority: Priority = Field(Priority.MEDIUM, description="優先級")
    due_date: Optional[date] = Field(None, description="截止日期")
    tags: Optional[list[str]] = Field(None, description="標籤")
    completed: bool = Field(False, description="是否完成")


def main():
    print("🌟 FSTUI Form Generator Demo")
    print("=" * 40)
    print("1. 創建新任務")
    print("2. 編輯任務")
    choice = input("選擇 (1-2): ")

    if choice == "1":
        print("\n📝 創建新任務...")
        task = create_model(Task)
        if task:
            print(f"✅ 創建成功: {task.title}")
            print_json(task.model_dump_json(indent=2))
    elif choice == "2":
        print("\n✏️ 編輯任務...")
        existing = Task(title="示例任務", priority=Priority.HIGH, tags=["demo", "test"])
        print("原始數據:")
        print_json(existing.model_dump_json(indent=2))

        updated = update_model(existing)
        if updated:
            print("\n✅ 更新成功!")
            show_changes(existing, updated)


if __name__ == "__main__":
    main()
