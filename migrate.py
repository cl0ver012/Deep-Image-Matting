import keras.backend as K
import numpy as np

import new_start
from utils import do_compile
from vgg16 import vgg16_model


def do_migrate_model(img_rows, img_cols, channel=4):
    old_model = vgg16_model(224, 224, 3)
    #print(old_model.summary())
    old_layers = [l for l in old_model.layers]
    new_model = new_start.autoencoder(img_rows, img_cols, 4)
    new_layers = [l for l in new_model.layers]

    old_conv1_1 = old_model.get_layer('conv1_1')
    old_weights = old_conv1_1.get_weights()[0]
    old_biases = old_conv1_1.get_weights()[1]
    new_weights = np.zeros((3, 3, channel, 64), dtype=np.float32)
    new_weights[:, :, 0:3, :] = old_weights
    new_weights[:, :, 3:channel, :] = 0.0
    new_conv1_1 = new_model.get_layer('conv1_1')
    new_conv1_1.set_weights([new_weights, old_biases])

    for i in range(2, 31):
        old_layer = old_layers[i]
        new_layer = new_layers[i]
        new_layer.set_weights(old_layer.get_weights())

    # flatten = old_model.get_layer('flatten')
    # f_dim = flatten.input_shape
    # print('f_dim: ' + str(f_dim))
    # old_dense1 = old_model.get_layer('dense1')
    # input_shape = old_dense1.input_shape
    # output_dim = old_dense1.get_weights()[1].shape[0]
    # print('output_dim: ' + str(output_dim))
    # W, b = old_dense1.get_weights()
    # shape = (7, 7, 512, output_dim)
    # new_W = W.reshape(shape)
    # new_conv6 = new_model.get_layer('conv6')
    # new_conv6.set_weights([new_W, b])

    del old_model

    return new_model


def migrate_model(img_rows, img_cols, channel=4):
    # num_gpu = len(get_available_gpus())
    # if num_gpu >= 2:
    #     with tf.device("/cpu:0"):
    #         print("Training with {} GPUs...".format(num_gpu))
    #         new_model = do_migrate_model(img_rows, img_cols, channel)
    #         new_model = multi_gpu_model(new_model, gpus=num_gpu)
    # else:
    new_model = do_migrate_model(img_rows, img_cols, channel)
    new_model = do_compile(new_model)
    return new_model


if __name__ == '__main__':
    model = migrate_model(320, 320, 4)
    print(model.summary())
    model.save_weights('models/model_weights.h5')

    K.clear_session()
