from controlMotor import *
from hanoi import *
import jetson.inference
import jetson.utils

coordinates = [
    [[11, 2.2, -1.3], [11.2, 2.2, 2.5], [11, -0.9, 2.3]],
    [[11, 2.2, -1.6], [11.2, 2.2, 2.5], [12.9, -4.2, 2.1]],
    [[11, -1, -3], [11.3, -1, 2.5], [13.5, -4.5, 2.2]],  # y should go to + when down but, no change
    [[11, 2.1, -2.5], [11.3, 2.2, 2.4], [11, -0.9, 2.3]],
    [[13.4, -4.5, -2.7], [13.4, -4.5, 2.5], [12, 2.3, 2.3]],
    [[13.4, -4.5, -3.4], [13.4, -4.5, 2.5], [11.9, -0.8, 2.3]],
    [[11, 2.2, -2.5], [11.2, 2.2, 2.3], [11.1, -0.8, 2.3]],
    [[12, 2.3, -3.3], [12.3, 2.4, 2.4], [13.7, -4.5, 2.3]],  # modify z +0.2 1st, x + 0.1 3rd, y + 0.1 3rd
    [[11, -1, -1.6], [11.4, -1, 2.5], [13.5, -4.5, 2.3]],
    [[11, -1, -2.5], [11.4, -1, 2.5], [11.5, 2.2, 2.3]],
    [[13.4, -4.5, -2.8], [13.4, -4.5, 2.5], [12, 2.3, 2.5]],
    [[11.5, -1, -3], [11.5, -1, 2.5], [13.4, -4.5, 2.3]],
    [[11, 2.2, -2.5], [11.2, 2.2, 2.5], [11, -0.8, 2.3]],
    [[11, 2.2, -3], [11.2, 2.2, 2.5], [13.1, -4.3, 2.3]],  # modify y + 0.1 3rd
    [[11, -1, -3], [11.3, -1, 2.5], [13.5, -4.5, 2.2]]  # modify y + 0.1 3rd
]


if __name__ == '__main__':
    net = jetson.inference.detectNet(
        argv=["--model=../jetson-inference/python/training/detection/ssd/models/05_23_1100/ssd-mobilenet.onnx",
              "--labels=../jetson-inference/python/training/detection/ssd/models/05_23_1100/labels.txt",
              "--input-blob=input_0", "--output-cvg=scores", "--output-bbox=boxes", "--threshold=0.2"])
    camera = jetson.utils.videoSource("/dev/video0")  # "/dev/video0" for V4L2
    display = jetson.utils.videoOutput("display://0")  # "my_video.mp4" for file

    cm = ControlMotor()
    h = HanoiTower(4)
    prev_state_labels = []
    cnt = 0

    cm.setDefault()
    while display.IsStreaming():
        state = [{}, {}, {}]
        img = camera.Capture()
        detections = net.Detect(img)
        height = display.GetHeight()
        width = display.GetWidth()
        jetson.utils.cudaDrawLine(img, (width / 3, 0), (width / 3, height), (255, 255, 255, 255), 5)
        jetson.utils.cudaDrawLine(img, (width / 3 * 2, 0), (width / 3 * 2, height), (255, 255, 255, 255), 5)

        display.Render(img)
        display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

        for detection in detections:
            # 학습 때 label 순서를 잘못 입력하여 가시성을 위한 classId 변경 부분
            if detection.ClassID == 3:
                classId = 1
            elif detection.ClassID == 1:
                classId = 2
            elif detection.ClassID == 2:
                classId = 3
            elif detection.ClassID == 4:
                classId = 4
            else:
                classId = 0

            # 원반의 좌표로 어느 기둥에 위치하는지 판단
            if 0 < detection.Center[0] < width / 3:
                state[0][classId] = detection.Center[1]
            elif width / 3 < detection.Center[0] < width / 3 * 2:
                state[1][classId] = detection.Center[1]
            elif width / 3 * 2 < detection.Center[0] < width:
                state[2][classId] = detection.Center[1]

        # 원반이 인식된 높이를 이용하여 기둥에 놓여있는 순서 판단
        sort_state = [[], [], []]
        sorted_labels = [[], [], []]
        for i in range(3):
            sort_state[i] = sorted(state[i].items(), key=lambda item: item[1])
            sorted_labels[i] = [label[0] for label in sort_state[i]]

        # 수정 필요
        total_cnt = len(sorted_labels[0] + sorted_labels[1] + sorted_labels[2])

        if sorted_labels == [[], [], [1, 2, 3, 4]]:
            continue
        elif prev_state_labels == sorted_labels:
            cnt += 1
        else:
            prev_state_labels = sorted_labels
            cnt = 0

        # 약 1.5(50frame)초간 확인된 상태가 유지되면 타겟 상태로 이동
        if h.current_state_idx != -1 and cnt >= 50 and total_cnt == 4:
            prev_state_labels = []
            print(f"a:{sorted_labels[0]}\nb:{sorted_labels[1]}\nc:{sorted_labels[2]}")
            print(h.current_state_idx)

            current_state = [sorted_labels[0], sorted_labels[1], sorted_labels[2]]
            h.invade_state(current_state)
            processState = h.state_history[h.current_state_idx + 1]
            pole = ord(processState[3][1]) - ord('A')
            disk = processState[pole][0] if processState[pole] else None
            if disk:
                cm.moveArmWithCoord(disk, coordinates[h.current_state_idx])
