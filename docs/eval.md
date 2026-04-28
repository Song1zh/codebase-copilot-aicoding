# Evaluation

评估 Codebase Copilot 的检索和规划能力。

## 评估指标

### 1. 检索准确率 (Retrieval Precision)

评估检索结果是否包含真正相关的文件。

**测试方法**:
- 准备测试 issue 集合
- 运行 retrieve 命令
- 检查返回的 top-k 文件是否真的与 issue 相关

**预期目标**: top-3 准确率 > 80%

### 2. FixPlan 有效性 (FixPlan Validity)

评估生成的修复计划是否合理、可执行。

**测试方法**:
- 输入不同类型的 issue
- 检查 FixPlan 结构完整性
- 验证 fix_steps 是否具体可执行

**评估标准**:
- [ ] suspected_files 非空
- [ ] fix_steps 非空且 order 连续
- [ ] risks 非空
- [ ] 所有 file_path 存在

## 测试用例

### 测试 Issue 集合

详见 `demo/sample_issues.md`

### 预期结果

| Issue | 预期相关文件 | 评估结果 |
|-------|------------|---------|
| 命令行参数解析错误 | app/cli.py | 通过 |
| 代码检索结果排序有问题 | core/code_retriever.py | 通过 |

## 持续集成

每次提交后运行测试套件:
```bash
pytest tests/
```
