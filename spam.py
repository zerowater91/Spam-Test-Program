#-*- coding: cp949 -*-
# 2015.09.23 김영수 작성
#---------------------

import csv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from pyPdf import PdfFileWriter, PdfFileReader
import poster.encode
import poster.streaminghttp
import time
import datetime
import random
import optparse
import urllib, urllib2
import sys, os
import shutil
import wx
from threading import Thread

#아래는 gmail 사용시만 사용
#gmail_user="test@a.com"
#gmail_pwd="12345"

js_file = "redirect.js"

class SendThread(Thread):
    def __init__(self, mailList, startNum, htmlfile, pdffile, attachbool, spam):
        Thread.__init__(self)
        self.mailList = mailList
        self.startNum = startNum
        self.htmlfile = htmlfile
        self.pdffile = pdffile
        self.attachbool = attachbool
        self.spam = spam
        self.username = self.spam.frame.txt_senduser.GetValue() + "<>"
        self.attach_pdf_file = self.spam.frame.txt_sendpdf.GetValue()

    def run(self):
        title=self.spam.frame.txt_mailtitle.GetValue()

        self.spam.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] Program Ready\n")

        index = self.startNum
        for email in self.mailList:
            dn = "http://"+self.spam.ipaddr+"/?index="
            dn += str(index)
            index += 1

            pdfurl = dn + "&method=2"

            self.spam.create_jsfile(js_file, pdfurl)
            if(self.spam.frame.chk_pdf.GetValue() == True):
                self.spam.create_pdf(self.pdffile, self.attach_pdf_file, js_file)
            db += "&method=1"

            src = open(self.htmlfile,"r")
            value = src.read()
            src.close()

            data = value.replace(u"testurl".encode('cp949'),dn.encode('cp949'))

            f = open("text.txt","w+")
            f.write(data)
            f.close()

            f = open("text.txt","r")
            message = f.read()
            f.close()
            shutil.copyfile("text.txt","html.html")

            f = open("html.html", "r")
            html = f.read()
            f.close()
            email = email.strip()
            if email == "":
                continue
            self.spam.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] ["+str(index-1) +"] Sending To "+email+"\n")

            try:
                self.send_gmail(email, title, message, html, self.attach_pdf_file, self.attachbool)
                if(self.attachbool == True):
                    os.remove(self.attach_pdf_file)
            except:
                self.spam.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] ["+str(index-1) +"] Sending Error "+email+"\n")
                self.spam.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] 이메일 전송 실패\n")
                os.remove("html.html")
                os.remove("redirect.js")
                os.remove("text.txt")
                return
        self.spam.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] 이메일 전송 완료\n")
        os.remove("html.html")
        os.remove("redirect.js")
        os.remove("text.txt")

    def send_gmail(self, to, subject, text, html, attach, attachbool):
        msg=MIMEMultipart('alternative')
        msg['From']=self.username.encode('cp949')
        msg['To']=to
        msg['Subject']=Header(subject,'cp949') #encoding
        msg.attach(MIMEText(text, 'plain', 'cp949')) #encoding
        msg.attach(MIMEText(html, 'html', 'cp949')) #encoding
        
        if(attachbool == True):
            part=MIMEBase('application','octet-stream')
            part.set_payload(open(attach, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition','attachment', filename=Header(os.path.basename(attach),'cp949').encode())
            msg.attach(part)
        
        mailServer=smtplib.SMTP("localhost")
        mailServer.ehlo()
        #mailServer.starttls()
        mailServer.ehlo()
        #mailServer.login(gmail_user,gmail_pwd)
        
        mailServer.sendmail(self.username.encode('cp949'), to, msg.as_string())
        mailServer.close()

class Spam:
    def __init__(self, user, pwd, ipaddr, frame):
        self.user = user
        self.pwd = pwd
        self.ipaddr = ipaddr
        self.cookie = ''
        self.frame = frame

    def session_login(self):
        try:
            url = "http://" + self.ipaddr + "/login_ok.php"
            login_form = {"m_id":self.user,"m_passwd":self.pwd,"remember":"1"}
            login_req = urllib.urlencode(login_form)
            request = urllib2.Request(url, login_req)
            response = urllib2.urlopen(request)
            data = response.read()
            if(data.find("입력한 정보가 틀렸습니다.") == -1 and data.find("history.back()") == -1):
                self.cookie = response.headers.get('Set-Cookie')
                wx.MessageBox("로그인 성공!\nCookie : %s" %(self.cookie),"로그인성공", wx.OK)
                return 1
            else:
                wx.MessageBox("로그인 실패!\nID/PW 및 IP:PORT 입력하세요","로그인실패", wx.OK)
                return 0
        except:
            wx.MessageBox("로그인 실패!\nID/PW 및 IP:PORT 입력하세요","로그인실패", wx.OK)
            return 0

    def del_ListDB(self):
        if(self.cookie != ''):
            url  = "http://" + self.ipaddr + "/super_dlapdlftkrwp.php"
            request = urllib2.Request(url)
            request.add_header('Cookie', self.cookie)
            response = urllib2.urlopen(request)
            data = response.read()
            st = unicode("삭제되었습니다.",'euc-kr').encode('utf-8')
            if(data.find(st) != -1):
                wx.MessageBox("삭제 성공!","삭제성공", wx.OK)
                return 1
            else:
                wx.MessageBox("삭제 실패!","삭제실패", wx.OK)
                return 0
        else:
            wx.MessageBox("로그인부터 먼저 해주세요","로그인",wx.OK)

    def csv_Upload(self, fileName):
        if(self.cookie != ''):
            url = "http://" + self.ipaddr + "/super_djqfhem-1.php"
            opener = poster.streaminghttp.register_openers()
            params = {'file"; fileName="'+os.path.basename(fileName)++'";':open(fileName,'rb').read()}
            datagen, headers = poster.encode.multipart_encode(params)
            request = urllib2.Request(url, datagen, headers)
            request.add_header('Cookie',self.cookie)
            response = opener.open(request)

            st = unicode("등록 되었습니다.", 'euc-kr').encode('utf-8')
            if(response.read().find(st) != -1):
                wx.MessageBox("등록 완료!","등록완료",wx.OK)
                return 1
            else:
                wx.MessageBox("등록 실패!","등록실패",wx.OK)
                return 0
        else:
            wx.MessageBox("로그인부터 먼저 해주세요","로그인",wx.OK)

    def create_pdf(self, src_file_path, dst_file_path, js_file_path):
        input_pdf_file = PdfFileReader(file(src_file_path,"rb"));
        output_pdf_file = PdfFileWriter()

        pages = input_pdf_file.getNumPages()

        for p in range(pages):
            output_pdf_file.addPage(input_pdf_file,getPage(p))
        try:
            js_file = open(js_file_path,'rb')
        except:
            self.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] JS파일 미존재\n")
            return
        try:
            javascript = js_file.read()
        except:
            self.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] JS파일 읽기 에러\n")
            return
        finally:
            js_file.close()
        output_pdf_file.addJS(javascript)
        outputStream = file(dst_file_path, "wb")
        output_pdf_file.write(outputStream)
        outputStream.close()

    def create_jsfile(self, js_file_path, url):
        try:
            f = open(js_file_path, "w")
            f.write("app.launchURL('"+url+"')")
            f.close()
        except:
            self.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] JS파일 생성 실패\n")
            return

    def csvRange(self, selectFile, startNum, endNum):
        returnList = []
        csvFile = open(selectFile,'rb')
        reader = csv.reader(csvFile)
        for row in reader:
            try:
                if(startNum <= int(row[0]) <= endNum):
                    returnList.append(row[1])
            except:
                continue
        self.frame.txt_status.AppendText("["+str(datetime.datetime.now())+"] 보낼메일주소\n")
        i = 1
        for retu in returnList:
            self.frame.txt_status.AppendText("["+str(i)+"] "+retu+"\n")
            i = i+1
        return returnList

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, style=wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(10,10)

        self.txt_csv = wx.TextCtrl(panel,1,'')
        self.btn_file = wx.Button(panel,2,'파일찾기')
        self.txt_ip = wx.TextCtrl(panel,3,'')
        self.txt_id = wx.TextCtrl(panel,4,'')
        self.txt_pw = wx.TextCtrl(panel,5,'', style=wx.TE_PASSWORD)
        self.btn_login = wx.Button(panel,6,'로그인')
        self.btn_logout = wx.Button(panel,7,'로그아웃')

        sizer.Add(wx.StaticText(panel,-1,"환경설정"),(0,0),(1,1),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"CSV파일"),(1,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_csv,(1,1),(1,11),wx.EXPAND)
        sizer.Add(self.btn_file,(1,12),(1,1),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"IP:PORT"),(2,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_ip,(2,1),(1,12),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"아이디"),(3,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_id,(3,1),(1,11),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"패스워드"),(4,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_pw,(4,1),(1,11),wx.EXPAND)
        sizer.Add(self.btn_login,(3,12),(1,1),wx.EXPAND)
        sizer.Add(self.btn_logout,(4,12),(1,1),wx.EXPAND)
        sizer.Add(wx.StaticLine(panel),(5,0),(1,13),wx.EXPAND)

        #DB DEL/INS
        self.btn_deldb = wx.Button(panel,8,'DataBase삭제')
        self.btn_insdb = wx.Button(panel,9,'DataBase등록')

        sizer.Add(wx.StaticText(panel,-1,"DB 삭제 및 등록"),(6,0),(1,1),wx.EXPAND)
        sizer.Add(self.btn_deldb,(7,0),(1,6),wx.EXPAND)
        sizer.Add(self.btn_insdb,(7,7),(1,6),wx.EXPAND)
        sizer.Add(wx.StaticLine(panel),(8,0),(1,13),wx.EXPAND)

        # Mail Send
        self.txt_html = wx.TextCtrl(panel,10,'')
        self.btn_html = wx.Button(panel,11,"파일 찾기")
        self.txt_pdf = wx.TextCtrl(panel,12,'')
        self.btn_pdf = wx.Button(panel,13,"파일 찾기")
        self.txt_sendpdf = wx.TextCtrl(panel,14,'')
        self.chk_pdf = wx.CheckBox(panel,15,"PDF포함")
        self.txt_senduser = wx.TextCtrl(panel,16,'')
        self.txt_mailtitle = wx.TextCtrl(panel,17,'')
        self.txt_start = wx.TextCtrl(panel,18,'')
        self.txt_end = wx.TextCtrl(panel,19,'')
        self.btn_send = wx.Button(panel,20,'메일보내기')

        sizer.Add(wx.StaticText(panel,-1,"메일 송신"),(9,0),(1,1),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"HTML파일"),(10,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_html,(10,1),(1,11),wx.EXPAND)
        sizer.Add(self.btn_html,(10,12),(1,1),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"PDF파일"),(11,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_pdf,(11,1),(1,11),wx.EXPAND)
        sizer.Add(self.btn_pdf,(11,12),(1,1),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"첨부파일명"),(12,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_sendpdf,(12,1),(1,11),wx.EXPAND)
        sizer.Add(self.chk_pdf,(12,12),(1,1),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"보내는사람"),(13,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_senduser,(13,1),(1,12),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"메일제목"),(14,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_mailtitle,(14,1),(1,12),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"시작인덱스"),(15,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_start,(15,1),(1,11),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,"종료인덱스"),(16,0),(1,1),wx.EXPAND)
        sizer.Add(self.txt_end,(16,1),(1,11),wx.EXPAND)
        sizer.Add(self.btn_send,(15,12),(3,1),wx.EXPAND)

        # Status
        self.txt_status = wx.TextCtrl(panel,21,'',style=wx.TE_MULTILINE | wx.TE_READONLY)

        sizer.Add(wx.StaticLine(panel,-1,style=wx.LI_VERTICAL),(1,13),(17,1),wx.EXPAND)
        sizer.Add(wx.StaticText(panel,-1,'상태창'),(0,14),(1,1),wx.EXPAND)
        sizer.Add(self.txt_status,(1,14),(17,21),wx.EXPAND)

        self.SetSizerAndFit(sizer)
        self.Centre()
        panel.SetSizer(sizer)
        panel.SetSize(self.GetSize())
        panel.Layout()

        # Bind Event
        self.Bind(wx.EVT_BUTTON, self.OnCsvFile, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnLogin, id=6)
        self.Bind(wx.EVT_BUTTON, self.OnDelDB, id=8)
        self.Bind(wx.EVT_BUTTON, self.OnInsDB, id=9)
        self.Bind(wx.EVT_BUTTON, self.OnHtmlFile, id=11)
        self.Bind(wx.EVT_BUTTON, self.OnPdfFile, id=13)
        self.Bind(wx.EVT_BUTTON, self.OnSend, id=20)
        self.Bind(wx.EVT_BUTTON, self.OnLogout, id=7)
        self.Bind(wx.EVT_CHECKBOX, self.OnPdfCheck, id=15)

        self.btn_deldb.Disable()
        self.btn_insdb.Disable()
        self.btn_html.Disable()
        self.btn_pdf.Disable()
        self.btn_send.Disable()
        self.btn_logout.Disable()
        self.chk_pdf.Disable()

    def OnPdfCheck(self, event):
        if(self.chk_pdf.GetValue() == True):
            self.txt_sendpdf.Enable()
        else:
            self.txt_sendpdf.Clear()
            self.txt_sendpdf.Disable()

    def OnCsvFile(self, event):
        dig = wx.FileDialog(self,"파일 선택", os.getcwd(),"","*.csv",wx.OPEN)
        if dig.ShowModal() == wx.ID_OK:
            path = dig.GetPath()
            self.txt_csv.Clear()
            self.txt_csv.SetValue(path)

    def OnLogin(self, event):
        if(self.txt_ip.GetValue != '' and self.txt_id.GetValue != '' and self.txt_pw.GetValue != ''):
            self.spam = Spam(self.txt_id.GetValue(),self.txt_pw.GetValue(),self.txt_ip.GetValue(),self)
            if(self.spam.session_login()==1):
                self.txt_status.AppendText("["+str(datetime.datetime.now())+"] 로그인성공( Cookie : "+self.spam.cookie+" )\n")
                self.btn_login.Disable()
                self.btn_deldb.Enable()
                self.btn_insdb.Enable()
                self.btn_html.Enable()
                self.btn_pdf.Enable()
                self.btn_send.Enable()
                self.btn_logout.Enable()
                self.txt_id.SetEditable(False)
                self.txt_pw.SetEditable(False)
                self.txt_ip.SetEditable(False)
                self.chk_pdf.Enable()
            else:
                self.txt_status.AppendText("["+str(datetime.datetime.now())+"] 로그인실패\n")

    def OnLogout(self, event):
        self.btn_login.Enable()
        self.btn_deldb.Disable()
        self.btn_insdb.Disable()
        self.btn_html.Disable()
        self.btn_pdf.Disable()
        self.btn_send.Disable()
        self.btn_logout.Disable()
        self.chk_pdf.Disable()
        self.txt_id.Clear()
        self.txt_pw.Clear()
        self.txt_id.SetEditable(True)
        self.txt_pw.SetEditable(True)
        self.txt_ip.SetEditable(True)
        self.spam.cookie = ''

    def OnDelDB(self, event):
        try:
            if(self.spam.del_ListDB()==1):
                self.txt_status.AppendText("["+str(datetime.datetime.now())+"] 삭제성공\n")
            else:
                self.txt_status.AppendText("["+str(datetime.datetime.now())+"] 삭제실패\n")
        except:
            wx.MessageBox("로그인부터 먼저 해주세요", "로그인", wx.OK)

    def OnInsDB(self, event):
        try:
            if(self.spam.csvUpload(self.txt_csv.GetValue())==1):
                self.txt_status.AppendText("["+str(datetime.datetime.now())+"] 업로드성공\n")
            else:
                self.txt_status.AppendText("["+str(datetime.datetime.now())+"] 업로드실패\n")
        except:
            wx.MessageBox("로그인이 되지 않았거나 CSV 선택을 안했습니다", "에러", wx.OK)

    def OnHtmlFile(self, event):
        dig = wx.FileDialog(self,"파일 선택", os.getcwd(),"","*.html",wx.OPEN)
        if dig.ShowModal() == wx.ID_OK:
            path = dig.GetPath()
            self.txt_html.Clear()
            self.txt_html.SetValue(path)

    def OnPdfFile(self, event):
        dig = wx.FileDialog(self,"파일 선택", os.getcwd(),"","*.pdf",wx.OPEN)
        if dig.ShowModal() == wx.ID_OK:
            path = dig.GetPath()
            self.txt_pdf.Clear()
            self.txt_pdf.SetValue(path)

    def OnSend(self, event):
        try:
            if(self.txt_html.GetValue() != '' and self.txt_start.GetValue() != '' and self.txt_end.GetValue() != ''):
                if(int(self.txt_start.GetValue())>int(self.txt_end.GetValue())):
                    self.txt_status.AppendText("["+str(datetime.datetime.now())+"] 시작인덱스가 더큽니다.\n")
                    return
                mailList = self.spam.csvRange(self.txt_csv.GetValue(), int(self.txt_start.GetValue()), int(self.txt_end.GetValue()))

                sendThread = SendThread(mailList,int(self.txt_start.GetValue()),self.txt_html.GetValue(),self.txt_pdf.GetValue(),self.chk_pdf.GetValue(),self.spam)
                sendThread.setName('Send Thread')

                sendThread.start()
            else:
                wx.MessageBox("로그인이 되지 않았거나 CSV,HTML,PDF 선택을 안했습니다.","에러",wx.OK)
        except:
            wx.MessageBox("로그인이 되지 않았거나 CSV,HTML,PDF 선택을 안했습니다.","에러",wx.OK)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "스팸메일 모의훈련 v0.1 by youngsoo")
        panel = wx.Panel(frame)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()
