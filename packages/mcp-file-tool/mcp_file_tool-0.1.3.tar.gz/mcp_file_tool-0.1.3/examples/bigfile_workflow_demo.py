"""
大文件高效处理工作流示例脚本。

该示例演示如何在本地（无需启动 MCP 服务）直接调用
`mcp_file_tool` 包中的核心函数，完成如下步骤：
1) 预检与示例数据准备；
2) 按字节/按行/尾部读取；
3) 流式字面量/正则搜索；
4) 构建倒排索引并进行查询；
5) 安全写入（覆盖、追加、插入）。

运行方式（Mac 示例）：
    python examples/bigfile_workflow_demo.py

注意：脚本默认在 `examples/.demo_data` 目录下生成演示文件，
不会修改仓库中的原始示例数据（如 `mcp_large_test.csv`）。
"""

from __future__ import annotations

import os
from typing import Tuple, List

from mcp_file_tool.chunkio import (
    get_file_info,
    read_bytes,
    read_lines,
    read_last_lines,
    write_overwrite,
    append_chunk,
    insert_chunk,
    build_line_index,
    line_number_at_offset,
)
from mcp_file_tool.search import search_literal, search_regex
from mcp_file_tool.indexer import build_inverted_index, search_index_term


DEMO_DIR = os.path.join(os.path.dirname(__file__), ".demo_data")
DEMO_FILE = os.path.join(DEMO_DIR, "bigfile_demo.txt")


def ensure_demo_file(path: str, target_lines: int = 200_000) -> Tuple[str, int]:
    """
    确保演示用大文件存在；若不存在则生成指定行数的文本文件。

    参数：
    - path: 目标文件路径。
    - target_lines: 目标行数（默认 200k 行）。

    返回：
    - (文件路径, 实际行数)。

    说明：
    - 每行格式为 `row-<序号> some payload ...`，便于搜索与索引演示。
    - 生成过程采用流式写入，避免一次性占用大量内存。
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        info = get_file_info(path)
        # 估算行数：简单按换行计数，避免完整扫描
        lines = 0
        with open(path, "rb") as f:
            while True:
                c = f.read(64 * 1024)
                if not c:
                    break
                lines += c.count(b"\n")
        return path, max(lines, 1)

    with open(path, "w", encoding="utf-8") as f:
        for i in range(1, target_lines + 1):
            f.write(f"row-{i:06d} some payload to index and search\n")
    return path, target_lines


def demo_read(file_path: str) -> None:
    """
    演示按字节、按行与尾部读取，输出关键元信息。

    - 字节读取：读取前 256 字节并打印摘要长度。
    - 行读取：读取第 10,000 行起的 5 行。
    - 尾部读取：读取最后 3 行。
    """
    info = get_file_info(file_path)
    print("[file_info]", info)

    b = read_bytes(file_path, offset=0, length=256)
    print("[read_bytes] bytes_read=", b["bytes_read"], "end_offset=", b["end_offset"])  # 不直接打印内容，避免刷屏

    lines = read_lines(file_path, start_line=10_000, num_lines=5)
    print("[read_lines] start_line=", lines["start_line"], "end_line=", lines["end_line"])  # 仅输出行号范围
    for i, ln in enumerate(lines["lines"], 1):
        print(f"  L{i}:", ln.rstrip())

    tail = read_last_lines(file_path, num_lines=3)
    print("[read_last_lines] start_line=", tail["start_line"], "end_line=", tail["end_line"])  # 仅输出行号范围
    for i, ln in enumerate(tail["lines"], 1):
        print(f"  T{i}:", ln.rstrip())


def demo_search(file_path: str) -> None:
    """
    演示流式字面量与正则搜索，返回偏移/近似行号与上下文片段。

    - 字面量：查询 `row-001000`；
    - 正则：查询 `row-\d{6}` 的某个模式示例。
    """
    lit = search_literal(file_path, query="row-001000", max_results=1, context_chars=64)
    print("[search_literal] count=", lit["count"])  # 打印命中数
    if lit["matches"]:
        m = lit["matches"][0]
        print("  offset=", m["start_offset"], "line~=", m["start_line"])
        print("  snippet=", m["snippet"].replace("\n", " ⏎ ")[:120])

    regex = search_regex(file_path, pattern=r"row-\d{6}", max_results=1, context_chars=64)
    print("[search_regex] count=", regex["count"])  # 打印命中数
    if regex["matches"]:
        m = regex["matches"][0]
        print("  offset=", m["start_offset"], "line~=", m["start_line"])
        print("  snippet=", m["snippet"].replace("\n", " ⏎ ")[:120])


def demo_index_and_query(file_path: str) -> None:
    """
    演示构建倒排索引并进行查询。

    - 首次运行进行全量索引；后续可增量（默认启用，追加有效）。
    - 查询精确词项与前缀匹配，返回偏移与片段。
    """
    res = build_inverted_index(file_path, incremental=True)
    print("[build_inverted_index] mode=", res["mode"], "indexed_bytes=", res["indexed_bytes"])  # 输出索引方式与大小

    q1 = search_index_term(file_path, term="row-001000", limit=1)
    print("[search_index_term] exact count=", q1["count"])  # 精确查询
    if q1["matches"]:
        m = q1["matches"][0]
        print("  term=", m["term"], "offset=", m["offset"], "line=", m["line"])  # 片段略

    q2 = search_index_term(file_path, term="row-00", prefix=True, limit=3)
    print("[search_index_term] prefix count=", q2["count"])  # 前缀查询
    for i, m in enumerate(q2["matches"], 1):
        print(f"  P{i}: term={m['term']} off={m['offset']} line={m['line']}")


def demo_write(file_path: str) -> None:
    """
    演示覆盖、追加与插入写入策略。

    - 覆盖：在偏移 0 处写入 `# header`；
    - 追加：在文件末尾追加一行；
    - 插入：在偏移 128 处插入一段文本。

    说明：
    - 所有写入均使用文件锁保护并发安全；
    - 插入采用临时文件 + 原子替换实现，适合在大文件中安全变更。
    """
    ow = write_overwrite(file_path, offset=0, data="# header\n")
    print("[write_overwrite] bytes=", ow["bytes_written"], "end_offset=", ow["end_offset"])  # 覆盖写入

    ap = append_chunk(file_path, data="appended-line\n")
    print("[append_chunk] bytes=", ap["bytes_written"], "end_offset=", ap["end_offset"])  # 追加写入

    ins = insert_chunk(file_path, offset=128, data="<INSERTED>\n")
    print("[insert_chunk] inserted=", ins["bytes_inserted"], "new_size=", ins["new_size"])  # 插入写入


def main() -> None:
    """
    示例主流程：准备数据并依次执行读取、搜索、索引与写入演示。

    - 生成或复用演示文件；
    - 构建行索引并演示偏移→行号；
    - 依次运行各演示函数；
    - 输出均为简化后的关键元信息，避免在控制台打印过量内容。
    """
    fp, lines = ensure_demo_file(DEMO_FILE)
    print("[prepare] file=", fp, "lines~=", lines)

    # 构建行索引并做一次偏移→行号演示
    idx = build_line_index(fp, step=10_000)
    print("[build_line_index] entries=", idx["entries"], "step=", idx["step"])  # 仅输出统计
    ln = line_number_at_offset(fp, offset=64)
    print("[line_number_at_offset] line~=", ln["line"], "scanned=", ln["scanned_bytes"])  # 偏移→行号估算

    # 读取/搜索/索引/写入
    demo_read(fp)
    demo_search(fp)
    demo_index_and_query(fp)
    demo_write(fp)


if __name__ == "__main__":
    main()