# Sample Issues

用于测试 Codebase Copilot 的示例 issue。

## Issue 1: Empty upload path

**类型**: Bug

**预期相关文件**:
- demo_repo/uploads.py

**描述**:
当上传路径为空字符串时，upload_file 函数没有进行验证，导致文件被上传到错误位置。

---

## Issue 2: Missing config file

**类型**: Bug

**预期相关文件**:
- demo_repo/parse.py

**描述**:
当配置文件不存在时，parse_config 函数返回 None 而不是抛出明确的错误信息。

---

## Issue 3: None input normalization

**类型**: Bug

**预期相关文件**:
- demo_repo/utils.py

**描述**:
normalize_text 函数没有处理 None 输入，传入 None 时会导致 AttributeError。
