import argparse

import cv2 as cv
import keras.backend as K
import numpy as np

from new_start import autoencoder
from utils import generate_trimap
from utils import get_crop_top_left

if __name__ == '__main__':
    img_rows, img_cols = 320, 320
    channel = 4

    model_weights_path = 'models/model.06-0.02.hdf5'
    model = autoencoder(img_rows, img_cols, channel)
    model.load_weights(model_weights_path)
    print(model.summary())

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", help="path to the image file")
    ap.add_argument("-t", "--alpha", help="path to the alpha file")
    args = vars(ap.parse_args())
    image = args["image"]
    alpha = args["alpha"]

    if image is None:
        image = 'images/0_0.png'
        alpha = 'images/035A4301.jpg'

    print('Start processing image: {}'.format(image))

    x_test = np.empty((1, img_rows, img_cols, 4), dtype=np.float32)
    bgr_img = cv.imread(image)
    bg_h, bg_w = bgr_img.shape[:2]
    print(bg_h, bg_w)
    a = cv.imread(alpha, 0)
    a_h, a_w = a.shape[:2]
    print(a_h, a_w)
    alpha = np.zeros((bg_h, bg_w), np.float32)
    alpha[0:a_h, 0:a_w] = a
    trimap = generate_trimap(alpha)
    x, y = get_crop_top_left(trimap)
    print(x, y)
    bgr_img = bgr_img[y:y + 320, x:x + 320]
    alpha = alpha[y:y + 320, x:x + 320]
    trimap = trimap[y:y + 320, x:x + 320]
    cv.imwrite('images/image.png', bgr_img)
    cv.imwrite('images/trimap.png', trimap)
    cv.imwrite('images/alpha.png', alpha)

    x_test = np.empty((1, 320, 320, 4), dtype=np.float32)
    x_test[0, :, :, 0:3] = bgr_img / 255.
    x_test[0, :, :, 3] = trimap / 255.

    out = model.predict(x_test)
    out = np.reshape(out, (img_rows, img_cols))
    print(out.shape)
    out = out * 255.0
    out = out.astype(np.uint8)
    cv.imshow('out', out)
    cv.imwrite('images/out.png', out)
    cv.waitKey(0)
    cv.destroyAllWindows()

    K.clear_session()
