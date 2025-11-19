"""Initializes package mongo-s3-archiver (fork of mongodump-s3)."""

from .s3 import S3
from .dump import MongoDump
from .notifications import Notifications

__version__ = '0.1.0'
__author__ = 'Vladislav I. Kulbatski'
__maintainer__ = 'Hadi Koubeissy'
__all__ = ['MongoDump', 'S3', 'Notifications', '__version__']
