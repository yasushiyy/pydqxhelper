# -*- coding: UTF-8 -*-
#

import sys
import threading
import Tkinter as tk
import Queue
from pydqxhelper import DQXHelper

class GUI(tk.Tk):
    def __init__(self, master):
        self.f = tk.Frame(master, bg='white')
        self.f.pack_propagate(0) # don't shrink
        self.f.pack()
        self.gui_b_field = tk.BooleanVar()
        self.gui_b_field.set(False)
        self.gui_b_battle_ini = tk.BooleanVar()
        self.gui_b_battle_ini.set(False)
        self.gui_b_battle_end = tk.BooleanVar()
        self.gui_b_battle_end.set(False)
        b1 = tk.Button(self.f, text=u'こうげき', command=self.attack, bg='oldlace')
        b2 = tk.Button(self.f, text=u'じゅもん', command=self.spell, bg='oldlace')
        b3 = tk.Button(self.f, text=u'とくぎ', command=self.tokugi, bg='oldlace')
        b4 = tk.Button(self.f, text=u'スロット', command=self.slot, bg='oldlace')
        b5 = tk.Button(self.f, text=u'とまれ', command=self.stop, fg='red', bg='oldlace')
        c1 = tk.Checkbutton(self.f, text=u'フィールドでのループ有効', variable=self.gui_b_field, bg='white')
        c2 = tk.Checkbutton(self.f, text=u'戦闘開始時とくぎ', variable=self.gui_b_battle_ini, bg='white')
        c3 = tk.Checkbutton(self.f, text=u'戦闘終了時まんたん', variable=self.gui_b_battle_end, bg='white')
        t1 = tk.Text(self.f, wrap='word', width=30, height=7)
        sys.stdout = StdoutRedirector(t1)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=0, column=2)
        b4.grid(row=0, column=3)
        b5.grid(row=0, column=4)
        c1.grid(row=1, column=0, columnspan=5, sticky=tk.W)
        c2.grid(row=2, column=0, columnspan=5, sticky=tk.W)
        c3.grid(row=3, column=0, columnspan=5, sticky=tk.W)
        t1.grid(row=0, column=5, rowspan=5, sticky=tk.W, padx=2)
        self.queue = Queue.Queue()
        self.running = False

    def attack(self):
        self.start('attack')

    def spell(self):
        self.start('spell')

    def tokugi(self):
        self.start('tokugi')

    def mantan(self):
        self.start('mantan')

    def slot(self):
        self.start('slot')

    def stop(self):
        if self.running:
            self.thread.dqx.set_gui_b_loop(False)
            print '\nGUI: Stopping...'
        else:
            print '\nGUI: Invalid Operation'

    def start(self, command):
        if not self.running and command in ['attack', 'spell', 'tokugi', 'slot']:
            print 'GUI: Started'
            self.running = True
            self.thread = ThreadedTask(self.queue, command,
                self.gui_b_field.get(), self.gui_b_battle_ini.get(), self.gui_b_battle_end.get())
            self.thread.start()
            self.f.after(100, self.process_queue)
        elif command in ['mantan']:
            # field interrupt
            print '\nGUI: Interrupting (Field)...'
            self.thread.dqx.set_gui_field_command(command)
        elif command in ['attack', 'spell', 'tokugi']:
            # battle interrupt
            print '\nGUI: Interrupting (Battle)...'
            self.thread.dqx.set_gui_battle_command(command)
        else:
            print '\nGUI: Invalid Operation'

    def process_queue(self):
        try:
            msg = self.queue.get(0)
            self.running = False
            print 'GUI: Stopped'
        except Queue.Empty:
            self.f.after(100, self.process_queue)

class ThreadedTask(threading.Thread):
    def __init__(self, queue, command, gui_b_field, gui_b_battle_ini, gui_b_battle_end):
        threading.Thread.__init__(self)
        self.queue = queue
        self.command = command
        self.gui_b_field = gui_b_field
        self.gui_b_battle_ini = gui_b_battle_ini
        self.gui_b_battle_end = gui_b_battle_end
        self.dqx = DQXHelper()

    def run(self):
        print 'GUI:', self.command, self.gui_b_field, self.gui_b_battle_ini, self.gui_b_battle_end
        if self.command == 'slot':
            self.dqx.slot_mode()
        else:
            self.dqx.set_gui_b_field(self.gui_b_field)
            self.dqx.set_gui_b_battle_ini(self.gui_b_battle_ini)
            self.dqx.set_gui_b_battle_end(self.gui_b_battle_end)
            self.dqx.field_mode(self.command)
        self.queue.put('Task finished')

class StdoutRedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area
        self.buf = ''

    def write(self, text):
        self.buf += text
        self.buf = self.buf[-30*7:]
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.buf)
        self.text_area.see(tk.END)

root = tk.Tk()
ui = GUI(root)
root.title('DQXHelper')
root.mainloop()
