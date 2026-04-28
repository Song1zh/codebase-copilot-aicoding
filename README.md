# Codebase Copilot

一个基于 AI 的代码仓库分析与修改建议生成工具，用于实习简历展示的 CLI MVP。

---

## Background

Codebase Copilot 是一个 AI 辅助的代码分析工具，旨在帮助开发者理解代码仓库结构、定位问题位置，并生成结构化的修复建议。

**核心价值**：
- 自动化分析代码仓库，提取关键信息
- 根据自然语言描述定位相关代码文件
- 生成可操作的修复计划和补丁建议
- 输出结构化的修复报告

---

## Features

| 功能 | 描述 |
|------|------|
| **仓库扫描** | 扫描 Python 仓库，提取文件、函数、类、导入信息 |
| **代码检索** | 根据 issue 描述检索 top-k 候选文件 |
| **修复计划** | 生成结构化 FixPlan，包含疑似文件、根因假设、修复步骤 |
| **代码读取** | 读取真实代码上下文，为补丁生成提供依据 |
| **补丁建议** | 基于代码上下文生成 PatchSuggestion |
| **测试建议** | 生成针对修复的测试建议 |
| **报告生成** | 输出完整的 Markdown 修复报告 |
| **工作流控制** | 使用 LangGraph 串联 workflow，支持检索结果优化分支 |

---

## Workflow

```
用户输入 Issue
       ↓
    扫描仓库 (scan)
       ↓
    检索相关文件 (retrieve)
       ↓
┌─────┴─────┐
│ 结果过弱? │
└─────┬─────┘
 是 ↓   ↓ 否
重新检索   ↓
       生成修复计划 (plan)
           ↓
       读取代码上下文
           ↓
       生成补丁建议 (suggest)
           ↓
       生成测试建议
           ↓
       生成修复报告 (report)
```

---

## CLI Usage

### 基础命令

```bash
# 扫描仓库
python -m app.cli scan --repo <repo_path>

# 检索相关文件
python -m app.cli retrieve --repo <repo_path> --issue "issue description" --top-k 3

# 生成修复计划
python -m app.cli plan --repo <repo_path> --issue "issue description" --top-k 3

# 生成补丁建议
python -m app.cli suggest --repo <repo_path> --issue "issue description" --top-k 3

# 生成完整报告
python -m app.cli report --repo <repo_path> --issue "issue description" --top-k 3

# 完整工作流（推荐）
python -m app.cli fix --repo <repo_path> --issue "issue description" --top-k 3
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--repo` | 目标仓库路径 | 必填 |
| `--issue` | issue 描述文本 | 必填 |
| `--top-k` | 返回的候选文件数量 | 3 |

---

## Demo Repo

项目包含一个演示仓库 `demo_repo/`，用于测试功能：

```
demo_repo/
├── app.py          # 主应用入口
├── parse.py        # 配置解析模块
├── uploads.py      # 文件上传模块
└── utils.py        # 工具函数模块
```

---

## Sample Issues

```bash
# Issue 1: 空上传路径处理
python -m app.cli fix --repo demo_repo --issue "Empty upload path"

# Issue 2: 配置文件缺失
python -m app.cli fix --repo demo_repo --issue "Missing config file"

# Issue 3: None 输入处理
python -m app.cli fix --repo demo_repo --issue "None input normalization"
```

完整示例见 `demo/sample_issues.md`。

---

## Example Output

```markdown
# Codebase Copilot Fix Report

## 1. Issue
命令行参数解析错误

## 2. Repository Summary
- Repo path: `demo_repo`
- Total Python files: 4
- Total functions: 4

## 3. Candidate Files
| Rank | Path | Score |
|---:|---|---:|
| 1 | `app.py` | 28 |
| 2 | `parse.py` | 22 |

## 4. Fix Plan
### Suspected files
- `app.py`: 包含命令行参数解析逻辑

### Fix steps
1. `app.py` - 检查参数验证逻辑

## 5. Patch Suggestion
- Target file: `app.py`
- Change summary: 添加参数验证

### Before snippet
```python
def main():
    args = parser.parse_args()
```

### After snippet
```python
def main():
    args = parser.parse_args()
    if not args.repo:
        raise ValueError("repo path is required")
```

## 6. Test Suggestions
| Name | Type | Command |
|---|---|---|
| 参数验证测试 | cli | python app.py --repo . |

## 7. Risks
- PatchSuggestion is not automatically applied; manual review is required.
```

---

## Project Boundaries

**本工具仅提供分析和建议，不执行以下操作：**

- ❌ 不自动修改代码文件
- ❌ 不自动执行测试
- ❌ 不提交代码到版本控制系统
- ❌ 不部署应用
- ❌ 不保证修复的正确性

---

## Current Limitations

1. **仅支持 Python 代码**：目前只分析 `.py` 文件
2. **依赖 LLM API**：需要有效的 API Key 才能生成修复计划和补丁建议
3. **网络依赖**：需要联网访问 LLM 服务
4. **检索质量**：基于关键词匹配，复杂问题可能检索不到相关文件
5. **代码理解深度**：对复杂代码结构的理解有限

---

## Getting Started

```bash
# 创建虚拟环境
python -m venv venu
.\venu\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建环境变量文件
cp .env.example .env
# 编辑 .env，填入 API Key

# 运行示例
python -m app.cli fix --repo demo_repo --issue "Empty upload path"
```

---

## Tech Stack

- Python 3.13+
- Pydantic v2 (数据验证)
- LangGraph (工作流编排)
- argparse (命令行解析)
- 阿里云 Qwen API (AI 能力)

---

## Project Structure

```
codebase-copilot/
├── app/
│   └── cli.py              # CLI 入口
├── core/
│   ├── repo_scanner.py     # 仓库扫描
│   ├── code_retriever.py   # 代码检索
│   ├── planner.py          # 修复计划生成
│   ├── code_reader.py      # 代码读取
│   ├── patch_generator.py  # 补丁建议生成
│   ├── test_suggester.py   # 测试建议生成
│   ├── report_generator.py # 报告生成
│   └── llm_client.py       # LLM 客户端
├── workflows/
│   └── fix_workflow.py     # LangGraph 工作流
├── schemas/                # Pydantic 模型
├── prompts/                # LLM 提示词
├── demo/                   # 演示资源
├── demo_repo/              # 演示仓库
└── tests/                  # 测试文件
```
