# app.py
import os
import shutil
import time
import requests
import gradio as gr
from core.client import Hitem3DClient
from config import settings

# 初始化 API 客戶端
client = Hitem3DClient(settings.CLIENT_ID, settings.CLIENT_SECRET)

# --- 積分計算邏輯 ---
def calculate_credits(model, resolution, req_type):
    # 積分對照表數據
    cost_table = {
        "hitem3dv1.5": {
            "512": {"1": 5, "2": 15, "3": 15},
            "1024": {"1": 10, "2": 20, "3": 20},
            "1536": {"1": 40, "2": 50, "3": 50},
            "1536pro": {"1": 60, "2": 70, "3": 70},
        },
        "hitem3dv2.0": {
            "1536": {"1": 40, "2": 50, "3": 50},
            "1536pro": {"1": 60, "2": 70, "3": 70},
        },
        "scene-portraitv1.5": {
            "1536": {"1": 40, "2": 50, "3": 50},
        }, 
        "scene-portraitv2.0": {
            "1536pro": {"1": 40, "2": 50, "3": 50},
        }         
    }
    
    try:
        points = cost_table.get(model, {}).get(resolution, {}).get(req_type, "N/A")
        if points == "N/A":
            return "⚠️ 此配置不支援"
        return f"💰 預計消耗積分: {points}"
    except:
        return "⚠️ 參數錯誤"

def update_preview(files):    
    if files is None:              
        return None   
    return [f.name for f in files] 
        
#--處理 Gradio上傳並串接 Hitem3D API
def process_3d_generation(image_files, request_type, resolution, face_count, model_ver, format_type, progress=gr.Progress()):
    if not image_files:
        return "❌ 請先上傳圖片", None, None

    # 1. 建立臨時資料夾存放上傳的圖片
    temp_input_dir = os.path.join(settings.BASE_DIR, "temp_uploads")
    if os.path.exists(temp_input_dir):
        shutil.rmtree(temp_input_dir)
    os.makedirs(temp_input_dir)

    for img in image_files:
        shutil.copy(img.name, temp_input_dir)

    # 2. 準備參數
    params = {
        "request_type": str(request_type),
        "resolution": str(resolution),
        "face": str(face_count),
        "model": str(model_ver),
        "format": str(format_type)
    }

    try:
        progress(0, desc="正在初始化任務...")
        # 3. 提交任務
        task_id = client.submit_multi_view_task(temp_input_dir, params)
        
        if not task_id:
            return "❌ 任務提交失敗，請檢查 API 憑證或圖片格式。", None

        # 4. 輪詢狀態 (修改原本的 wait_for_result 以便配合進度條)
        progress(0.2, desc="任務已提交，雲端處理中...")
        
        model_url = None
        while True:
            # 這裡調用 API 查詢，以便在介面更新狀態
            url = f"{client.base_url}/query-task"
            headers = {"Authorization": f"Bearer {client.access_token}"}
            resp = requests.get(url, headers=headers, params={"task_id": task_id})
            
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                state = data.get("state")
                
                if state == "success":
                    model_url = data.get("url")
                    break
                elif state == "failed":
                    return "❌ 生成失敗，雲端引擎無法處理這些圖片。", None
                else:
                    progress(0.5, desc=f"正在生成中... 目前狀態: {state}")
                    time.sleep(10)
            else:
                time.sleep(5)

        # 5. 下載模型
        progress(0.9, desc="生成完成！正在下載模型...")
        
        # 呼叫 client 的下載函式，傳入 format_type
        save_path = client.download_model(
            url=model_url, 
            output_folder=settings.OUTPUT_DIR, 
            format_code=format_type, 
            task_id=task_id
        )

        if not save_path:
            return "❌ 檔案下載失敗", None, None

        progress(1.0, desc="完成！")
        
        # 6. 判斷預覽與狀態訊息
        is_glb = save_path.lower().endswith(".glb")
        
        status_msg = f"✅ 成功！模型已儲存至: {save_path}"
        
        return status_msg, (save_path if is_glb else None), save_path

    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}", None, None

# --- Gradio UI 介面設計 ---

with gr.Blocks(title="Hitem3D AI 建模生成器") as demo:
    gr.Markdown("# 🧊 Hitem3D AI 多視角建模工具")
    gr.Markdown("上傳物體的多個角度照片（建議 4 張），AI 將自動為您生成 3D 模型。")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1. 上傳照片")
            file_input = gr.File(
                file_count="multiple",
                label="選擇四面視角圖片 (JPG)")
            
            preview_gallery = gr.Gallery(
                label="上傳圖片預覽", 
                show_label=True, 
                columns=4, 
                rows=1, 
                height="300px",
                object_fit="contain"
            )         
            file_input.change(
                fn=update_preview, 
                inputs=file_input, 
                outputs=preview_gallery
            )
            
            gr.Markdown("### 2. 模型參數設定")
            model_ver = gr.Dropdown(
                choices=["hitem3dv1.5", "hitem3dv2.0", "scene-portraitv1.5", "scene-portraitv2.0"], 
                value="hitem3dv1.5", label="模型版本"
            )
            req_type = gr.Radio(
                choices=[("僅幾何", "1"), ("分階幾何/紋理", "2"), ("一次幾何/紋理", "3")], 
                value="3", label="生成類型"
            )
            res = gr.Dropdown(
                choices=["512", "1024", "1536", "1536pro"], 
                value="1024", label="解析度"
            )
            faces = gr.Slider(
                minimum=100000, maximum=2000000, step=100000, 
                value=1000000, label="面數 (Faces)"
            )
            fmt = gr.Radio(
                choices=[("OBJ", "1"), ("GLB", "2"), ("STL", "3"), ("FBX", "4")], 
                value="3", label="輸出格式"
            )
            # 🖼️ 積分顯示區
            credit_display = gr.Label(value="💰 預計使用點數: 15", label="點數使用預估")
            # 監聽參數變化，即時更新積分
            param_inputs = [model_ver, res, req_type]
            for inp in param_inputs:
                inp.change(fn=calculate_credits, inputs=param_inputs, outputs=credit_display)
         
            submit_btn = gr.Button("🚀 開始生成", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### 3. 生成結果")
            status_output = gr.Textbox(label="任務狀態", interactive=True)
            model_preview = gr.Model3D(label="3D 預覽 (僅支援 GLB/OBJ)", clear_color=[1, 1, 1, 1], camera_position=[90, 90, 100])
            file_download = gr.File(label="下載模型檔案")

    # 綁定按鈕動作
    submit_btn.click(
        fn=process_3d_generation,
        inputs=[file_input, req_type, res, faces, model_ver, fmt],
        outputs=[status_output, model_preview, file_download]
    )
    
if __name__ == "__main__":
    demo.launch(share=False)