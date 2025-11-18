# HappyLife

HappyLife 將重複的事情抽象為函數，自動運行。  
不做無聊的事，體驗有趣的事，讓人生更輕鬆。

安裝方法：
```shell
pip install HappyLife
```
## 依賴關係

安裝HappyLife會自動安裝依賴套件


## 使用教學

### 後臺操作（綁定窗口後，可以後臺運行，但窗口不能最小化，使用者可做別的事情）

>       from auto import Bd  # 引入類別

>       # 綁定夜神模擬器方法  
>       bd = Bd("夜神模擬器")

>       # 綁定雷電模擬器方法(需額外綁定子窗口)  
>       bd = Bd('雷電模擬器');  
>       bd.bind_child_window(0)

>       Bd.keypress(bd,65,2) # 按下A鍵2秒後鬆開
>       bd.img_click(bd,'0.png')  # 點擊圖片  
>       bd.img_drag(bd,'1.png','2.png')  # 拖拽圖片，滑鼠從圖片1座標拖拽到圖片2座標的位置  
>       bd.lclick(bd,55,64)   # 左鍵單擊  
>       bd.lclick2(bd,55,64)  # 左鍵雙擊  
>       bd.rclick(bd,55,64)   # 右鍵單擊  

>       bd.topwd() # 窗口置頂
>       bd.closewd() # 窗口關閉
>       bd.miniwd() # 窗口最小化
>       bd.maxwd() # 窗口最大化
>       bd.hidewd() # 窗口隱藏
>       bd.showwd() # 窗口顯示(隱藏後顯示)
>       bd.wd_transparency() # 窗口透明度
>       bd.getpoint() # 獲取相對座標


### 前臺操作（必須在當前窗口，才能運行，使用者無法做別的事情，通常後臺操作無效時才會使用此方法）

>       from auto import Fd   # 引入類別

>       Fd.img_click('1.png')   # 點擊圖片  
>       Fd.img_drag('1.png','2.png')   # 拖拽圖片，滑鼠從圖片1座標拖拽到圖片2座標的位置  
>       Fd.lclick(55,64)  # 左鍵單擊  
>       Fd.lclick2(55,64) # 左鍵雙擊  
>       Fd.rclick(55,64)  # 右鍵單擊  
>       Fd.keypress(65)   # keypress(按鍵代碼,按下X秒後自動鬆開)  
>       Fd.key_down(65)   # 按鍵按下，key_down(按鍵代碼)  
>       Fd.key_up(65)     # 按鍵鬆開，key_up(按鍵代碼)  

>       # 打開檔案/資料夾/網址  
>       Fd.open_file("D:\\code\\123.py")  
>       Fd.open_file("C:\\Program Files (x86)\\Windows Defender")  
>       Fd.open_file("http://www.j4.com.tw/big-gb/")  

* 如果使用前臺操作，無法自動操作滑鼠鍵盤，請用系統管理員身份啓動腳本

## 依序執行任務的方法

>       # 要執行的任務列表
>       tasks = [
>           (bd.img_click, bd,"81.png"), #(函數, 參數：可以填寫多個參數)
>           (bd.img_click, bd,"82.png"),
>           (bd.img_click, bd,"83.png"),
>           (bd.img_click, bd,"84.png")
>       ]
>       # 按照順序執行任務，完成全部任務跳出迴圈
>       execute_tasks_in_sequence(tasks)




### 圖色識別

>       import auto # 引入


>       auto.img_center_point() # 獲取圖片中心點坐標，img_center_point('1.jpg', confidence=0.9, grayscale=True)
>       auto.img_center_point2() # 後臺獲取圖片中心點坐標，img_center_point2(bd,'1.jpg', confidence=0.9, grayscale=True)
>       auto.mouse_getRGB() # 獲取滑鼠坐標和RGB顏色
>       auto.mouse_getHEX() # 獲取滑鼠坐標和HEX顏色
>       auto.matches_color() # 坐標找色，matches_color(100, 200, (25, 118, 199), tolerance=20)
