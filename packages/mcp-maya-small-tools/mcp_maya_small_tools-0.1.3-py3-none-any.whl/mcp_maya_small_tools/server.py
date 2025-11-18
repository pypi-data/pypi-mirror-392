import pathlib
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

# 定义mcp服务器
mcp = FastMCP("Maya-Small-Tools")


def get_maya_reference(file_path):
    """
    以文本打开ma文件，获取所有reference文件路径列表
    Args:
        file_path: ma文件路径
    Returns:
        引用文件列表
    """
    # 尝试不同的编码方式读取文件
    encodings = ['utf-8', 'latin1', 'cp1252']
    content = None
    ref_path_list = []

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.readlines()
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        return f'[error]处理文件时出现编码错误 {file_path}，请查看日志'

    # 读取文件内容, 获取reference路径
    for line in content:
        line = line.strip()

        if not line or line[-5:-2] not in ('.ma', '.mb'):
            continue

        if '-rfn' in line:
            line = line.split()[-1]

        if '"mayaAscii"' in line:
            line = line.split('"mayaAscii"')[-1].strip()

        if '"mayaBinary"' in line:
            line = line.split('"mayaBinary"')[-1].strip()

        if line.startswith('"') and line.endswith(';'):
            ref_path = line.replace('"', '')
            ref_path = ref_path.replace(';', '')
            ref_path_list.append(ref_path)

    ref_path_list = list(set(ref_path_list))

    return ref_path_list


# 定义一个mcp tool
@mcp.tool()
def list_maya_references(dir_path: str) -> Dict[str, Any]:
    """
    列出目录中所有maya文件(ma格式)，以及其reference列表。
    Args:
        dir_path: 目录
    Returns:
        字典，key为maya文件路径，value为Reference列表
    """
    dir_path = pathlib.Path(dir_path)
    if not dir_path.exists():
        return {}

    result = {}
    for maya_path in dir_path.glob('*.ma'):
        ref_list = get_maya_reference(maya_path)
        result[str(maya_path)] = ref_list

    return result


def main():
    mcp.run(transport='stdio')
