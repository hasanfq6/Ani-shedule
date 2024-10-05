from enimation import loading
from enimation.motions import dots_loading
import time

@loading(custom=dots_loading)
def long_task():
    time.sleep(5)

long_task()  # The dots_loading animation will play during the task
