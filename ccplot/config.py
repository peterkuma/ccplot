import os
import sys

if os.path.exists(os.path.join(os.path.dirname(__file__), '../../../../share/ccplot/')):
    sharepath = os.path.join(os.path.dirname(__file__), '../../../../share/ccplot/')
elif os.path.exists(os.path.join(os.path.dirname(__file__), '../../../share/ccplot/')):
    sharepath = os.path.join(os.path.dirname(__file__), '../../../share/ccplot/')
else:
    sharepath = os.path.join(sys.prefix, 'share/ccplot/')
