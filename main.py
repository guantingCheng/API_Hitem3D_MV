# main.py
import os
from core.client import Hitem3DClient
from config import settings

def main():
    # 1. 初始化
    client = Hitem3DClient(settings.CLIENT_ID, settings.CLIENT_SECRET)
    
    # 2. 設定存放「多視角圖片」的資料夾路徑
    task_folder = os.path.join(settings.INPUT_DIR, "input")

    # 3. 檢查資料夾是否存在
    if os.path.exists(task_folder) and os.path.isdir(task_folder):
        # 提交任務
        task_id = client.submit_multi_view_task(task_folder, settings.DEFAULT_PARAMS)
        
        if task_id:
            # 查詢生成狀態
            model_url = client.wait_for_result(task_id)
            
            if model_url:
                # 下載至 output 資料夾
                client.download_model(model_url, settings.OUTPUT_DIR, settings.DEFAULT_PARAMS["format"], task_id)
    else:
        print(f"❌ 錯誤: 找不到資料夾或路徑不是資料夾: {task_folder}")

if __name__ == "__main__":
    main()