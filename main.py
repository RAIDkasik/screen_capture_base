from utils.grabbers.mss import Grabber

from utils.fps import FPS

from utils.win32 import WinHelper
import keyboard

import cv2
import multiprocessing


# CONFIG
GAME_WINDOW_TITLE = "Counter-Strike 2"  # window game
ACTIVATION_HOTKEY = 58  # https://snipp.ru/handbk/scan-codes
_show_cv2 = True

# used by the script
game_window_rect = WinHelper.GetWindowRect(GAME_WINDOW_TITLE, (8, 30, 16, 39))  # cut the borders
_activated = False


def grab_process(q):
    grabber = Grabber()

    while True:
        img = grabber.get_image({"left": int(game_window_rect[0]), "top": int(game_window_rect[1]), "width": int(game_window_rect[2]), "height": int(game_window_rect[3])}) #screen

        if img is None:
            continue

        q.put_nowait(img)
        q.join()


def cv2_process(q):
    global _show_cv2, game_window_rect

    fps = FPS()
    font = cv2.FONT_HERSHEY_SIMPLEX

    # mouse = MouseControls()

    while True:
        if not q.empty():
            img = q.get_nowait()
            q.task_done()

            if _show_cv2:
                img = cv2.putText(img, f"{fps():.2f}", (20, 120), font, 1.7, (0, 255, 0), 7, cv2.LINE_AA)

                img = cv2.resize(img, (1280, 720))
                cv2.imshow("Output", img)
                cv2.waitKey(1)


def switch_shoot_state(triggered, hotkey):
    global _activated
    _activated = not _activated  # inverse value


keyboard.add_hotkey(ACTIVATION_HOTKEY, switch_shoot_state, args=('triggered', 'hotkey'))


if __name__ == "__main__":

    q = multiprocessing.JoinableQueue()

    p1 = multiprocessing.Process(target=grab_process, args=(q,))
    p2 = multiprocessing.Process(target=cv2_process, args=(q,))

    p1.start()
    p2.start()