import datetime
import os
import pathlib
import time

import numpy as np
import tensorflow as tf
from IPython import display
from matplotlib import pyplot as plt
from PIL import Image

img_width = 256
img_height = 256


def decode(filters, size, apply_dropout=False):
    initializer = tf.random_normal_initializer(0, 0.02)
    result = tf.keras.Sequential()
    result.add(tf.keras.layers.Conv2DTranspose(filters, size, strides=2, padding='same',
                                               kernel_initializer=initializer, use_bias=False))
    result.add(tf.keras.layers.BatchNormalization())

    if apply_dropout:
        result.add(tf.keras.layers.Dropout(0.5))

    result.add(tf.keras.layers.ReLU())

    return result


def encode(filters, size, apply_batchnorm=True):
    initializer = tf.random_normal_initializer(0, 0.02)
    result = tf.keras.Sequential()
    result.add(tf.keras.layers.Conv2D(filters, size, strides=2, padding='same',
                                      kernel_initializer=initializer, use_bias=False))
    if apply_batchnorm:
        result.add(tf.keras.layers.BatchNormalization())
    result.add(tf.keras.layers.LeakyReLU())
    return result


def Generator():
    inputs = tf.keras.layers.Input(shape=[256, 256, 3])

    downsampling = [
        encode(64, 4, apply_batchnorm=False),  # (batch_size, 128, 128, 64)
        encode(128, 4),  # (batch_size, 64, 64, 128)
        encode(256, 4),  # (batch_size, 32, 32, 256)
        encode(512, 4),  # (batch_size, 16, 16, 512)
        encode(512, 4),  # (batch_size, 8, 8, 512)
        encode(512, 4),  # (batch_size, 4, 4, 512)
        encode(512, 4),  # (batch_size, 2, 2, 512)
        encode(512, 4),  # (batch_size, 1, 1, 512)
    ]

    upsampling = [
        decode(512, 4, apply_dropout=True),  # (batch_size, 2, 2, 512)
        decode(512, 4, apply_dropout=True),  # (batch_size, 4, 4, 512)
        decode(512, 4, apply_dropout=True),  # (batch_size, 8, 8, 512)
        decode(512, 4),  # (batch_size, 16, 16, 512)
        decode(256, 4),  # (batch_size, 32, 32, 256)
        decode(128, 4),  # (batch_size, 64, 64, 128)
        decode(64, 4),  # (batch_size, 128, 128, 64)
    ]

    output_channels = 3
    initializer = tf.random_normal_initializer(0., 0.02)
    last = tf.keras.layers.Conv2DTranspose(output_channels, 4, strides=2, padding='same',
                                           kernel_initializer=initializer, activation='tanh')  # (batch_size, 256, 256, 3)

    x = inputs
    skips = []
    for down in downsampling:
        x = down(x)
        skips.append(x)

    skips = reversed(skips[:-1])

    for up, skip in zip(upsampling, skips):
        x = up(x)
        x = tf.keras.layers.Concatenate()([x, skip])

    x = last(x)

    return tf.keras.Model(inputs=inputs, outputs=x)


model2 = Generator()


def make_prediction(path, kind):
    original_img, transformed_img = load_testing_images(path, False)
    original_img = tf.expand_dims(original_img, axis=0)
    transformed_img = tf.expand_dims(transformed_img, axis=0)
    dataset = 'facades_b_w'
    model2.load_weights('./models/{}/model_pix2pix.h5'.format(dataset))
    generate_image = model2(original_img, training=True)
    return generate_image


def load_testing_images(img_file, transform_og_image=True):

    original_img, transformed_img = load_image(img_file, transform_og_image)
    original_img, transformed_img = resize(
        original_img, transformed_img, img_width, img_height)
    original_img, transformed_img = normalize(original_img, transformed_img)
    return original_img, transformed_img


def resize(original_img, transformed_img, width, height):
    original_img = tf.image.resize(
        original_img, [width, height], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    transformed_img = tf.image.resize(
        transformed_img, [width, height], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    return original_img, transformed_img


def normalize(original_img, transformed_img):
    original_img = (original_img / 127.5) - 1
    transformed_img = (transformed_img / 127.5) - 1
    return original_img, transformed_img


def load_image(img_file, transform_og_image=True):
    img = tf.io.read_file(img_file)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)

    if (transform_og_image):
        img = tf.image.resize(img, [256, 512])
    else:
        img = tf.image.resize(img, [256, 256])

    width = tf.shape(img)[1] // 2
    transformed_img = img[:, :width, :]

    if (transform_og_image):
        original_img = img[:, width:, :]
    else:
        original_img = img

    # Convert original image to grayscale
    original_gray = rgb2gray(original_img)

    # Invert the grayscale image
    inverted_img = invert_colors(original_gray)

    # Apply blurring to the inverted image
    blurred_img = blur_image(inverted_img)

    # Create pencil sketch by blending the original grayscale image with the inverted blurred image
    pencil_sketch = blend(original_gray, blurred_img)

    # Convert pencil_sketch to a 3-channel image
    pencil_sketch_3_channel = tf.image.grayscale_to_rgb(pencil_sketch)

    # Cast to float32
    transformed_img = tf.cast(transformed_img, tf.float32)
    pencil_sketch_3_channel = tf.cast(pencil_sketch_3_channel, tf.float32)

    return pencil_sketch_3_channel, transformed_img


def rgb2gray(rgb):
    return tf.image.rgb_to_grayscale(rgb)


def invert_colors(img):
    return 255 - img


def blur_image(img, size=3):
    # Add a batch dimension to the image
    img = tf.expand_dims(img, axis=0)
    # Use average pooling to blur the image
    blurred_img = tf.nn.avg_pool2d(img, ksize=[1, size, size, 1], strides=[
                                   1, 1, 1, 1], padding='SAME')
    # Remove the batch dimension from the image
    blurred_img = tf.squeeze(blurred_img, axis=0)
    return blurred_img


def blend(original, mask):
    # Ensure that the original and mask images have the same shape
    mask = tf.image.resize(mask, tf.shape(original)[
                           0:2], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    return (original * (255 - mask) + (255 * mask)) / 255
