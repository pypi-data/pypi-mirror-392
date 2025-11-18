# Form Generator Bug Fixes

## 修復的問題

### 1. ✅ InvalidSelectValueError: Illegal select value 'MEDIUM'
**問題**: Enum Select 組件的 options 格式錯誤
**原因**: Textual Select 的 options 格式是 `(prompt, value)`，而不是 `(value, prompt)`
**修復**: 將 options 改為 `[(member.name, member.value) for member in field_type]`

### 2. ✅ PydanticUndefined 顯示為 "PydanticUndefi1ned" 字符串
**問題**: 當字段沒有默認值時，`PydanticUndefined` 被轉換為字符串顯示
**原因**: 沒有正確檢查 `PydanticUndefined`
**修復**: 在所有輸入類型中添加檢查：
```python
from pydantic_core import PydanticUndefined
if default_value is None or default_value is PydanticUndefined:
    value = ""  # 或適當的空值
```

### 3. ✅ PydanticUndefined 在 number field 無法編輯
**問題**: Integer/Float 輸入框被設置為 "PydanticUndefined" 字符串，無法編輯
**原因**: 同上，沒有檢查 `PydanticUndefined`
**修復**: 使用空字符串 `""` 作為數字字段的初始值

### 4. ✅ List 字段輸入任何內容都報錯 "Input should be a valid list"
**問題**: `Optional[list[str]]` 類型的字段無法正確解析用戶輸入
**原因**: 在 `_get_field_value` 中，解包 `Optional` 後沒有重新獲取 `origin`，導致無法識別內部的 `list` 類型
**修復**: 
```python
# 解包 Optional 後重新獲取 origin
actual_type = field_type
if origin is type(None) or ...:
    actual_type = args[0] if args[0] is not type(None) else ...

# 重新評估 origin
actual_origin = get_origin(actual_type)

# 使用 actual_origin 判斷
elif actual_origin is list:
    return [item.strip() for item in value.split(",") if item.strip()]
```

## 修復後的行為

- **Enum Select**: 正確顯示選項並預選默認值
- **必填字段**: 空白輸入框，可以正常輸入
- **選填字段**: 空白輸入框，可以正常輸入
- **有默認值的字段**: 顯示默認值
- **數字字段**: 可以正常編輯（不會顯示 "PydanticUndefined"）
- **List 字段**: 可以輸入逗號分隔的值（例如：`a, b, c`），自動解析為列表

## 測試

```bash
# 測試所有示例表單
uv run main.py form --example personal
uv run main.py form --example task      # 包含 tags (list) 字段
uv run main.py form --example product
uv run main.py form --example user
```

### List 字段測試
在 `task` 示例中，`tags` 字段接受以下格式：
- `a, b, c` → `['a', 'b', 'c']`
- `a,b,c` → `['a', 'b', 'c']`
- `tag1, tag2` → `['tag1', 'tag2']`
- 留空 → `None` (對於 Optional 字段)

所有表單應該能正常顯示和編輯！
