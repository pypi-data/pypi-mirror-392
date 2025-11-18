import json
import os
import datetime
import time

def parse_date_from_filename(filename):
    """
    从文件名中解析日期
    支持常见的日期格式，如: 20231225, 2023-12-25, 20231225_1030等
    
    Args:
        filename (str): 文件名
        
    Returns:
        datetime: 解析出的日期时间对象，如果解析失败返回None
    """
    import re
    
    # 常见的日期格式正则表达式
    date_patterns = [
        r'(\d{4})(\d{2})(\d{2})',  # 20231225
        r'(\d{4})-(\d{2})-(\d{2})',  # 2023-12-25
        r'(\d{4})_(\d{2})_(\d{2})',  # 2023_12_25
        r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})',  # 20231225_1030
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                if len(match.groups()) == 3:
                    year, month, day = map(int, match.groups())
                    return datetime(year, month, day)
                elif len(match.groups()) == 5:
                    year, month, day, hour, minute = map(int, match.groups())
                    return datetime(year, month, day, hour, minute)
            except ValueError:
                continue
    
    return None


def delete_old_files(folder_path, days=7):
    """
    删除指定文件夹中days天以前的文件
    
    Args:
        folder_path (str): 文件夹路径
        days (int): 天数，默认7天
    """
    # 计算截止日期
    cutoff_time = time.time() - days * 24 * 60 * 60
    
    try:
        # 获取文件夹中的所有文件
        files = os.listdir(folder_path)
        
        deleted_count = 0
        error_count = 0
        
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            
            # 跳过目录，只处理文件
            if os.path.isfile(file_path):
                try:
                    # 解析文件名中的日期（假设文件名包含日期）
                    file_date = parse_date_from_filename(file_name)
                    
                    if file_date:
                        # 如果文件日期早于截止日期，则删除
                        file_timestamp = file_date.timestamp()
                        if file_timestamp < cutoff_time:
                            os.remove(file_path)
                            print(f"已删除文件: {file_name}")
                            deleted_count += 1
                    else:
                        # 如果无法从文件名解析日期，使用文件修改时间
                        file_mtime = os.path.getmtime(file_path)
                        if file_mtime < cutoff_time:
                            os.remove(file_path)
                            print(f"已删除文件(按修改时间): {file_name}")
                            deleted_count += 1
                            
                except Exception as e:
                    print(f"处理文件 {file_name} 时出错: {e}")
                    error_count += 1
        
        print(f"\n操作完成！")
        print(f"成功删除文件数: {deleted_count}")
        print(f"处理出错文件数: {error_count}")
        
    except Exception as e:
        print(f"访问文件夹时出错: {e}")

def read_file_to_list(file_address: str) -> list:
    """
    打开文件，并输出文件内容为列表\n
    输入：文件地址
    输出：列表形式的文件内容
    """
    try:
        f = open(file_address, 'r', encoding="utf-8")
        content = f.read()
        # 将读取内容转化为列表
        file_content = json.loads(content)
    except json.decoder.JSONDecodeError:
        file_content = []
    except FileNotFoundError:
        file_content = []
        f = open(file_address, 'w')
        f.close()
    return file_content


def save_list_to_file(list, file_adress) -> None:
    """
    保存列表到文件
    输入：列表，文件地址
    输出：无
    """
    save_json = open(file_adress, 'w', encoding='utf-8')
    # 通过json.dumps()把dict降级为字符串
    save_json.write(json.dumps(list, indent=4, ensure_ascii=False))
    save_json.close()


def get_file_name_from_folder(folder_path: str, file_extension: str) -> list:
    """
    从文件夹中获取所有文件的名称（不含文件拓展名）
    输入：文件夹路径，文件拓展名
    返回：包含文件名的列表
    """
    files_name_list = []

    # 使用os.listdir()函数获取文件夹中的所有文件和子文件夹
    files_and_folders = os.listdir(folder_path)

    # 遍历文件和子文件夹列表
    for item in files_and_folders:
        # 使用os.path.isfile()函数检查当前项是否为文件
        if os.path.isfile(os.path.join(folder_path, item)):
            # 如果是文件，则append到列表中
            files_name_list.append(item.rstrip("." + file_extension))

    return files_name_list


def get_file_full_name_from_folder(folder_path: str) -> list:
    """
    从文件夹中获取所有文件的完整名称
    输入：文件夹路径，文件拓展名
    返回：包含文件名的列表
    """
    files_name_list = []

    # 使用os.listdir()函数获取文件夹中的所有文件和子文件夹
    files_and_folders = os.listdir(folder_path)

    # 遍历文件和子文件夹列表
    for item in files_and_folders:
        # 使用os.path.isfile()函数检查当前项是否为文件
        if os.path.isfile(os.path.join(folder_path, item)):
            # 如果是文件，则append到列表中
            files_name_list.append(item)

    return files_name_list


def get_file_and_folder_full_name_from_folder(folder_path: str) -> list:
    """
    从文件夹中获取所有文件、文件夹的完整名称
    输入：文件夹路径，文件拓展名
    返回：包含文件名、文件夹名的列表
    """

    # 使用os.listdir()函数获取文件夹中的所有文件和子文件夹
    files_and_folders = os.listdir(folder_path)

    return files_and_folders
