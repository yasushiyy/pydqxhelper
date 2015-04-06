pydqxhelper.py
==============

## 概要
* DQ10の2アカ側操作ヘルパーです。
* 「ついていく」を前提に、各種コマンドの自動入力を行います。
* 自動移動は行いません。

## 注意事項
* 自動操作およびBOTは違反行為であり、本スクリプトも例外ではありません。
* あくまでこういったツールを作る上でのProof-of-Concept、サンプル実装として公開しています。
* 本スクリプトはそのままでは動きません。動かすためのいかなる手助けも提供しません。
* 他のBOTツールのほうが高機能ですので、そちらのご利用をご検討ください。

## インストール
* Python2.7.X をインストールします。
* 以下それぞれのサイトからモジュールをダウンロードします。32-bit版と64-bit版かは、Windowsに合わせます。
  * http://www.lfd.uci.edu/~gohlke/pythonlibs/
    * numpy
      * `> c:¥Python27¥Scripts¥pip.exe install numpy*.*`
    * opencv
      * `> c:¥Python27¥Scripts¥pip.exe install opencv*.*`
    * pywin32
      * `> c:¥Python27¥Scripts¥pip.exe install pywin32*.*`
      * c:¥python27¥lib¥site-packages¥pywin32-system32¥*.dllをc:¥python27¥lib¥site-packages¥win32にコピーします。
    * pillow
      * `> c:¥Python27¥Scripts¥pip.exe install pillow*.*`
  * http://code.google.com/p/pywinauto/ (32-bit Windowsの場合)、 https://github.com/vasily-v-ryabov/pywinauto-64 (64-bit Windowsの場合)
    * `> c:¥python27¥python.exe setup.py install`
  * キーコンフィグを調整します。
    * F11: メインウィンドウ
    * F12: カメラリセット

## 実行方法
* 640x480 低画質モードでゲームを起動します。
* pydqxgui.pywをダブルクリックして起動します。
* ゲーム画面ウィンドウをアクティブにします。
* 非アクティブにすると中断します。

## 起動オプション
スクリプト単体でも動きます。

```
> python pydqxhelper.py [attack|spell|tokugi|slot]
   - attack： フィールドモード（こうげきリピート）
   - spell ： フィールドモード（じゅもんリピート）
              起動前に実行した「じゅもん」をリピート
   - tokugi： フィールドモード（とくぎリピート）
              起動前に実行した「とくぎ」をリピート
   - slot  ： スロットゲームモード
```
