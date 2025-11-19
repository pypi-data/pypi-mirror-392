import os

import requests

# files	form-data	文件列表	要上传的文件（多文件）
# path	query	字符串	文件保存的相对路径（可选，默认为根目录）
# is_cover	query	int整型	如果文件存在，是否覆盖（可选，默认为0不替换，）
# file_name	query	字符串	文件重命名(可选，默认原文件名),使用此参数只能上传单文件

# 上传文件到chfs上  chfs_path为chfs的路径，不包含F:/wsl/chfs/,比如要上传到：F:/wsl/chfs/test，直接填test就行 is_cover=1为如果文件存在则覆盖，为0则文件存在就取消上传
def upload(file_path, chfs_path="test", is_cover=1):
    url = "http://192.168.31.22:8081/upload"
    params = {
        "path": chfs_path,
        "is_cover": is_cover
    }
    files = {
        "files": (file_path, open(file_path, "rb"))
    }

    response = requests.post(url, params=params, files=files)
    return response.json()

# 下载
def download(chfs_file_path):
    url = f"http://192.168.31.22:8081/download?file_path={chfs_file_path}"
    response = requests.get(url, stream=True)
    local_file_name = os.path.basename(chfs_file_path)

    if response.status_code == 200:
        with open(local_file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
        print("文件下载成功")
    else:
        print("文件下载失败:", response.json())


# 查询文件 默认查询/目录下的所有目录和文件
def get_file_list(path="/",page=1,per_page=2):
    url = f"http://192.168.31.22:8081/list?dir_path={path}&page={page}&per_page={per_page}"
    response = requests.get(url)
    return response.json()



