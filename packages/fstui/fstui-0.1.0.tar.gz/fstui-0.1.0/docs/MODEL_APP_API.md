# Model Form API Documentation

## 概述

`model_app.py` 提供了兩個主要的函數來處理 Pydantic 模型的創建和更新：

1. **`create_model()`** - 創建新的模型實例
2. **`update_model()`** - 編輯現有的模型實例

這兩個函數是處理 Pydantic 模型的主要接口，適用於大多數 CRUD 場景。

---

## 快速開始

### 創建新記錄

```python
from pydantic import BaseModel
from model_app import create_model

class User(BaseModel):
    name: str
    email: str
    age: int

# 打開表單讓用戶填寫
new_user = create_model(User)

if new_user:
    print(f"Created: {new_user.name}")
    # 保存到數據庫
    db.save(new_user)
```

### 更新現有記錄

```python
from model_app import update_model

# 從數據庫載入現有用戶
user = db.get_user(user_id)

# 打開編輯表單（預填現有值）
updated_user = update_model(user)

if updated_user:
    print(f"Updated: {updated_user.name}")
    # 保存更改
    db.save(updated_user)
```

---

## API 參考

### `create_model()`

創建新的 Pydantic 模型實例。

```python
def create_model(
    model_class: Type[T],
    title: Optional[str] = None,
    on_success: Optional[Callable[[T], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None
) -> Optional[T]
```

**參數：**
- `model_class`: Pydantic BaseModel 類
- `title`: 自定義表單標題（可選）
- `on_success`: 成功回調函數，接收創建的實例
- `on_cancel`: 取消回調函數

**返回值：**
- 創建的模型實例，如果取消則返回 `None`

**示例：**

```python
# 基本用法
user = create_model(UserModel)

# 自定義標題
user = create_model(UserModel, title="Register New User")

# 使用回調
def save_to_db(user):
    db.save(user)
    print(f"Saved {user.name} to database")

user = create_model(UserModel, on_success=save_to_db)
```

---

### `update_model()`

更新現有的 Pydantic 模型實例。

```python
def update_model(
    model_instance: T,
    title: Optional[str] = None,
    show_original: bool = True,
    on_success: Optional[Callable[[T, T], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None
) -> Optional[T]
```

**參數：**
- `model_instance`: 要編輯的現有模型實例
- `title`: 自定義表單標題（可選）
- `show_original`: 是否顯示原始數據（默認 True）
- `on_success`: 成功回調函數，接收 (原始實例, 更新後實例)
- `on_cancel`: 取消回調函數

**返回值：**
- 更新後的模型實例，如果取消則返回 `None`

**示例：**

```python
# 基本用法
updated = update_model(existing_user)

# 自定義標題，隱藏原始數據
updated = update_model(
    existing_user,
    title="Edit Profile",
    show_original=False
)

# 使用回調處理變更
def handle_update(original, updated):
    print("Changes:")
    if original.email != updated.email:
        print(f"  Email: {original.email} -> {updated.email}")
        send_verification_email(updated.email)
    
    db.save(updated)

updated = update_model(existing_user, on_success=handle_update)
```

---

### `show_changes()`

顯示兩個模型實例之間的差異。

```python
def show_changes(original: BaseModel, updated: BaseModel) -> None
```

**參數：**
- `original`: 原始模型實例
- `updated`: 更新後的模型實例

**示例：**

```python
updated = update_model(user)
if updated:
    show_changes(user, updated)
    # 輸出:
    # 📊 Changes:
    #   email:
    #     - old@example.com
    #     + new@example.com
```

---

## 完整示例

### 用戶管理系統

```python
from pydantic import BaseModel, EmailStr, Field
from model_app import create_model, update_model, show_changes

class User(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    is_active: bool = True

# 創建新用戶
def register_user():
    user = create_model(User, title="User Registration")
    if user:
        save_to_db(user)
        send_welcome_email(user.email)
        return user
    return None

# 更新用戶資料
def edit_user_profile(user_id: int):
    # 從數據庫載入
    user = load_user(user_id)
    
    # 編輯
    updated = update_model(user, title="Edit Profile")
    
    if updated:
        # 檢查關鍵變更
        if user.email != updated.email:
            send_verification_email(updated.email)
        
        # 保存
        save_to_db(updated)
        
        # 顯示變更
        show_changes(user, updated)
        
        return updated
    return None
```

### 任務管理

```python
from datetime import date
from enum import Enum
from model_app import create_model, update_model

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    due_date: date
    completed: bool = False

# 創建任務
def create_task():
    task = create_model(Task, title="Create New Task")
    if task:
        print(f"✅ Created: {task.title}")
        tasks_db.insert(task)
    return task

# 標記為完成
def complete_task(task_id: int):
    task = tasks_db.get(task_id)
    
    def on_complete(original, updated):
        if updated.completed and not original.completed:
            print(f"✅ Task '{updated.title}' marked as complete!")
            notify_team(updated)
    
    updated = update_model(task, on_success=on_complete)
    if updated:
        tasks_db.update(task_id, updated)
    return updated
```

---

## 高級用法

### 自定義 App 類

如果需要更多控制，可以直接使用 `ModelFormApp`：

```python
from model_app import ModelFormApp

class CustomFormApp(ModelFormApp):
    """自定義表單應用，添加額外的邏輯"""
    
    def on_mount(self):
        """應用啟動時的初始化"""
        super().on_mount()
        # 添加自定義邏輯
        self.log("Form opened")
    
    def on_pydantic_form_generator_submitted(self, message):
        """自定義提交處理"""
        # 額外驗證
        if self.validate_custom_rules(message.model_instance):
            super().on_pydantic_form_generator_submitted(message)
        else:
            self.notify("Validation failed", severity="error")

# 使用自定義 app
app = CustomFormApp(UserModel, existing_user)
result = app.run()
```

### 條件性顯示原始數據

```python
# 只在重要更改時顯示原始數據
def edit_sensitive_data(user):
    is_admin = check_admin_permission()
    
    updated = update_model(
        user,
        title="Edit Sensitive Information",
        show_original=is_admin  # 只有管理員看到原始數據
    )
    
    if updated:
        log_audit_trail(user, updated)
        return updated
```

### 連鎖更新

```python
def update_order_with_items(order_id):
    # 更新訂單
    order = db.get_order(order_id)
    updated_order = update_model(order, title="Edit Order")
    
    if updated_order:
        db.save(updated_order)
        
        # 繼續更新訂單項目
        for item_id in updated_order.item_ids:
            item = db.get_item(item_id)
            updated_item = update_model(item, title=f"Edit Item {item.name}")
            if updated_item:
                db.save(updated_item)
```

---

## 最佳實踐

### 1. 使用回調處理副作用

```python
# ✅ 好
def on_save(user):
    db.save(user)
    send_notification(user)
    log_activity(user)

user = create_model(User, on_success=on_save)

# ❌ 不好
user = create_model(User)
if user:
    db.save(user)
    send_notification(user)
    log_activity(user)
```

### 2. 驗證後再保存

```python
def save_user(user):
    # 額外業務邏輯驗證
    if not is_username_available(user.username):
        print("Username already taken")
        return
    
    db.save(user)
    print(f"Saved {user.username}")

create_model(User, on_success=save_user)
```

### 3. 使用 show_changes 來記錄審計日誌

```python
updated = update_model(user)
if updated:
    show_changes(user, updated)  # 用戶可見的變更
    audit_log.record(user, updated)  # 記錄到日誌
```

---

## 常見問題

### Q: 如何處理取消？

```python
user = create_model(User)
if user:
    print("User created")
else:
    print("User cancelled creation")
```

### Q: 如何自定義驗證？

在 Pydantic 模型中使用驗證器：

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    email: str
    
    @field_validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v
```

### Q: 支持哪些字段類型？

- 基本類型：`str`, `int`, `float`, `bool`
- 日期：`date`, `datetime`
- 列表：`list[str]`, `list[int]`, etc.
- 枚舉：`Enum`
- 可選：`Optional[T]`
- Markdown：長文本字段自動使用 TextArea

### Q: 如何處理嵌套模型？

目前不支持嵌套模型的自動表單生成。需要手動處理：

```python
# 分別處理父子模型
parent = update_model(parent_model)
if parent:
    for child_id in parent.children_ids:
        child = update_model(db.get_child(child_id))
```

---

## 參考

- `model_app.py` - 主要 API 實現
- `form_generator.py` - 底層表單生成器
- `edit_demo.py` - 完整示例
- `example_models.py` - 示例模型定義
