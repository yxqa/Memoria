import requests

BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

def get_access_token(username="wangwu", password="123456"):
    """登录并返回 access_token，失败则退出程序"""
    resp = requests.post(
        LOGIN_URL,
        json={"username": username, "password": password}
    )

    if resp.status_code != 200:
        print(f"登录失败: {resp.text}")
        exit()

    token_data = resp.json()
    access_token = token_data.get("access_token")

    if not access_token:
        print("响应中没有 access_token:", token_data)
        exit()
    print("获取 Token 成功")
    return access_token

def create_memoria():
    """创建记忆示例"""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/v1/memories"
    data = {
        "content": "今天去了大理",
        "mood": "开心",
        "location": "大理",
        "happened_at": "2026-05-31T10:00:00",
        "tags": ["开心", "旅行"],
    }
    # 如果有文件，可添加 files 参数
    response = requests.post(url, data=data, headers=headers)
    print("创建记忆状态码:", response.status_code)
    print("响应内容:", response.text)

def get_all_memories():
    """获取所有记忆"""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/v1/memories"
    resp = requests.get(url, headers=headers)
    print("状态码:", resp.status_code)
    print(resp.json())

def get_one_memoria(memoria_id: str):
    """根据 ID 获取单个记忆"""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    # 修正：使用变量拼接 URL
    url = f"{BASE_URL}/api/v1/memories/{memoria_id}"
    resp = requests.get(url, headers=headers)
    print(resp.json())

if __name__ == "__main__":
    # 示例用法
    # get_all_memories()
    # 获取指定记忆，请替换成真实 ID
    get_one_memoria("1541a841-b3d0-478e-81dd-c5e559fc7a98")