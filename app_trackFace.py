import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import mediapipe as mp
import numpy as np
from utils import mediapipe_detection, draw_landmarks, draw_landmarks_custom, draw_limit_rh, draw_limit_lh, check_detection
from argparse import ArgumentParser
#from facial_landmarks import FaceLandmarks

class FaceLandmarks:
    def __init__(self):
        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(max_num_faces=6, min_detection_confidence=0.2)


    def get_facial_landmarks(self, frame):
        height, width, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(frame_rgb)

        facelandmarks = []
        for facial_landmarks in result.multi_face_landmarks:
            for i in range(0, 468):
                pt1 = facial_landmarks.landmark[i]
                x = int(pt1.x * width)
                y = int(pt1.y * height)
                facelandmarks.append([x, y])


        return np.array(facelandmarks, np.int32)

parser = ArgumentParser()
parser.add_argument("-a", "--area", dest="active_area", default=1.2,
                    help="Active area for tracking", type=float)
parser.add_argument("-s", "--smooth", dest="average_smooth", default=60, type=int,
                    help="Smooth tracking taking average position last N points. Default is 60.")
parser.add_argument("-ow", "--output_width", dest="preferred_width", default=1280, type=int,
                    help="Width of the image. Default value is 1280px.")
parser.add_argument("-oh", "--output_height", dest="preferred_height", default=720, type=int,
                    help="Height of the image. Default value is 720px.")
parser.add_argument("-c", "--camera_id", dest="camera_id", default=1, type=int,
                    help="Select camera device ID. An integer from 0 to N.")
args = parser.parse_args()

index = 0
arr = []
while True:
    cap = cv2.VideoCapture(index)
    if not cap.read()[0]:
        break
    else:
        arr.append(index)
    cap.release()
    index += 1

print('------------------------------------')
print('Devices')
print('------------------------------------')
print(arr)
print()

# width_cropped = width_out
# height_cropped = height_out
media_mobile = args.average_smooth

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
#drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

baricentro_x = []
baricentro_y = []

vc = cv2.VideoCapture(args.camera_id)

if not vc.isOpened():
    raise RuntimeError('Could not open video source')

print('-- Camera Settings -----------------------------------')
print(f'Device ID: {args.camera_id}')
print()


print('-- Camera Settings -----------------------------------')
print(f'Height: {int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))}')
print(f'Width: {int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))}')
print(f'FPS: {int(vc.get(cv2.CAP_PROP_FPS))}')
print()

pref_width = args.preferred_width
pref_height = args.preferred_height
pref_fps = 30

vc.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
vc.set(cv2.CAP_PROP_FPS, pref_fps)

# Query final capture device values
# (may be different from preferred settings)
width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = vc.get(cv2.CAP_PROP_FPS)

print('-- Original Output Settings -----------------------------------')
print(f'Height: {height}')
print(f'Width: {width}')
print(f'FPS: {int(fps)}')
print()

# with mp_holistic.Holistic(
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5) as holistic:

zoom_scale = args.active_area
width_out = int(width/zoom_scale)
height_out = int(height/zoom_scale)

start_x = 0
start_y = 0
stop_x = width_out
stop_y = height_out

print('-- Output Settings -----------------------------------')
print(f'Height: {height_out}')
print(f'Width: {width_out}')
print(f'Active Area: {round(1/zoom_scale,2)}%')
print()



with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

    # with pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR) as cam:
    with pyvirtualcam.Camera(width_out, height_out, fps, fmt=PixelFormat.BGR) as cam:
        print()
        print('Virtual camera device: ' + cam.device)
        print()

        while True:
            ret, image = vc.read()
            fl = FaceLandmarks()

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(image)

            # calculate height and width.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    # blur = []
                    # for i in range(0, 468):
                    #     pt1 = face_landmarks.landmark[i]
                    #     x = int(pt1.x * width)
                    #     y = int(pt1.y * height)
                    #     blur.append([x, y])
                    # blur = np.array(blur, np.int32)
                    # convexhull = cv2.convexHull(blur)
                    #
                    # h, w = image.shape[:2]
                    # mask = np.zeros((h, w), np.uint8)
                    #
                    # cv2.fillConvexPoly(mask, convexhull, 255)
                    #
                    # image_copy = cv2.blur(image, (27, 27))
                    # face_extracted = cv2.bitwise_and(image_copy, image_copy, mask=mask)
                    #
                    # mask = (255-mask)
                    # background_mask = cv2.bitwise_not(mask)
                    # background = cv2.bitwise_and(image, image, mask=background_mask)
                    # image = cv2.add(background, face_extracted)

                    x_face_min = face_landmarks.landmark[234].x
                    y_face_min = face_landmarks.landmark[234].y

                    x_face_max = face_landmarks.landmark[447].x
                    y_face_max = face_landmarks.landmark[447].y

                    x_face = int((x_face_max + x_face_min)/2*width)
                    y_face = int((y_face_max + y_face_min)/2*height)

                    baricentro_x.append(x_face)
                    baricentro_y.append(y_face)

                    smooth = len(baricentro_x)
                    if smooth > media_mobile:
                        del baricentro_x[0]
                        del baricentro_y[0]
                        x_face = int(sum(baricentro_x)/media_mobile)
                        y_face = int(sum(baricentro_y)/media_mobile)
                    else:
                        x_face = int(sum(baricentro_x)/smooth)
                        y_face = int(sum(baricentro_y)/smooth)

                    if y_face - height_out/2 < 0:
                        start_y = 0
                        stop_y = height_out
                    elif y_face + height_out/2 > height:
                        start_y =  height - height_out
                        stop_y = height
                    else:
                        start_y = y_face-height_out/2
                        stop_y = y_face+height_out/2

                    if x_face - width_out/2 < 0:
                        start_x = 0
                        stop_x = width_out
                    elif x_face + width_out/2 > width:
                        start_x = width - width_out
                        stop_x = width
                    else:
                        start_x = x_face - width_out/2
                        stop_x = x_face + width_out/2

                    image_crop = image[int(start_y):int(stop_y), int(start_x):int(stop_x), :]

            else:
                image_crop = image[int(start_y):int(stop_y), int(start_x):int(stop_x), :]

            cv2.imshow('check video2', image_crop)          # Scommenta per testare
            cam.send(image_crop)
            cam.sleep_until_next_frame()
            # if cv2.waitKey(1) == ord('q'):
            #     print("Quit system")
            #     break
            # if cv2.waitKey(1) == ord('z'):
            #     tracking = False
            #     print("Tracking OFF")                      # To be done
            # if cv2.waitKey(1) == ord('x'):
            #     tracking = True
            #     print("Tracking ON")                       # To be done
