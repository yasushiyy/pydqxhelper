# -*- coding: UTF-8 -*-
#

import os
import sys
import cv2
import numpy as np
from PIL import ImageGrab
from time import sleep
from random import randint
from win32api import keybd_event
from win32con import KEYEVENTF_KEYUP, VK_MENU, VK_SNAPSHOT
from win32gui import GetWindowText, GetForegroundWindow
from win32clipboard import OpenClipboard, CloseClipboard, EmptyClipboard
from pywinauto.SendKeysCtypes import SendKeys # SendInput対応

class DQXHelper():
    """ メインクラス """

    """ 初期化 """
    def __init__(self, debug=False):
        # パターンマッチテーブル
        # (画像, (元画像検索範囲ymin, ymax, xmin, xmax), (ターゲット座標y, x), 自信度)
        self.tbl = {}
        self.tbl['Attack1']  = (self.img('attack.png'),   (250, 360,   0, 150), (330,  57), 0.5) # こうげき
        self.tbl['Attack2']  = (self.img('attack.png'),   (250, 360,   0, 150), (319,  50), 0.5) # こうげき
        self.tbl['Hissatsu'] = (self.img('hissatsu.png'), (250, 360,   0, 150), (300,  48), 0.4) # ひっさつ
        self.tbl['Field']    = (self.img('field.png'),    (300, 480,   0, 240), (319,  29), 0.2) # 小マップ
        self.tbl['Menu']     = (self.img('menu.png'),     (400, 480, 500, 640), (422, 568), 0.3) # HP/MP
        self.tbl['Gold']     = (self.img('gold.png'),     (  0, 100, 500, 640), ( 66, 594), 0.5) # G
        self.tbl['LongMenu'] = (self.img('longmenu.png'), (400, 480,   0, 640), (468,  42), 0.2) # 画面下部バー
        self.tbl['Chest']    = (self.img('chest.png'),    (  0, 100,   0, 150), ( 63,  46), 0.5) # たからばこ
        self.tbl['Person']   = (self.img('person.png'),   (  0, 100, 200, 400), ( 63, 243), 0.5) # 対人メニュー
        self.tbl['YesNo']    = (self.img('yesno.png'),    (300, 400, 400, 640), (325, 499), 0.5) # はい・いいえ
        self.debug = debug
        # GUI指定オプション
        self.gui_b_loop = True
        self.gui_b_field = False
        self.gui_b_battle_ini = False
        self.gui_b_battle_end = False
        self.gui_field_command = ''
        self.gui_battle_command = ''

    """ テンプレート読み込み """
    def img(self, f):
        return cv2.imread(os.path.join('template', f), cv2.CV_LOAD_IMAGE_GRAYSCALE)

    """ スクリーンショットのキャプチャ """
    def capture(self):
        # 前回のキャプチャをクリア
        OpenClipboard()
        EmptyClipboard()
        CloseClipboard()
        # Alt+PrintScreen (高速化のため直接イベント送信)
        keybd_event(VK_MENU, 0, 0, 0)
        keybd_event(VK_SNAPSHOT, 0, 0, 0)
        keybd_event(VK_SNAPSHOT, 0, KEYEVENTF_KEYUP, 0)
        keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
        img_capt = None
        img_capt_count = 0
        while not img_capt:
            img_capt = ImageGrab.grabclipboard()
            img_capt_count = img_capt_count + 1
            if img_capt_count > 10:
                # capture failed
                img_capt = None
                break
            sleep(0.05)
        if img_capt:
            img_orig = np.array(img_capt)[:, :, ::-1]  # RGB->BGR
        else:
            img_orig = None
        return img_orig

    """ グレースケール化、平滑化、二値化 """
    def transform(self, img_orig):
        img_gray = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (1, 1), 0)
        img_proc = cv2.adaptiveThreshold(img_blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        #img_proc = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        if self.debug:
            tmpdir = 'c:\\temp\\'
            cv2.imwrite(tmpdir + 'orig.png', img_orig)
            cv2.imwrite(tmpdir + 'gray.png', img_gray)
            cv2.imwrite(tmpdir + 'blur.png', img_blur)
            cv2.imwrite(tmpdir + 'proc.png', img_proc)
            cv2.imwrite(tmpdir + 'attack1.png', img_proc[329:347, 56:130])
            cv2.imwrite(tmpdir + 'attack2.png', img_proc[319:337, 50:121])
            cv2.imwrite(tmpdir + 'hissatsu.png', img_proc[300:322, 48:125])
            cv2.imwrite(tmpdir + 'field.png', img_proc[319:475, 29:200])
            cv2.imwrite(tmpdir + 'menu.png', img_proc[422:460, 568:583])
            cv2.imwrite(tmpdir + 'gold.png', img_proc[66:85, 594:608])
            cv2.imwrite(tmpdir + 'longmenu.png', img_proc[468:480, 42:600])
            cv2.imwrite(tmpdir + 'chest.png', img_proc[63:83, 46:143])
            cv2.imwrite(tmpdir + 'person.png', img_proc[63:84, 243:318])
            cv2.imwrite(tmpdir + 'yesno.png', img_proc[325:371, 499:560])
            print 'Saved',
        return img_proc

    """ パターンマッチング
        TM_CCOEFF_NORMEDはmaxLoc、SQDIFFはminLocがベストマッチ """
    def find_match(self, img_proc, entry_name):
        # マッチテーブル読み込み
        entry = self.tbl[entry_name]
        img_part = entry[0]
        (ymin, ymax, xmin, xmax) = entry[1]
        ytgt = entry[2][0] - ymin
        xtgt = entry[2][1] - xmin
        confid = entry[3]
        img_all = img_proc[ymin:ymax, xmin:xmax]
        # サイズチェック
        if img_all.shape[0] < img_part.shape[0] or img_all.shape[1] < img_part.shape[1]:
            # キャプチャ失敗？
            print 'ERROR: Bad Capture.'
            return 0
        # マッチング
        result = cv2.matchTemplate(img_part, img_all, cv2.TM_CCOEFF_NORMED)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
        (x, y) = maxLoc
        #(y, x) = np.unravel_index(result.argmax(), result.shape)
        if self.debug:
            print '/ Confid:', round(maxVal, 3), '/ Actual:', (y, x), '/ Target:', (ytgt, xtgt)
        # 評価
        if maxVal > confid and abs(y - ytgt) < 10 and abs(x - xtgt) < 10:
            # 自信度が指定値以上、かつx/yが指定値と10ピクセル以上ずれていない
            return round(maxVal, 1)
        else:
            return 0

    """ デバッグモード """
    def debug_mode(self, img_proc):
        names = self.tbl.keys()
        names.sort()
        for name in names:
            if self.debug:
                print '/ Name:', name,
            confid = self.find_match(img_proc, name)
            if confid > 0:
                print '{0}({1})'.format(name, confid),
        print ''

    """ コマンド実行 """
    def exec_command(self, name):
        if name == 'mantan':
            # 「まんたん」（フィールド）
            SendKeys('{F11}')
            SendKeys('{LEFT}{UP}', 0.1)
            SendKeys('{ENTER}{ENTER}', 0.3)
            SendKeys('{ESC}{ESC}{ESC}', 0.1)
            print 'Command(mantan)'
        elif name == 'hissatsu':
            # 「ひっさつ」（戦闘）
            SendKeys('{UP}')
            SendKeys('{ENTER}{ENTER}{ENTER}', 0.3)
            print 'Command(hissatsu)'
        elif name == 'attack':
            # 「こうげき」 （戦闘）
            SendKeys('{ENTER}{ENTER}', 0.3)
            print 'Command(attack)'
        elif name == 'spell':
            # 「じゅもん」（戦闘）
            SendKeys('{DOWN}')
            SendKeys('{ENTER}{ENTER}{ENTER}', 0.3)
            print 'Command(spell)'
        elif name == 'tokugi':
            # 「とくぎ」（戦闘）
            SendKeys('{DOWN}{DOWN}', 0.1)
            SendKeys('{ENTER}{ENTER}{ENTER}', 0.3)
            print 'Command(tokugi)'

    """ フィールドモード """
    def field_mode(self, bcommand):
        print 'Field Mode', bcommand
        b_battle_ini = True
        b_battle_end = False
        count5 = 5
        while self.gui_b_loop:
            # ゲーム画面がアクティブ
            if GetWindowText(GetForegroundWindow()).decode('SJIS').startswith(u'ドラゴンクエスト'):
                # 5回毎にカメラリセット
                count5 = count5 - 1
                if count5 == 0:
                    SendKeys('{F12}')
                    count5 = 5
                # 画像処理
                img_orig = self.capture()
                if img_orig is None:
                    print 'ERROR: Capture Failed.'
                    sleep(0.5)
                    continue
                img_proc = self.transform(img_orig)
                # 分岐
                if self.find_match(img_proc, 'Person'):
                    # 対人メニューが表示されている場合、最優先でキャンセル
                    SendKeys('{ESC}')
                    print 'Person(ESC)'
                else:
                    # フィールド、戦闘中、その他の判断
                    b_match_field = self.find_match(img_proc, 'Field')
                    b_match_menu = self.find_match(img_proc, 'Menu')
                    if b_match_field:
                        # フィールド上（左下小マップ表示あり）
                        b_match_chest = self.find_match(img_proc, 'Chest')
                        if self.gui_b_battle_end and b_battle_end and not b_match_chest and not b_match_menu:
                            # 戦闘終了時まんたん（GUIから）
                            # 宝箱なし、HP/MPメニューなし、行動可能
                            print 'BattleEnd ->',
                            self.exec_command('mantan')
                            b_battle_end = False
                        elif self.gui_b_field:
                            # 禁止されてなければ分岐（GUIから）
                            print 'Field ->',
                            if b_match_chest:
                                # 宝箱を開いている場合、ゲット
                                SendKeys('{ENTER}')
                                print 'GetItem(ENTER)'
                            elif b_match_menu:
                                # HP/MPが表示されている場合、キャンセル
                                SendKeys('{ESC}')
                                print 'Menu(ESC)'
                            elif b_battle_end:
                                # 戦闘終了直後（かつまんたん未実施）の場合、誤動作を防ぐため待機
                                print 'BattleEnd(Sleep)'
                                sleep(5)
                                b_battle_end = False
                            elif self.gui_field_command:
                                # フィールド割り込みコマンド（GUIから）
                                print'Interrupt',
                                self.exec_command(self.gui_field_command)
                                self.gui_field_command = ''
                            else:
                                # ENTERで何かActivateしてみる
                                SendKeys('{ENTER}')
                                print 'Else(ENTER)'
                        else:
                            # 禁止されてるから何もしない
                            print 'x',
                    elif not b_match_field and b_match_menu:
                        # 戦闘中（左下小マップなし、HP/MP表示あり）
                        print 'Battle ->',
                        if self.find_match(img_proc, 'Hissatsu'):
                            # 「ひっさつ」
                            self.exec_command('hissatsu')
                        elif self.find_match(img_proc, 'Attack1'):
                            # 通常戦闘状態（こうげき～どうぐメニュー表示）
                            if self.gui_battle_command:
                                # 戦闘割り込みコマンド（GUIから）
                                print'Interrupt',
                                self.exec_command(self.gui_battle_command)
                                self.gui_battle_command = ''
                            elif self.gui_b_battle_ini and b_battle_ini:
                                # 初回行動時とくぎ（GUIから）
                                print 'BattleInit ->',
                                self.exec_command('tokugi')
                                b_battle_ini = False
                            else:
                                # 「こうげき」「じゅもん」「とくぎ」
                                self.exec_command(bcommand)
                        elif self.find_match(img_proc, 'Attack2'):
                            # 「こうげき」選択済み
                            # イレギュラー状態になるとここに来る可能性あり
                            SendKeys('{ENTER}')
                            print 'Attack2(ENTER)'
                        else:
                            # コマンド未表示なので何もしない
                            print 'x'
                        # 戦闘中なので、戦闘完了後行動フラグをたてる
                        b_battle_end = True
                    elif not b_match_field and not b_match_menu:
                        # その他（左下小マップ表示なし、HP/MP表示なし）
                        # 戦闘開始前後や、立て看板表示など
                        print 'Others ->',
                        if self.find_match(img_proc, 'LongMenu'):
                            # 画面下部メッセージがある場合、キャンセル
                            SendKeys('{ESC}')
                            print 'LongMenu(ESC)'
                        else:
                            # することがないので何もしない
                            print 'x'
                            # 戦闘開始前後なので、戦闘初回行動フラグをたてる
                            b_battle_ini = True
                    else:
                        # 未対応なので何もしない
                        print '?',
            else:
                # ゲーム画面が非アクティブなので何もしない
                print '.',
            # アイドル時間
            sleep(0.5)

    """ ループ停止・再開 """
    def set_gui_b_loop(self, val):
        self.gui_b_loop = val

    """ フィールド有効フラグ """
    def set_gui_b_field(self, val):
        self.gui_b_field = val

    """ 戦闘開始時とくぎ有効フラグ """
    def set_gui_b_battle_ini(self, val):
        self.gui_b_battle_ini = val

    """ 戦闘終了時まんたん有効フラグ """
    def set_gui_b_battle_end(self, val):
        self.gui_b_battle_end = val

    """ フィールド割り込みコマンド """
    def set_gui_field_command(self, val):
        self.gui_field_command = val

    """ 戦闘割り込みコマンド """
    def set_gui_battle_command(self, val):
        self.gui_battle_command = val

    """ メイン """
    def run(self, args):
        if not args:
            print 'Invalid option.'
        elif args[0] in ['attack', 'spell', 'tokugi']:
            # 「こうげき」「じゅもん」「とくぎ」でフィールドモード
            self.field_mode(args[0])
        elif args[0] == 'debug':
            # debugサブディレクトリ以下すべて読み込み
            print 'DEBUG: Reading all files'
            for filename in [f for f in os.listdir('debug') if f.endswith('.png')]:
                print 'DEBUG:', filename,
                img_orig = cv2.imread(os.path.join('debug', filename))
                img_proc = self.transform(img_orig)
                self.debug_mode(img_proc)
        elif args[0].endswith('.png'):
            # 指定ファイル読み込み（＋デバッグファイル出力）
            self.debug = True
            print 'DEBUG:', sys.argv[1]
            img_orig = cv2.imread(sys.argv[1])
            img_proc = self.transform(img_orig)
            print ''
            self.debug_mode(img_proc)

# 実行
if __name__ == '__main__':
    dqx = DQXHelper()
    dqx.run(sys.argv[1:])
