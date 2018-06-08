#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 13:12:14 2018

@author: ljk
"""
import sys
import re
import requests
import json
import execjs 

class Py4Js():  
      
    def __init__(self):  
        self.ctx = execjs.compile(""" 
        function TL(a) { 
        var k = ""; 
        var b = 406644; 
        var b1 = 3293161072; 
         
        var jd = "."; 
        var $b = "+-a^+6"; 
        var Zb = "+-3^+b+-f"; 
     
        for (var e = [], f = 0, g = 0; g < a.length; g++) { 
            var m = a.charCodeAt(g); 
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
            e[f++] = m >> 18 | 240, 
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
            e[f++] = m >> 6 & 63 | 128), 
            e[f++] = m & 63 | 128) 
        } 
        a = b; 
        for (f = 0; f < e.length; f++) a += e[f], 
        a = RL(a, $b); 
        a = RL(a, Zb); 
        a ^= b1 || 0; 
        0 > a && (a = (a & 2147483647) + 2147483648); 
        a %= 1E6; 
        return a.toString() + jd + (a ^ b) 
    }; 
     
    function RL(a, b) { 
        var t = "a"; 
        var Yb = "+"; 
        for (var c = 0; c < b.length - 2; c += 3) { 
            var d = b.charAt(c + 2), 
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
        } 
        return a 
    } 
    """)  
          
    def getTk(self,text):  
        return self.ctx.call("TL",text)  
if __name__ == '__main__':
    #print('please input')
    word=sys.argv[1]
    headers={
            'cookie':'_ga=GA1.3.1163951248.1511946285; NID=131=XX0_dJsOrF47GXs2WNtO1MXyKVCK39bW4HXS0XZZ3ZYHTvMGOz8CVJe1G2XVwAJNF9MYOb1ngCqa_NegB6db2kgJ5A9hT3SScy0ag_L41wvtXHiPpNZweONFGHFNtWR_; 1P_JAR=2018-6-7-15',
    'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
            }
    try:
        re.search('[a-z]',word)[0]
        url='https://translate.google.cn/translate_a/single?client=t&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&otf=1&ssel=0&tsel=0&kc=2&tk={tk}&q='+word
    except:
        url='https://translate.google.cn/translate_a/single?client=t&sl=zh-CN&tl=en&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&otf=2&ssel=6&tsel=3&kc=1&&tk={tk}&q='+word
    js =Py4Js()
    tk = js.getTk(word)
    url=url.format(tk=tk)
    print('***********translating***********')
    #while
    try:
        s=requests.get(url,headers=headers)
        sj=s.json()
        trans=''
        try:
            len(sj[1])
            trans+='['+sj[1][0][0]+']'+'\n'
            for i in sj[1][0][1]:
                trans+=str(i)+','
            trans=trans.rstrip(',')
        except:
            for i in sj[0][:-1]:
                trans+=i[0]+'\n'
    except:
        trans=word
    print(trans)
