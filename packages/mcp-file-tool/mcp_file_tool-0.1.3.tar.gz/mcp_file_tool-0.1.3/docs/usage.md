# 使用指南

> 说明：本文示例中使用的 `tool_*` 函数名是 Python 包装器，便于在本地直接调用；MCP 服务向客户端导出的工具名为无前缀版本（例如 `read_bytes`、`file_info` 等）。如果你在 MCP 客户端中调用，请使用无前缀的导出名。

## 命令启动
```bash
mcp-file-tool
```

## 上下文与日志（可选）
- 所有工具支持可选参数 `ctx`，用于在调用时携带上下文信息（如 `request_id`、来源标签等）；服务端将把该信息写入结构化日志，便于审计与排障。工具功能不依赖该参数。

```python
from mcp_file_tool.server import tool_read_bytes
ctx = {"request_id": "abc-123", "source": "test"}
print(tool_read_bytes(file_path='sample.txt', offset=0, length=128, ctx=ctx))
```

以 STDIO 传输启动 MCP 服务，适配 Trae/Claude Desktop 等客户端。

## 环境变量
- `MCP_FILE_TOOL_ENCODING`: 默认编码（`utf-8`）
- `MCP_FILE_TOOL_MAX_READ_BYTES`: 单次读取上限（默认 4MiB）
- `MCP_FILE_TOOL_STREAM_BUFFER`: 流式缓冲（默认 64KiB）
- `MCP_FILE_TOOL_LOCK_TIMEOUT`: 写入锁超时（默认 10s）
- `MCP_FILE_TOOL_RUNTIME_DIR`: 运行时根目录（默认 `~/.mft`）
- `MCP_FILE_TOOL_INDEX_DIR`: 索引目录（默认 `~/.mft/.mcp_index`）
- `MCP_FILE_TOOL_LOG_DIR`: 日志目录（默认 `~/.mft/logs`）
- `MCP_FILE_TOOL_LOG_LEVEL`: 日志级别（默认 `INFO`）
- `MCP_FILE_TOOL_MAX_SEARCH_RESULTS`: 搜索返回最大条数（默认 200）
- `MCP_FILE_TOOL_CONTEXT_CHARS`: 搜索上下文字符数（默认 96）

## 倒排索引
- 构建：`build_inverted_index(file_path, incremental?, token_pattern?, lower?)`
- 查询：`search_index_term(file_path, term, prefix?, limit?, context_chars?)`
- 默认存储位置：`~/.mft/.mcp_index/<filename>.invidx.sqlite`
- 增量策略：仅支持末尾追加；中段修改将触发全量重建
- 默认分词：`[\w\-]+`，可自定义

## 示例
```python
from mcp_file_tool.server import (
    tool_file_info,
    tool_read_bytes,
    tool_read_lines,
    tool_write_overwrite,
    tool_append,
    tool_insert,
    tool_build_line_index,
    tool_line_number_at_offset,
    tool_search_literal,
    tool_search_regex,
    tool_build_inverted_index,
    tool_search_index_term,
)

fp = 'sample.txt'

# 基本信息与读取
print(tool_file_info(file_path=fp))
print(tool_read_bytes(file_path=fp, offset=0, length=64)["data"])  
print(tool_read_lines(file_path=fp, start_line=10, num_lines=3)["lines"])  

# 写入与插入
tool_write_overwrite(file_path=fp, offset=0, data="HEADER\n")
tool_append(file_path=fp, data="extra-line\n")
off = len(tool_read_lines(file_path=fp, start_line=1, num_lines=1)["lines"][0])
tool_insert(file_path=fp, offset=off, data="INS\n")

# 行索引与偏移→行号
print(tool_build_line_index(file_path=fp, step=100))
print(tool_line_number_at_offset(file_path=fp, offset=50))

# 搜索
print(tool_search_literal(file_path=fp, query="line-0099", max_results=1))
print(tool_search_regex(file_path=fp, pattern=r"line-0\d{2}0", max_results=1))

# 倒排索引（构建与查询）
tool_build_inverted_index(file_path=fp, incremental=False)
print(tool_search_index_term(file_path=fp, term="line-0100"))
print(tool_search_index_term(file_path=fp, term="line-01", prefix=True, limit=3))
```

## 大文件高效处理（工作流示例）
- 该仓库提供了一个完整演示脚本：`examples/bigfile_workflow_demo.py`，涵盖预检、分片读取、搜索、索引与安全写入。
- 适用场景：在本地快速验证策略与性能，无需先启动 MCP 服务。

### 运行（Mac）
- 准备 Python 环境并安装依赖：`pip install -r requirements.txt`
- 执行脚本：`python examples/bigfile_workflow_demo.py`
- 默认会在 `examples/.demo_data/bigfile_demo.txt` 生成 ~200k 行的示例文件，不会更改仓库原始数据。

### 演示内容
- 读取：按字节（首 256B）、按行（第 10,000 行起 5 行）、尾部（最后 3 行）。
- 搜索：字面量 `row-001000` 与正则 `row-\d{6}`，返回偏移、近似行号与片段。
- 索引：构建倒排索引（支持增量），执行精确与前缀查询。
- 写入：覆盖（偏移 0 写入 header）、追加（末尾追加一行）、插入（偏移 128 处插入）。

### 关键建议（与“优化军规”对齐）
- 单一职责：读字节/读行/尾读/搜索/索引/写入分别提供独立工具与结构化结果。
- 流式处理：所有读取/搜索均采用分块拼接，避免一次性加载超大文件。
- 行索引：为大文件构建行偏移索引，加速随机行访问与偏移→行号推断。
- 错误友好：对不存在文件、超范围偏移、编码异常返回可读错误信息。
- 日志与环境：通过环境变量控制缓冲大小、搜索返回数等，日志写入 `~/.mft/logs`。