import user_config
import mss
import cv2
from pynput import keyboard
import numpy as np
import monitor
import time

SideBar_Direct = user_config.SideBar_Direct     #侧边栏位置，只能为left或者right
Screen_Width = user_config.Screen_Width         #屏幕尺寸->宽度
Screen_Height = user_config.Screen_Height       #屏幕尺寸->高度
Version = user_config.Version                   #学习通网页版版本，只能为old或者new
Original = user_config.Original                 #是否是原生板网页（未装插件），原生态则为True，使用了插件则为False（这里装插件的情况下只能适配edge浏览器上的Dark Reader插件）

start_flag = False

#关键点色彩阈值
if Original:    #原生态配色
    if Version == 'old':
        color_dict = {
            # 老版本
            'unread_color_red': np.array([[46, 114, 233], [69, 130, 255]]),
            'unread_color_yellow': np.array([[45, 168, 254], [78, 200, 255]]),
            'select_green': np.array([[47, 149, 118], [63, 160, 132]]),  
        }
    elif Version == 'new':
        color_dict = {
            # 新版本
            'unread_color_red': np.array([[68, 164, 233], [140, 232, 254]]),
            'unread_color_yellow': np.array([[45, 168, 254], [78, 200, 255]]),
            'select_green': np.array([[39, 133, 103], [43, 137, 107]]),  
        }
else:       #使用Dark Reader插件后的配色
    if Version == 'old':
        color_dict = {
            # 老版本
            'unread_color_red': np.array([[0, 52, 159], [44, 80, 186]]),
            'unread_color_yellow': np.array([[45, 168, 254], [78, 200, 255]]),
            'select_green': np.array([[39, 133, 103], [43, 137, 107]]),  
        }
    elif Version == 'new':
        color_dict = {
            # 新版本
            'unread_color_red': np.array([[71, 178, 247], [120, 211, 253]]),
            'unread_color_yellow': np.array([[45, 168, 254], [78, 200, 255]]),
            'select_green': np.array([[39, 133, 103], [43, 137, 107]]),
        }

def main():
    #初始化mss用于屏幕捕获
    key_listener = keyboard.Listener(on_press = key_monitor)
    key_listener.start()
    print('按下enter以开始脚本, 按下esc再按下enter退出脚本')
    input()
    
    with mss.mss() as sct:                                  #获取主显示器的分辨率（也可指定区域：top, left, width, height）
        screen_monitor = sct.monitors[1]                    #monitors[0]是整个屏幕，monitors[1]是主显示器

        while start_flag:
            screenshot = sct.grab(screen_monitor)
            frame = np.array(screenshot)                         #转换为OpenCV可处理的BGR格式（mss返回的是BGRA，需转换）
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  #先转为numpy数组，再从BGRA转BGR
        #侧边栏状态检测
            sidebar = monitor.monitor_sidebar(frame_bgr.copy(), SideBar_Direct) #创建侧边栏监视对象
            while sidebar.state == 1 and start_flag:                    #侧边栏有未完成章节
                sidebar.select_index(0)
                time.sleep(4)                                           #切换章节，等待四秒确保内容刷新完毕
                frame_bgr = screen_update()                             #内容刷新完毕后更新屏幕
                text = monitor.monitor_text(frame_bgr.copy(), sidebar)  #创建文本监视对象
                while text.state == 1 and start_flag:                   #检测到章节内有未完成任务点
                    text.start_work(sidebar)                            #开始完成当前任务点
                    frame_bgr = screen_update()                         #完成任务点后刷新屏幕
                time.sleep(1)
                frame_bgr = screen_update()
                sidebar.update(frame_bgr.copy(), 0, SideBar_Direct)     #侧边栏监视器更新
            else:
                print('课程完成，将退出脚本')
                break
        #完成侧边栏检测 
    # cv2.destroyAllWindows()
    print('脚本结束')

def screen_update():
    with mss.mss() as sct:
        screen_monitor = sct.monitors[1]
        screenshot = sct.grab(screen_monitor)
        frame = np.array(screenshot)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    return frame_bgr
    
def key_monitor(key):
    global start_flag
    if key == keyboard.Key.esc:
        monitor.monitor_stop()
        start_flag = False
        return False
    elif key == keyboard.Key.enter:
        monitor.monitor_start()
        start_flag = True

if __name__ == "__main__":  
    main()