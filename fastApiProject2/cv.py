import cv2
import time
from collections import OrderedDict
import numpy as np
import os
import argparse
import dlib
import imutils
import shutil
from collections import Counter
import serial

from personal_color import analysis
def clear_image_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def get_stream_video(image_folder):
    # Ensure the image folder exists

    # Define the camera
    cam = cv2.VideoCapture(0)

    start_time = time.time()
    frame_count = 0
    max_frames = 8

    while frame_count < max_frames:
        success, frame = cam.read()
        if not success:
            break
        elapsed_time = time.time() - start_time
        frame_count += 1
        image_filename = os.path.join(image_folder, f'image_{frame_count}.jpg')
        cv2.imwrite(image_filename, frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # Capture an image approximately every 0.8 seconds to get 6 images in 5 seconds
        time.sleep(1)
        #if elapsed_time > 10:
         #   break
    cam.release()


def inferance():
    inference=[]
    imgs = os.listdir('./images')
    for imgpath in imgs:
        try:

            result=analysis(os.path.join('./images', imgpath))
            print(imgpath)

            inference.append(result)
        except Exception as e:

            continue
    print(inference)
    cnt = Counter(inference)
    mode = cnt.most_common(1)
    return mode[0][0]


def extract():


    # 시리얼 포트를 설정합니다 (아두이노가 연결된 포트로 설정해야 합니다)
    arduino_port = 'COM3'  # 실제 아두이노 연결 포트를 확인하고 설정하세요.
    baud_rate = 9600  # 아두이노와 동일한 baud rate 설정
    with open('templates/result.txt', 'r') as f:
        result = f.read()
    list1=['봄 라이트','봄 비비드','가을 뮤트','가을 딥',' 여름 라이트','여름 뮤트','겨울 브라이트','겨울 딥']
    # 시리얼 포트를 엽니다
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)

    time.sleep(2)  # 시리얼 통신이 안정화될 때까지 잠시 대기

    def send_command(command):
        ser.write(f"{command}\n".encode())  # 명령 전송
        time.sleep(2)  # 아두이노가 명령을 처리할 시간을 줍니다

    # 객체 인식 결과로 얻은 숫자 (1부터 8까지의 숫자 중 하나)
    object_recognition_result = list1.index(result)+1  # 예를 들어, 객체 인식 결과가 3이라면

    # 객체 인식 결과를 아두이노로 전송
    send_command(object_recognition_result)

    # 시리얼 포트를 닫습니다
    ser.close()
