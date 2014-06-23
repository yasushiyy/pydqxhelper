# -*- coding: UTF-8 -*-
#
# debug用のスクリーンショット取得
#   > python pydqxcapture.py [output_file]
#

import cv2
import sys
from time import sleep
from datetime import datetime
from pydqxhelper import DQXHelper
from win32gui import GetWindowText, GetForegroundWindow

if __name__ == '__main__':
    # 出力ファイル名指定
    outfile = datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
    if len(sys.argv) > 1:
        outfile = sys.argv[1]

    # キャプチャ取得
    dqx = DQXHelper()
    img_orig = None
    while img_orig is None:
        print '.',
        if GetWindowText(GetForegroundWindow()).decode('SJIS').startswith(u'ドラゴンクエスト'):
            img_orig = dqx.capture()
            print 'OK'
        sleep(0.5)

    # 保存
    cv2.imwrite(outfile, img_orig)
    print 'Created:', outfile
