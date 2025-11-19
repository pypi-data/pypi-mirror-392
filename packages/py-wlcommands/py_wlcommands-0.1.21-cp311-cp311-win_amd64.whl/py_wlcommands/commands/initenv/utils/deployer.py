"""
Deployment functionality for init command.
"""

import ctypes
import os
import platform
import shutil

try:
    from packaging.version import parse as parse_version
except ImportError:
    # 如果没有安装 packaging 库，则回退到简单的字符串比较
    def parse_version(version):
        return version


# 白名单列表：只有这些文件或文件夹会被部署
DEPLOY_WHITELIST = [
    ".uv",
    # '.cursor',
    ".lingma",
    "tools",
    "Makefile",
    ".python-version",
    "project_vendors",
]


def create_symlink(source: str, target: str) -> bool:
    """
    创建从源到目标的软链接，处理平台差异
    """
    source = os.path.abspath(source)
    target = os.path.abspath(target)

    # 如果目标文件已存在，先删除
    if os.path.exists(target):
        try:
            if os.path.islink(target):
                os.unlink(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            elif os.path.isfile(target):
                os.remove(target)
        except OSError as e:
            return False

    # 确保目标目录存在
    target_dir = os.path.dirname(target)
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError as e:
        return False

    # 创建软链接（处理不同操作系统）
    try:
        if platform.system() == "Windows":
            # Windows 需要管理员权限并区分目录和文件链接
            is_directory = os.path.isdir(source)
            if is_directory:
                # Windows 10以上版本支持目录符号链接，低版本需使用junction
                os.symlink(source, target, target_is_directory=True)
            else:
                os.symlink(source, target)
        else:
            # Unix/Linux/macOS
            os.symlink(source, target)
        return True
    except OSError as e:
        return False


def find_py_directories() -> list[str]:
    """
    查找当前目录下所有以 py_ 开头的文件夹
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    py_dirs = []

    try:
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if item.startswith("py_") and os.path.isdir(item_path):
                py_dirs.append(item_path)
    except OSError as e:
        pass

    return py_dirs


def is_ignored_directory(dir_name: str) -> bool:
    """
    检查目录是否应被忽略
    """
    ignored_dirs = [".git", "__pycache__"]  # 移除了 .cursor 和 .uv
    for ignored in ignored_dirs:
        if ignored in dir_name.split(os.sep):
            return True
    return False


def is_excluded_file(file_name: str) -> bool:
    """
    检查文件是否应被排除不创建链接
    """
    excluded_files = ["README.md", ".gitignore"]  # 添加.gitignore到排除列表
    return file_name in excluded_files


def is_in_whitelist(path: str, source_dir: str) -> bool:
    """
    检查文件或目录是否在白名单中
    """
    try:
        rel_path = os.path.relpath(path, source_dir)
        if rel_path == ".":
            return False

        # 检查路径或其父目录是否在白名单中
        path_parts = rel_path.split(os.sep)
        for i in range(len(path_parts)):
            if os.sep.join(path_parts[: i + 1]) in DEPLOY_WHITELIST:
                return True
        return False
    except (OSError, ValueError) as e:
        return False


def _clean_file_symlinks(root: str, files: list[str], source_dir_basename: str) -> int:
    """
    清理文件软链接

    Args:
        root: 根目录路径
        files: 文件列表
        source_dir_basename: 源目录基本名称

    Returns:
        int: 清理的链接数量
    """
    cleaned_count = 0
    for file in files:
        file_path = os.path.join(root, file)
        if os.path.islink(file_path):
            try:
                link_target = os.readlink(file_path)
                if source_dir_basename in link_target:
                    os.unlink(file_path)
                    cleaned_count += 1
            except OSError as e:
                pass
    return cleaned_count


def _clean_directory_symlinks(
    root: str, dirs: list[str], source_dir_basename: str
) -> tuple[int, list[str]]:
    """
    清理目录软链接

    Args:
        root: 根目录路径
        dirs: 目录列表
        source_dir_basename: 源目录基本名称

    Returns:
        tuple[int, list[str]]: (清理的链接数量, 需要从遍历中移除的目录列表)
    """
    cleaned_count = 0
    removed_dirs = []
    for dir_name in dirs[:]:  # 使用副本进行迭代，因为我们可能会修改dirs
        dir_path = os.path.join(root, dir_name)
        if os.path.islink(dir_path):
            try:
                link_target = os.readlink(dir_path)
                if source_dir_basename in link_target:
                    os.unlink(dir_path)
                    cleaned_count += 1
                    removed_dirs.append(dir_name)  # 记录需要移除的目录
            except OSError as e:
                pass
    return cleaned_count, removed_dirs


def clean_existing_symlinks(
    py_dirs: list[str], source_dir_name: str = "shared-build-system"
) -> int:
    """
    清理目标文件夹中已有的软链接
    """
    cleaned_count = 0
    source_dir_basename = os.path.basename(source_dir_name)

    for py_dir in py_dirs:
        if not os.path.exists(py_dir):
            continue

        # 递归清理子目录中的链接
        try:
            for root, dirs, files in os.walk(py_dir):
                # 清理文件链接
                cleaned_count += _clean_file_symlinks(root, files, source_dir_basename)

                # 清理目录链接
                dir_cleaned_count, removed_dirs = _clean_directory_symlinks(
                    root, dirs, source_dir_basename
                )
                cleaned_count += dir_cleaned_count

                # 从遍历列表中移除已清理的目录
                for removed_dir in removed_dirs:
                    try:
                        dirs.remove(removed_dir)
                    except ValueError:
                        pass  # 目录不在列表中，忽略

        except OSError as e:
            pass

    return cleaned_count


def _process_files_in_directory(
    root: str,
    source_dir: str,
    py_dir: str,
    rel_path: str,
    dirs: list[str],
    files: list[str],
) -> bool:
    """
    处理目录中的文件和子目录，创建软链接
    """
    success = True

    # 处理当前目录中的文件
    for file in files:
        source_file = os.path.join(root, file)

        # 检查是否在白名单中
        if not is_in_whitelist(source_file, source_dir):
            continue

        # 排除特定文件
        if rel_path == "" and is_excluded_file(file):
            continue

        # 排除任何目录下的.gitignore文件
        if file == ".gitignore":
            continue

        target_file = os.path.join(py_dir, rel_path, file)

        if not create_symlink(source_file, target_file):
            success = False

    # 处理当前目录中的子目录
    for dir_name in dirs:
        source_dir_path = os.path.join(root, dir_name)

        # 检查是否在白名单中
        if not is_in_whitelist(source_dir_path, source_dir):
            continue

        target_dir_path = os.path.join(py_dir, rel_path, dir_name)

        # 只为空目录创建链接
        try:
            if not os.listdir(source_dir_path):
                if not create_symlink(source_dir_path, target_dir_path):
                    success = False
        except OSError as e:
            success = False

    return success


def _walk_source_directory(source_dir: str, py_dir: str) -> bool:
    """
    遍历源目录，为指定的py目录创建软链接
    """
    success = True

    # 遍历源目录中的所有内容
    try:
        for root, dirs, files in os.walk(source_dir):
            # 忽略特定目录
            dirs[:] = [d for d in dirs if not is_ignored_directory(d)]

            # 计算相对路径
            rel_path = os.path.relpath(root, source_dir)
            if rel_path == ".":
                rel_path = ""

            if not _process_files_in_directory(
                root, source_dir, py_dir, rel_path, dirs, files
            ):
                success = False
    except OSError as e:
        success = False

    return success


def deploy_to_py_folders() -> bool:
    """
    将 shared-build-system 中的文件部署到所有 py_ 开头的文件夹中
    """
