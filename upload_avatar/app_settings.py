# -*- coding: utf-8 -*-
import os

from django.conf import settings
PROJECT_PATH = settings.PROJECT_PATH


DEFAULT_AVATAR = 'default.png'


# where the uploaded image store, absolute path
UPLOAD_AVATAR_UPLOAD_ROOT = os.path.join(PROJECT_PATH, 'avatar')

# where the cropped avatar store, absolute path
UPLOAD_AVATAR_AVATAR_ROOT = os.path.join(PROJECT_PATH, 'avatar')


if not os.path.isdir(UPLOAD_AVATAR_UPLOAD_ROOT):
    os.mkdir(UPLOAD_AVATAR_UPLOAD_ROOT)
if not os.path.isdir(UPLOAD_AVATAR_AVATAR_ROOT):
    os.mkdir(UPLOAD_AVATAR_AVATAR_ROOT)


# URL prefix for the original uploaded image
# e.g. uploadedimage/ or image/ ...
UPLOAD_AVATAR_URL_PREFIX_ORIGINAL = '/static/avatar/'

# URL prefix for the cropped, real avatar
# e.g. avatar/
UPLOAD_AVATAR_URL_PREFIX_CROPPED = '/static/avatar/'

# Yes, you noticed there are two URLs,
# URL_PREFIX_ORIGINAL just used after user upload an image,
# and the web will shown the uploaded image for select the crop area.
#
# URL_PREFIX_CROPPED is actually  used for user avatar


# Default max allowed size is 3MB
UPLOAD_AVATAR_MAX_SIZE = 1024 * 1024 * 3


UPLOAD_AVATAR_RESIZE_SIZE = 50


# Avatar format, you can also choose: jpep, gif...
UPLOAD_AVATAR_SAVE_FORMAT = 'png'

UPLOAD_AVATAR_SAVE_QUALITY = 90


# Whethe delete the uploaded original image after avatar cropped, default is True
UPLOAD_AVATAR_DELETE_ORIGINAL_AFTER_CROP = True


