此檔案僅在Win10 LTSC 測試，其他Windows版本尚未測試。

/需求/
	1. 安裝python     ========https://www.python.org/downloads/
	2. 申請Hitem3D帳號  =====https://platform.hitem3d.ai/
	3. 並創造API Key     ======https://platform.hitem3d.ai/console/apiKey/
	**API key 務必用記事本另外紀錄，只能開啟一次!!!!**

/安裝步驟/
	1. 檔案先解壓縮
	2. 安裝 setup.bat

/填寫API key/
	1. 開啟路徑：[core]-> settings.py
	2. 輸入 CLIENT_ID            (Access Key)
	3. 輸入 CLIENT_SECRET  (Secret Key)
	4. 保存文件 

/開啟步驟/
	1. 開啟 App-Launcher.bat
	2. 重新整理網頁(按 F5)
	3. 正常使用

/使用步驟/
	1. 放入選好的四張照片
	2. 選擇 模型版本  
	3. 選擇 生成類型 
	4. 選擇 解析度
	5. 選擇 面數 ( 範圍建議: 100,000～2,000,000 )
		512 ------------ 500,000; 
		1024----------1,000,000; 
		1536---------- 2,000,000; 
		1536 pro------ 2,000,000;
	**版本、類型、解析度會影響點數消耗**
	6. 選擇輸出類型
	7. 按下開始生成
	8. 等待時間約3分鐘...
	9. 到 [data] 資料夾確認檔案，如果無法開啟，請把副檔名換成.glb



