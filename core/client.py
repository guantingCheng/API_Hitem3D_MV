# core/client.py
import requests
import time
import base64
import os
from config import settings

class Hitem3DClient:
    def __init__(self, client_id, client_secret):
        self.base_url = "https://api.hitem3d.ai/open-api/v1"
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    # 獲取 Access Token
    def get_token(self):
        url = f"{self.base_url}/auth/token"
        
        # 構造 Basic Auth
        auth_str = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json={})
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 200:
                self.access_token = data["data"]["accessToken"]
                print("✅ 成功獲取 Token")
                return self.access_token
            else:
                raise Exception(f"獲取 Token 失敗: {data}")
        except Exception as e:
            print(f"❌ 認證錯誤: {e}")
            return None       


    # 接收 params 參數，上傳圖片並創建任務
    def submit_multi_view_task(self, image_folder, params):
        if not self.access_token:
            self.get_token()

        url = f"{self.base_url}/submit-task"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        # 參數設置：request_type=3 (幾何+紋理), model=hitem3dv1.5 (推薦)
        data = params
        
        
        # 1. 獲取資料夾內所有圖片路徑
        valid_extensions = ('.jpg', '.jpeg', '.png')
        image_files = [
            os.path.join(image_folder, f) for f in os.listdir(image_folder) 
            if f.lower().endswith(valid_extensions)
        ]

        if not image_files:
            print(f"❌ 錯誤：資料夾 {image_folder} 內找不到圖片")
            return None
       
       # 2. 開啟所有檔案並準備 files 列表
       # 使用 ExitStack 可以動態開啟不確定數量的檔案並確保關閉
        from contextlib import ExitStack
        
        try:
            with ExitStack() as stack:
                # 構造符合 API 規範的 multi_images 列表
                files = []
                for img_path in image_files:
                    f = stack.enter_context(open(img_path, "rb"))
                    # 格式: (欄位名稱, (檔名, 檔案物件, MIME類型))
                    files.append(
                        ('multi_images', (os.path.basename(img_path), f, 'image/jpeg'))
                    )

                print(f"🚀 正在上傳 {len(files)} 張視角圖並提交任務...")
                
                # 3. 發送請求 (data 放入原本的參數，files 放入圖片列表)
                response = requests.post(url, headers=headers, data=data, files=files)
                response.raise_for_status()
                
                result = response.json()
                if result.get("code") == 200:
                    task_id = result["data"]["task_id"]
                    print(f"✅ 多視角任務提交成功! Task ID: {task_id}")
                    return task_id
                else:
                    print(f"❌ 提交失敗: {result}")                        
                    return None

        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            return None             
    
    # 查詢任務狀態
    def wait_for_result(self, task_id):
        url = f"{self.base_url}/query-task"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        print("⏳ 正在等待生成結果 (每10秒查詢一次)...")
        while True:
            try:
                response = requests.get(url, headers=headers, params={"task_id": task_id})
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    state = data.get("state")
                    
                    if state == "success":
                        model_url = data.get("url")
                        print(f"🎉 生成成功! 下載鏈接: {model_url}")
                        return model_url
                    elif state == "failed":
                        print("❌ 生成失敗，請檢查輸入圖片。")
                        return None
                    elif state in ["queueing", "processing", "created"]:
                        print(f"   狀態: {state} ...")
                        time.sleep(10)  # 等待 10 秒再次查詢
                    else:
                        print(f"⚠️ 未知狀態: {state}")
                        break
                else:
                    print("網絡請求錯誤，重試中...")
                    time.sleep(5)
            except KeyboardInterrupt:
                print("停止查詢")
                break

    #下載最終模型
        """
        根據 format_code 動態決定副檔名並下載
        1: OBJ 
        2: GLB
        3: STL
        4: FBX
        5: USDZ
        """    
    def download_model(self, url, output_folder, format_code, task_id):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        ext_map = {"1": "obj", "2": "glb", "3": "stl", "4": "fbx", "5": "usdz"}
        ext = ext_map.get(str(format_code), "glb")
        
        filename = os.path.join(output_folder, f"result_{task_id}.{ext}")
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        return None
