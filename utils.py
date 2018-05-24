import multiprocessing

import cv2 as cv
import keras.backend as K
import numpy as np
from tensorflow.python.client import device_lib

from config import img_cols
from config import img_rows


# simple alpha prediction loss
def custom_loss(y_true, y_pred):
    trimap = y_true[:, :, :, 1]
    mask = K.cast(K.equal(trimap, 128 / 255.), dtype='float32')
    diff = (y_pred - y_true)[:, :, :, 0]
    diff *= mask
    num_pixels = K.sum(mask)
    epsilon = 1e-6
    epsilon_sqr = epsilon ** 2
    return K.sum(K.sqrt(K.square(diff) + epsilon_sqr)) / (num_pixels + epsilon)


def custom_loss_wrapper(input_tensor):
    def custom_loss(y_true, y_pred):
        trimap = input_tensor[:, :, :, 3]
        mask = K.cast(K.equal(trimap, 128 / 255.), dtype='float32')
        diff = (y_pred - y_true)[:, :, :, 0]
        diff *= mask
        num_pixels = K.sum(mask)
        epsilon = 1e-6
        epsilon_sqr = epsilon ** 2
        return K.sum(K.sqrt(K.square(diff) + epsilon_sqr)) / (num_pixels + epsilon)

    return custom_loss


# getting the number of GPUs
def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']


# getting the number of CPUs
def get_available_cpus():
    return multiprocessing.cpu_count()


def get_final_output(out, trimap):
    known = trimap.copy()
    known[known == 128] = 0
    unknown_mask = trimap.copy()
    unknown_mask[unknown_mask != 128] = 0
    unknown_mask[unknown_mask == 128] = 1
    return known + unknown_mask * out


def safe_crop(mat, x, y, crop_size=(320, 320)):
    crop_height, crop_width = crop_size
    if len(mat.shape) == 2:
        ret = np.zeros((crop_height, crop_width), np.float32)
    else:
        ret = np.zeros((crop_height, crop_width, 3), np.float32)
    crop = mat[y:y + crop_height, x:x + crop_width]
    h, w = crop.shape[:2]
    ret[0:h, 0:w] = crop
    if crop_size != (320, 320):
        ret = cv.resize(ret, dsize=(img_rows, img_cols), interpolation=cv.INTER_NEAREST)
    return ret


def draw_str(dst, target, s):
    x, y = target
    cv.putText(dst, s, (x + 1, y + 1), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness=2, lineType=cv.LINE_AA)
    cv.putText(dst, s, (x, y), cv.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv.LINE_AA)


def compute_mse_loss(pred, target, trimap):
    error_map = (pred - target) / 255.
    unknown = (trimap == 128).astype(np.float32)
    print('unknown: ' + str(unknown))
    loss = np.sum(np.square(error_map) * unknown) / np.sum(unknown)
    print('mse_loss: ' + str(loss))
    return loss


def compute_sad_loss(pred, target, trimap):
    error_map = np.abs(pred - target) / 255.
    unknown = (trimap == 128).astype(np.float32)
    loss = np.sum(error_map * unknown)
    loss = loss / 1000
    print('sad_loss: ' + str(loss))
    return loss
