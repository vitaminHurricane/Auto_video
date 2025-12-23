import cv2
import numpy as np
import math

def __img_sumarea(contours):
    sum = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        sum += area
    return sum

def __img_filter(contours):
    new_contours = []
    for cnt in contours:
        if cv2.contourArea(cnt) < 200:
            continue
        else:
            new_contours.append(cnt)
    return new_contours

def img_color_search(src: cv2.typing.MatLike, min_list, max_list):
    search_kernel = np.array((3, 3), np.uint8)              #卷积核

    mask_temp = cv2.inRange(src, min_list, max_list)
    mask_temp = cv2.erode(mask_temp.copy(), search_kernel, iterations = 1)
    mask = cv2.dilate(mask_temp.copy(), search_kernel, iterations = 4)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = __img_filter(contours)

    # cv2.namedWindow('test', cv2.WINDOW_FREERATIO)
    # cv2.resizeWindow('test', 400, 300)
    # cv2.imshow('test', mask)
    # cv2.waitKey()

    valid_contours = []
    edge = 0
    if len(contours) > 0:
        sum_area = __img_sumarea(contours)
        average_area = sum_area / len(contours)
        edge = int(math.sqrt(average_area))
        for cnt in contours:
            if math.fabs(average_area - cv2.contourArea(cnt)) / average_area <= 0.5:
                valid_contours.append(cnt)
        valid_contours = sorted(valid_contours, key = lambda y_loc: y_loc[0][0][1], reverse = False)

    return valid_contours, edge

def img_draw_aim(src: cv2.typing.MatLike, contours, square_length: int):
    if len(contours) > 0:
        for i in range(0, len(contours)):
            point1 = (contours[i][0][0][0] - int(square_length / 2), contours[i][0][0][1])
            point2 = (contours[i][0][0][0] + int(square_length / 2), contours[i][0][0][1] + square_length)
            cv2.rectangle(src, point1, point2, color = (0, 0, 255), thickness = 1)

    return src
        
def img_compare(compared1: cv2.typing.MatLike, compared2: cv2.typing.MatLike):
    img1 = cv2.cvtColor(compared1, cv2.COLOR_BGR2HSV)
    img2 = cv2.cvtColor(compared2, cv2.COLOR_BGR2HSV)
    hist1 = cv2.calcHist([img1], [0, 1], None, [180, 256], [0, 180, 0, 256])
    hist2 = cv2.calcHist([img2], [0, 1], None, [180, 256], [0, 180, 0, 256])
    cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
    cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    return similarity

def img_get_location(contours, index: int):
    loc_x, loc_y = 0, 0
    if contours != []:
        loc_x = contours[index][0][0][0]
        loc_y = contours[index][0][0][1]

    return loc_x, loc_y



