import _init_paths
from utils import to_categorical_4d, to_categorical_4d_reverse
from FCN import FCN8
import tensorflow as tf
import numpy as np
import ear_pen
import math
import cv2

batch_size = 2
model_store_path = '../model/FCN-8/FCN-8.ckpt'

if __name__ == '__main__':
    img_ph = tf.placeholder(tf.float32, [None, 104, 78, 3])
    ann_ph = tf.placeholder(tf.int32, [None, 104, 78, 1])
    net = FCN8(img_ph, ann_ph)

    # Load data
    (train_img, train_ann), (test_img, test_ann) = ear_pen.load_data()
    # test_ann = np.asarray(test_ann) / 255
    test_ann, _map = to_categorical_4d(test_ann)

    # Test
    saver = tf.train.Saver()
    loss_list = []
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess, model_store_path)
        loss_sum = 0
        for i in range(math.ceil(len(test_img) / batch_size)):
            feed_dict = {
                img_ph: test_img[i*batch_size: i*batch_size+batch_size],
                ann_ph: test_ann[i*batch_size: i*batch_size+batch_size] 
            }
            _loss, _pred= sess.run([net.loss, net.prediction], feed_dict=feed_dict)
            loss_sum += _loss
        loss_list.append(loss_sum)
        print('test loss: ', loss_sum)
    _pred = np.asarray(to_categorical_4d_reverse(_pred, _map)[:, :, :, :], dtype=np.uint8) * 255
    # show_img = np.concatenate((test_img[0], test_img[1]), axis=1)

    test_ann = to_categorical_4d_reverse(test_ann, _map)
    show_img = np.concatenate((test_ann[0], test_ann[1]), axis=1)
    # show_img = np.concatenate((_, show_img), axis=0)
    print(np.shape(show_img))
    print(np.shape(np.concatenate((_pred[0], _pred[1]), axis=1)))
    show_img = np.concatenate((show_img, np.concatenate((_pred[0], _pred[1]), axis=1)), axis=0)
    print(np.shape(show_img))
    cv2.imshow('res', show_img)
    cv2.waitKey(0)
