import wx
from wx import adv
import os
import string
import threading
from threading import Thread
import time
import math
from time import sleep

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select

class ExamplePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        grid = wx.GridBagSizer(hgap=8,vgap=8)
        
        self.logger = wx.TextCtrl(self, size=(1000,int(1000*0.618)), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.logger.SetForegroundColour(wx.WHITE)
        self.logger.SetBackgroundColour(wx.BLACK)
        self.logger.SetEditable(False)
        hSizer.Add(self.logger, 0, wx.ALL, 6)

        btlen = 100

        grid.Add(wx.StaticText(self, label='Setup Time', size=(btlen*2,-1)), pos=(2,0))
        self.datePicker_1 = adv.DatePickerCtrl(self, wx.ID_ANY, wx.DateTime.Now(),size=(btlen+10, -1))
        grid.Add(self.datePicker_1, pos=(3,0))

        self.produceBt = wx.Button(self, label="Daily", size=(btlen, -1))
        self.Bind(wx.EVT_BUTTON, self.OnClickProduceDaily, self.produceBt)
        grid.Add(self.produceBt, pos=(5,0))

        self.produceWeekBt = wx.Button(self, label="Weekly", size=(btlen, -1))
        self.Bind(wx.EVT_BUTTON, self.OnClickProduceWeek, self.produceWeekBt)
        grid.Add(self.produceWeekBt, pos=(7,0))

        self.clearBt = wx.Button(self, label="Clear", size=(btlen, -1))
        self.Bind(wx.EVT_BUTTON, self.OnClickClear, self.clearBt)
        grid.Add(self.clearBt, pos=(20,2))

        hSizer.Add(grid, 0, wx.ALL, 12)
        mainSizer.Add(hSizer, 0, wx.ALL, 6)
        self.SetSizerAndFit(mainSizer)

        self.filename1 = ''
        self.filename2 = ''
        self.compFileName = ''

    def OnClickClear(self, event):
        self.logger.SetValue('')

    def OnClickProduceDaily(self, event):
        date1 = self.datePicker_1.GetValue()
        timestr = date1.FormatISODate()
        self.logger.AppendText("设置时间信息: " + timestr + "\n")
        self.logger.AppendText("合约净多变化量 开始生成, 请稍候......\n\n")
        self.produceBt.Enable(False)
        self.produceWeekBt.Enable(False)
        ProduceThread(self, 1)

    def OnClickProduceWeek(self, event):
        date1 = self.datePicker_1.GetValue()
        timestr = date1.FormatISODate()
        self.logger.AppendText("设置时间信息: " + timestr + "\n")
        self.logger.AppendText("合约交易量净多 开始生成, 请稍候......\n\n")
        self.produceBt.Enable(False)
        self.produceWeekBt.Enable(False)
        ProduceThread(self, 2)


class ProduceThread(threading.Thread):
    def __init__(self, lay, method):
        threading.Thread.__init__(self)
        self.lay = lay
        self.start()
        self.method = method

    def run(self):
        lay = self.lay
        date1 = lay.datePicker_1.GetValue()
        self.timestr = date1.FormatISODate()

        self.driver = webdriver.PhantomJS()

        try:
            self.driver.get('http://www.cffex.com.cn/ccpm')
            self.driver.find_element_by_id('actualDate').clear()
            self.driver.find_element_by_id('actualDate').send_keys(self.timestr)

            self.select = Select(self.driver.find_element_by_id('selectSec'))

            if self.method == 1:
                self.getDataByName('IC')
                self.getDataByName('IF')
                self.getDataByName('IH')
            elif self.method == 2:
                self.getWeekDataByName('IC')
                self.getWeekDataByName('IF')
                self.getWeekDataByName('IH')
            self.lay.produceBt.Enable(True)
            self.lay.produceWeekBt.Enable(True)
            self.driver.quit()
        except Exception as e:
            self.driver.quit()

        lay.logger.AppendText("\n")

    def getDataByName(self, strName):
        #self.lay.logger.AppendText(strName + "开始生成\n")
        self.select.select_by_visible_text(strName)
        self.driver.find_element_by_class_name('btn-query').click()
        tbs = self.driver.find_elements_by_class_name('IF_if_table')

        num = 0
        total_delta = 0
        for tb in tbs:
            num += 1
            tdall = tb.find_elements_by_tag_name('td')
            buy = 0
            sell = 0
            for i in range(1, len(tdall)):
                if tdall[i].text == '中信期货':
                    if i % 12 == 8:
                        buy = int(tdall[i+2].text)
                    elif i % 12 == 0:
                        sell = int(tdall[i+2].text)

                    if buy != 0 and sell != 0:
                        break

            total_delta += (buy - sell)
            #str1 = "Name: {}, 合约: {}, 买: {:<10d}, 卖: {:<10d}, 差值: {:<10d}\n".format(strName, num, buy, sell, buy-sell)
            #self.lay.logger.AppendText(str1)

        str2 = "{} {} 合约净多变化量:  {}\n".format(self.timestr, strName, total_delta)
        self.lay.logger.AppendText(str2)

    def getWeekDataByName(self, strName):
        self.select.select_by_visible_text(strName)
        self.driver.find_element_by_class_name('btn-query').click()
        tbs = self.driver.find_elements_by_class_name('IF_if_table')

        num = 0
        total_delta = 0
        for tb in tbs:
            num += 1
            tdall = tb.find_elements_by_tag_name('td')
            buy = 0
            sell = 0
            for i in range(1, len(tdall)):
                if tdall[i].text == '中信期货':
                    if i % 12 == 8:
                        buy = int(tdall[i+1].text)
                    elif i % 12 == 0:
                        sell = int(tdall[i+1].text)

                    if buy != 0 and sell != 0:
                        break
            total_delta += (buy - sell)

        str2 = "{} {} 合约交易量净多:  {}\n".format(self.timestr, strName, total_delta)
        self.lay.logger.AppendText(str2)

def main():
    app = wx.App(False)
    frame = wx.Frame(None, 100, '期指合约', size = wx.Size(1400, int(1200*0.618)))
    panel = ExamplePanel(frame)
    frame.Show()
    app.MainLoop()
main()

