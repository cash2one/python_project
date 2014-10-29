#!/usr/bin/env python
#-*- coding:UTF-8 -*-
"""
@Item   :  database Backup
@Author :  Kevin Jiang
@Date   :  2013-02-26
@Funtion:
 
    
"""
 
import os,sys,time,re,socket,threading,json,base64,traceback,ConfigParser,fcntl,struct
from rsync_log import rsync_log
from rsync_post import rsync_post
from  statvfs import F_BLOCKS,F_BAVAIL,F_BSIZE
 
pcg = 0
""" ����쳲���������"""
lists = []
a,b = 0,1
while b <= 365:
    a,b = b ,a+b
    lists.append(b)
 
 
class rsync_thread(threading.Thread):
    def __init__(self,path):
        threading.Thread.__init__(self)
        self.log = rsync_log()
        self.path = path
 
 
    """ ���㵱ǰ���̵�ʹ�ðٷֱ�"""
    def disk(self):
        try:
            vfs = os.statvfs(self.path)
            disk_full = int(vfs[F_BLOCKS]*vfs[F_BSIZE]/1024/1024/1024)
            disk_free = int(vfs[F_BAVAIL]*vfs[F_BSIZE]/1024/1024/1024)
            return  '%.1f'%(float(disk_full - disk_free) / disk_full * 100)
        except:
            self.log.log_info('rsync_info.err','dfile.disk',traceback.print_exc())
            return traceback.print_exc()
 
 
    def run(self):
        global pcg
        old_df = []     # ��һ���ɾ����ʷ�ļ�
        new_df = []     # �����ɾ����ʷ�ļ�
        sf = []         # ��������ʷ�ļ�
        res = {}        # �����ļ����������ļ���·��
        rs = 0          # ɾ���ļ����ܺ�
        size = []       # ��ȡɾ���ļ��Ĵ�С
        msize = []      # ���챸�������ļ��Ĵ�С
        tday_size = []  # ���챸���ļ��Ĵ�С
        ms = 0          # ���챸���ļ����ܺ�
        year = time.localtime().tm_year
 
        """ �õ��ļ������������ļ�����Ϊkey��������Ϊvalue """
        for root,dirs,files in os.walk(self.path):
            for fpath in files:
                res[os.path.join(root,fpath)] =  time.localtime(os.stat(os.path.join(root,fpath)).st_ctime).tm_yday
 
        """ �ж��ļ��������Ƿ����쳲��������У���������append��sf�б���,������append df�б��� """
        for v,k in  res.items():
            if k in lists:
                sf.append(k)
                self.log.log_info('log_info.save','dfile.rsync_thread','%s:::%s'%(v,k))
            elif k not in lists:
                if year != time.localtime(os.stat(v).st_ctime).tm_year:
                    old_df.append({v:k})
                else:
                    new_df.append({v:k})
            try:
                for s in  range(len(new_df)):
                    for f,k in new_df[s].items():
                        tday_size.append(k)
                if max({}.fromkeys(tday_size).keys()) == k:
                    msize.append(os.path.getsize(f))
            except:
                pass
        c = []
        pcg = float(self.disk())
        """ �жϽ����Ƿ����µ��ļ����ݣ���ɾ�����б���ɾ�����һ������ݣ������뱣֤���̵�ʹ�ðٷֱȴ��ڵ��� %91 """
        if time.localtime().tm_yday in res.values():
            if len(old_df) != 0:
                for s in  range(len(old_df)):
                    for f,k in old_df[s].items():
                        c.append(k)
                for s in  range(len(old_df)):
                    for f,k in old_df[s].items():
                        if min({}.fromkeys(c).keys()) == k and pcg > 91:
                            size.append(os.path.getsize(f))
                            os.system('rm -frv %s' %f)
                            self.log.log_info('log_info.delete','remove cmd','rm -frv %s %s'%(f,k))
                        elif pcg <= 91:
                            break
                        pcg = float(self.disk())
            elif len(new_df) != 0:
                for s in  range(len(new_df)):
                    for f,k in new_df[s].items():
                        c.append(k)
                for s in  range(len(new_df)):
                    for f,k in new_df[s].items():
                        if min({}.fromkeys(c).keys()) == k and pcg > 91:
                            size.append(os.path.getsize(f))
                            os.system('rm -frv %s' %f)
                            self.log.log_info('log_info.delete','remove cmd','rm -frv %s %s'%(f,k))
                        elif pcg <= 91:
                            break
                        pcg = float(self.disk())
            for s in size:
                rs += s
            for m in msize:
                ms += m
            self.log.log_info('log_info.delete','Disk release %s %s MB'%(self.path,rs /1024/1024) ,'Disk append %s %s MB'%(self.path,ms /1024/1024))
        else:
            self.log.log_info('log_info.delete','Disk files ',' %s No update file' %self.path)
            sys.exit()
 
 
class rsync_dfile(object):
    def __init__(self):
 
    def work(self):
        fp =  open('/proc/mounts','r')
        m_info=fp.readlines()
        fp.close()
        data = {}
        sections = []
 
        for i in m_info:
            if i.find('data=ordered') != -1 or  i.find('mfs') != -1 or i.find('nfs') != -1:
                if os.path.ismount(str(i.split()[1])):
                    if str(i.split()[1]) != '/':
                        if str(i.split()[1]) != '/root':
                            if str(i.split()[1]) != '/var':
                                if len(i.split()[1]) != 1:
                                    if not i.find('sunrpc') != -1:
                                        rs_thread = rsync_thread(i.split()[1])
                                        rs_thread.start()
 
 
if __name__ == "__main__":
    rs = rsync_dfile()
    while True:
        rs.work()
        if pcg <= 91:
             break