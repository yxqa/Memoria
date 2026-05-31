import requests


def Memoria_test():
    # 1. 登录（使用 JSON 格式）
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    resp = requests.post(
        login_url,
        json={"username": "wangwu", "password": "123456"}   # 注意使用 json 参数
    )
    print("登录状态码:", resp.status_code)
    if resp.status_code != 200:
        print("登录失败:", resp.text)
        exit()

    token_data = resp.json()
    access_token = token_data.get("access_token")  # 根据实际字段调整
    if not access_token:
        print("响应中没有 access_token:", token_data)
        exit()

    print("获取 Token 成功")

    # 2. 创建记忆（使用 multipart/form-data）
    # 2. 创建记忆（使用 multipart/form-data）
    memories_url = "http://127.0.0.1:8000/api/v1/memories"
    headers = {"Authorization": f"Bearer {access_token}"}

    data = {
        "content": "今天去了大理",
        "mood": "开心",
        "location": "大理",
        "happened_at": "2026-05-31T10:00:00",
        "tags": ["开心", "旅行"],  # 多个标签
    }

    # 如果有图片/视频就加，没有就不传
    # files = [
    #     ("image", ("photo.jpg", open("photo.jpg", "rb"), "image/jpeg")),
    # ]

    response = requests.post(
        memories_url,
        data=data,
        # files=files,   # 没有文件就去掉这行
        headers=headers
    )
    print("创建记忆状态码:", response.status_code)
    print("响应内容:", response.text)

def get_memoria_test():
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    resp = requests.post(
        login_url,
        json={"username": "wangwu", "password": "123456"}
    )
    if resp.status_code != 200:
        print("登录失败", resp.text)
        exit()

    access_token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    memories_url = "http://127.0.0.1:8000/api/v1/memories"

    text_memoria = [
        {"content": "今天去了大理", "mood": "开心", "location": "大理·洱海边"},
        {"content": "在家看书", "mood": "平静", "location": "家里"},
        {"content": "和朋友吃火锅", "mood": "开心", "location": "成都"},
    ]

    r = requests.get(
        memories_url,
        headers=headers
    )
    print("状态码", r.status_code)
    print(r.json())

if __name__ == "__main__":

    get_memoria_test()
    # Memoria_test()