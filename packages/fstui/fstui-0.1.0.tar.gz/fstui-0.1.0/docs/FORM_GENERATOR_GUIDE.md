# 🌟 Form Generator 使用指南

## 快速開始

FSTUI Form Generator 可以從 Pydantic 模型自動生成交互式表單。以下是完整的使用方法：

## 1. 基本用法

## Quick Start

### Creating Models

```python
from fstui import create_model

# Create a new user (empty form)
user = create_model(User)

# Create a new user with default values
user = create_model(
    User, 
    title="Register New User",
    default_values={
        "name": "Alice",
        "age": 25,
        "email": "alice@example.com"
    }
)

if user:
    print(f"Created user: {user.name}")
```

### Editing Models

```python
from fstui import update_model

# Edit existing user
existing_user = User(name="Bob", age=30, email="bob@example.com")
updated_user = update_model(existing_user, title="Edit User Profile")

if updated_user:
    print(f"Updated user: {updated_user.name}")
```

## 2. 支持的字段類型

| 類型 | 界面組件 | 示例 |
|------|----------|------|
| `str` | 文本輸入框 | `title: str` |
| `int` | 數字輸入框 | `age: int` |
| `float` | 數字輸入框 | `price: float` |
| `bool` | 開關按鈕 | `is_active: bool` |
| `Enum` | 下拉選單 | `priority: Priority` |
| `date` | 日期輸入框 | `due_date: date` |
| `list[str]` | 逗號分隔輸入 | `tags: list[str]` |
| `Optional[T]` | 可選字段 | `description: Optional[str]` |

### 長文本支持

字段名包含 `description`、`content`、`notes` 或設置 `json_schema_extra={"format": "markdown"}` 會使用多行文本編輯器：

```python
from pydantic import BaseModel, Field

class BlogPost(BaseModel):
    title: str
    content: str = Field(..., json_schema_extra={"format": "markdown"})
    description: str  # 自動使用 TextArea
```

## 3. 完整示例

```python
from typing import Optional
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field
from fstui import create_model, update_model, show_changes

# 定義枚舉
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# 定義模型
class Task(BaseModel):
    title: str = Field(..., description="任務標題")
    description: Optional[str] = Field(None, description="詳細說明")
    priority: Priority = Field(Priority.MEDIUM, description="優先級")
    due_date: Optional[date] = Field(None, description="截止日期")
    tags: Optional[list[str]] = Field(None, description="標籤（逗號分隔）")
    completed: bool = Field(False, description="是否完成")

# 創建新任務
def create_task():
    task = create_model(Task)
    if task:
        print(f"創建任務: {task.title}")
        return task
    return None

# 編輯任務
def edit_task(task):
    updated = update_model(task)
    if updated:
        show_changes(task, updated)
        return updated
    return None

# 使用示例
if __name__ == "__main__":
    # 創建
    new_task = create_task()
    
    # 編輯
    if new_task:
        edited_task = edit_task(new_task)
```

## 4. 高級功能

### 使用預設值

你可以在創建新模型時提供預設值：

```python
from datetime import date
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority = Priority.MEDIUM
    due_date: Optional[date] = None

# 創建帶預設值的任務
task = create_model(
    Task,
    title="創建新任務", 
    default_values={
        "title": "重要任務",
        "priority": Priority.HIGH,
        "due_date": date(2024, 12, 31)
    }
)
```

### 使用回調

```python
def on_save(instance):
    print(f"保存: {instance}")
    # 保存到數據庫等邏輯

def on_cancel():
    print("用戶取消了操作")

# 帶回調的創建
task = create_model(
    Task,
    title="帶回調的任務",
    on_success=on_save,
    on_cancel=on_cancel
)

# 帶回調的編輯
updated = update_model(
    existing_task,
    title="編輯任務",
    on_success=lambda orig, upd: print("更新成功!")
)
```

### 自定義標題

```python
# 創建時自定義標題
user = create_model(User, title="用戶註冊")

# 編輯時自定義標題
updated = update_model(user, title="編輯個人資料")
```

### 控制原始數據顯示

```python
# 隱藏原始數據（編輯時）
updated = update_model(user, show_original=False)
```

## 5. 實際使用場景

### 用戶管理系統

```python
class User(BaseModel):
    username: str = Field(..., min_length=3)
    email: str
    age: int = Field(..., ge=0, le=150)
    is_active: bool = True

def register_user():
    return create_model(User, title="用戶註冊")

def edit_profile(user):
    return update_model(user, title="編輯個人資料")
```

### 內容管理

```python
class Article(BaseModel):
    title: str
    content: str = Field(..., json_schema_extra={"format": "markdown"})
    tags: Optional[list[str]] = None
    published: bool = False

def create_article():
    return create_model(Article, title="寫新文章")

def edit_article(article):
    return update_model(article, title="編輯文章")
```

### 任務管理

```python
class Task(BaseModel):
    title: str
    priority: Priority
    due_date: Optional[date] = None
    completed: bool = False

def create_task():
    return create_model(Task, title="新建任務")

def complete_task(task):
    task.completed = True
    return update_model(task, title="標記完成")
```

## 6. 快速測試

運行以下命令來測試 Form Generator：

```bash
# 運行演示
uv run python3 form_demo.py

# 或者運行現有示例
uv run python3 examples/form_app.py
uv run python3 examples/edit_demo.py
```

## 7. 鍵盤快捷鍵

在表單中：
- **Tab** / **Shift+Tab**: 在字段間移動
- **Enter**: 提交表單
- **Escape** / **Ctrl+C**: 取消
- **↑↓**: 在下拉選單中選擇

## 8. 驗證

所有 Pydantic 驗證器都會自動應用：

```python
class ValidatedModel(BaseModel):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=150)
    
    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('必須包含@符號')
        return v
```

驗證錯誤會在表單中自動顯示。

## 🎉 就是這麼簡單！

FSTUI Form Generator 讓你可以專注於數據模型的定義，自動處理所有的 UI 細節。無論是創建新記錄還是編輯現有數據，只需要一行代碼！