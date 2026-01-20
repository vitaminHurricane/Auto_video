import cv2
import watching
import mouseact
import main
import time

Monitor_Flag = main.start_flag

def monitor_start():    #所有监视器控制
    global Monitor_Flag
    Monitor_Flag = True

def monitor_stop():
    global Monitor_Flag
    Monitor_Flag = False

class monitor_sidebar():
    def __init__(self, monitor_src: cv2.typing.MatLike, side: str):
        self.unread_num, self.cur_index = 0, 0      #默认没有未完成任务，当前下标为0
        self.cur_index_x, self.cur_index_y = 0, 0   #默认当前下标x，y坐标位置为0
        self.contours, self.mask = None, None       #目标轮廓数组，掩码图片
        self.edge_length = 0                        #目标轮廓边长（画图测试需要）
        self.state = 0                              #状态，找到未完成任务为1，未找到未完成任务为0
        self.side = side                            #侧边栏章节选择区的位置
        self.update(monitor_src, 0, self.side)

    def update(self, monitor_src: cv2.typing.MatLike, repeat_time: int, side: str):
        if repeat_time < 15 and Monitor_Flag:
            self.contours, self.edge_length = watching.img_color_search(monitor_src, main.color_dict['unread_color_red'][0], main.color_dict['unread_color_red'][1])
            if len(self.contours) > 0:
                self.state = 1
                self.unread_num = len(self.contours)
                self.cur_index_x, self.cur_index_y = watching.img_get_location(self.contours, self.cur_index)
            else:
                if side == 'left':
                    mouseact.mouse_move_click(int(main.Screen_Width / 11), int(main.Screen_Height / 2))
                elif side == 'right':
                    mouseact.mouse_move_click(int(main.Screen_Width / 11 * 10), int(main.Screen_Height / 2))
                time.sleep(0.1)
                mouseact.mouse_scroll('down', 30 * 12)
                new_screen = main.screen_update()
                repeat_time += 1
                self.update(new_screen, repeat_time, side)
        else:
            self.state = 2
            print('该课程任务已完成')

    def select_index(self, index: int):     #鼠标选择未完成任务下标
        if self.state == 1:
            self.cur_index = index
            self.cur_index_x, self.cur_index_y = watching.img_get_location(self.contours, self.cur_index)
            mouseact.mouse_move_click(self.cur_index_x - 13 * self.edge_length, self.cur_index_y + int(self.edge_length / 4), clicks = 1)
            time.sleep(0.2)
            new_screen = main.screen_update()
            contours_select, _ = watching.img_color_search(new_screen, main.color_dict['select_green'][0], main.color_dict['select_green'][1], 'green')
            if main.Version == 'old':
                while contours_select == [] and Monitor_Flag:
                    mouseact.mouse_move_click(self.cur_index_x - 13 * self.edge_length, self.cur_index_y + int(self.edge_length / 4), clicks = 1)
                    time.sleep(0.2)
                    new_screen = main.screen_update()
                    contours_select, _ = watching.img_color_search(new_screen, main.color_dict['select_green'][0], main.color_dict['select_green'][1], 'green')
                cur_select_y = contours_select[0][0][0][1]
                while abs(cur_select_y - self.cur_index_y) > 50 and Monitor_Flag:
                    mouseact.mouse_move_click(self.cur_index_x - 13 * self.edge_length, self.cur_index_y + int(self.edge_length / 4), clicks = 1)
                    time.sleep(0.2)
                    new_screen = main.screen_update()
                    contours_select, _ = watching.img_color_search(new_screen, main.color_dict['select_green'][0], main.color_dict['select_green'][1], 'green')
                    cur_select_y = contours_select[0][0][0][1]

    def show_result(self, img_src: cv2.typing.MatLike):
        if self.state == 1:
            self.mask = watching.img_draw_aim(img_src, self.contours, self.edge_length)
            cv2.namedWindow('test', cv2.WINDOW_FREERATIO)
            cv2.resizeWindow('test', 400, 300)
            cv2.imshow('test', self.mask)
            cv2.waitKey()
        else:
            print('无未完成任务')
            


class monitor_text():
    def __init__(self, monitor_src: cv2.typing.MatLike, sidebar_info: monitor_sidebar):
        self.unread_num, self.cur_index = 0, 0      #默认没有未完成任务，当前下标为0
        self.cur_index_x, self.cur_index_y = 0, 0   #默认当前下标x，y坐标位置为0
        self.contours, self.mask = None, None       #目标轮廓数组，掩码图片
        self.edge_length = 0                        #目标轮廓边长（画图测试需要）
        self.state = 0                              #状态，找到未完成任务为1，未找到未完成任务为0
        self.update(monitor_src, sidebar_info, 0)

    def update(self, monitor_src: cv2.typing.MatLike, sidebar_info: monitor_sidebar, repeat_time: int):
        if repeat_time < 15 and Monitor_Flag:     #递归检测出口判断
            self.contours, self.edge_length = watching.img_color_search(monitor_src, main.color_dict['unread_color_yellow'][0], main.color_dict['unread_color_yellow'][1], 'yellow')
            if len(self.contours) > 0:
                self.state = 1
                self.unread_num = len(self.contours)
                self.cur_index_x, self.cur_index_y = watching.img_get_location(self.contours, self.cur_index)
            else:
                if sidebar_info.side == 'left':
                    mouseact.mouse_move_click(sidebar_info.cur_index_x + sidebar_info.edge_length * 5, int(main.Screen_Height / 2))
                elif sidebar_info.side == 'right':
                    mouseact.mouse_move_click(sidebar_info.cur_index_x - sidebar_info.edge_length * 20, int(main.Screen_Height / 2))
                mouseact.mouse_scroll('down', sidebar_info.edge_length * 30)
                time.sleep(0.2)
                new_screen = main.screen_update()
                repeat_time += 1
                self.update(new_screen, sidebar_info, repeat_time)
        else:
            self.cur_index_x, self.cur_index_y = 0, 0
            self.state = 2
            print('当前章节任务已完成')

    def start_work(self, sidebar_info: monitor_sidebar):
        while self.cur_index_y > int(main.Screen_Height / 2.5) and Monitor_Flag:
            if sidebar_info.side == 'left':
                mouseact.mouse_move_click(sidebar_info.cur_index_x + sidebar_info.edge_length * 5, int(main.Screen_Height / 2))
            elif sidebar_info.side == 'right':
                mouseact.mouse_move_click(sidebar_info.cur_index_x - sidebar_info.edge_length * 20, int(main.Screen_Height / 2))
            mouseact.mouse_scroll('down', self.edge_length * 5)
            time.sleep(0.1)
            new_screen = main.screen_update()
            self.update(new_screen, sidebar_info, 0)
        time.sleep(0.1)
        if main.Version == 'old':
            mouseact.mouse_move_click(self.cur_index_x + self.edge_length * 29, self.cur_index_y + self.edge_length * 18)
        elif main.Version == 'new':
            mouseact.mouse_move_click(self.cur_index_x + self.edge_length * 41, self.cur_index_y + self.edge_length * 25)
        time.sleep(0.5)
        pre_screen = main.screen_update()
        mouseact.mouse_move_click(clicks = 1)
        time.sleep(0.2)
        new_screen = main.screen_update()
        state = watching.img_compare(pre_screen, new_screen)
        print(state)
        if state >= 0.99999:          #当state等于1，判断当前任务点为ppt课件
            state = 1
            print('是ppt任务')
            mouseact.mouse_move_click(side = 'middle', clicks = 1)
            if main.Version == 'old':
                mouseact.mouse_move_click(self.cur_index_x + self.edge_length * 29, self.cur_index_y + self.edge_length * 35)
            elif main.Version == 'new':
                mouseact.mouse_move_click(self.cur_index_x + self.edge_length * 40, self.cur_index_y + self.edge_length * 42)
        else:                   #其余情况，判断当前任务点为视频
            print('是视频任务')
            pass
        pre_screen = new_screen
        time.sleep(1)
        new_screen = main.screen_update()
        similarity = watching.img_compare(pre_screen, new_screen) 
        while similarity != 1.0 and Monitor_Flag:
            pre_screen = new_screen
            time.sleep(1)
            new_screen = main.screen_update()
            similarity = watching.img_compare(pre_screen, new_screen) 
            if similarity >= 0.99999:
                similarity = 1
        finish_flag = False
        while state != 1 and Monitor_Flag and not finish_flag:      #检测到任务点是视频的情况下的保留判断，防止小人在视频里不给画面只放音乐水时长导致任务点判断失误（真没招了）
            pre_screen = new_screen
            pre_index_y = self.cur_index_y
            time.sleep(1)
            new_screen = main.screen_update()
            self.update(new_screen, sidebar_info, 0)
            cur_index_y = self.cur_index_y
            if cur_index_y != 0:
                if abs(pre_index_y - cur_index_y) < 50:     #任务点仍未完成，即出现黑屏播放水视频情况
                    print('视频未结束')
                else:
                    print('视频结束')
                    finish_flag = True
            else:
                break
        if state >= 0.99999:          #是ppt任务则在结束时更新，视频的更新再上述while里更新过了
            mouseact.mouse_move_click(clicks = 1)
            self.update(new_screen, sidebar_info, 0)

    def show_result(self, img_src: cv2.typing.MatLike):
        if self.state == 1:
            self.mask = watching.img_draw_aim(img_src, self.contours, self.edge_length)
            cv2.namedWindow('test', cv2.WINDOW_FREERATIO)
            cv2.resizeWindow('test', 400, 300)
            cv2.imshow('test', self.mask)
            cv2.waitKey()
        else:
            print('无未完成任务')