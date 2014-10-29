#!/usr/bin/env python
#coding:utf8
import re
import sys
contents = sys.argv[1]
def NginxIpHite(logfile_path):
        #IP��4���ַ�����ÿ��1��3�����֣��ɵ�����
        ipadd = r'\.'.join([r'\d{1,3}']*4)
        re_ip = re.compile(ipadd)
        iphitlisting = {}
        for line in open(contents):
                match = re_ip.match(line)
                if match:
                        ip = match.group( )
                        #���IP��������1���������õ����Ϊ1
                        iphitlisting[ip] = iphitlisting.get(ip, 0) + 1
        print iphitlisting
NginxIpHite(contents)