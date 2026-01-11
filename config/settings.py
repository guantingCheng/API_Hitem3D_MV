# config/settings.py
import os

# API 憑證
CLIENT_ID = "輸入Access Key:"
CLIENT_SECRET = "輸入Secret Key:"

# 路徑設定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "data")

# 模型參數
DEFAULT_PARAMS = {
    "request_type": "1",     # 1: 僅幾何; 2: 分階生成:幾何+紋理; 3: 一次生成:幾何+紋理
    "resolution": "512",     # 512, 1024, 1536, 1536pro  (V2.0 = 1536, 1536pro)
    "face": "1000000",       # 範圍建議: 100,000～2,000,000 (512 = 500,000; 1024 = 1,000,000; 1536 = 2,000,000; 1536pro = 2,000,000)
    "model": "hitem3dv1.5",  # v2.0模型（hitem3dv2.0、scene-portraitv2.0）不支持 request_type=2
    "format": "2"            # 1:obj; 2:glb; 3:stl; 4:fbx; 5:usdz
}