#!/usr/bin/python
# coding=utf-8
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import re
from simplified_scrapy.core.utils import printInfo
from simplified_scrapy.core.dictex import Dict


class XmlDictConfig(Dict):
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(Dict(parent_element.items()))
            # self['text'] = parent_element.text
        flag = False
        for element in parent_element:
            flag = True
            if not self.get(element.tag):
                self.update({element.tag: []})

            dic = self.getDic(element)
            self[element.tag].append(dic)
            count = len(element)
            if count > 0:
                self.ele2arr(dic, element)
        if not flag:
            self.update({"tag": parent_element.tag})  # , 'text':parent_element.text})

def convert2Dic(html) -> Dict:
    try:
        start = html.find("<")
        end = html.find(">")
        html = html[start + 1 : end].strip("/").strip()
        html = re.sub(r"(\s|&nbsp;)+", " ", html, count=0)
        html = re.sub(r"(')+", '"', html, count=0)
        html = re.sub(r'(=\s*")+', '="', html, count=0)
        lst_c = []
        n = len(html)
        i = 0
        first = False
        flag = False
        while i < n:
            if html[i] == '"':
                lst_c.append(html[i])
                first = not first
            elif not first and html[i] == "=" and html[i + 1] != '"':
                lst_c.append(html[i])
                lst_c.append('"')
                flag = True
            elif not first and flag and html[i] == " ":
                flag = False
                lst_c.append('"')
                lst_c.append(html[i])
            else:
                lst_c.append(html[i])
            i += 1
        html = "".join(lst_c)
        paras = html.split('"')
        dic = Dict()
        last_p = None
        first = True
        for para in paras:
            if first:
                first = False
                tmp = para.split()
                dic["tag"] = tmp[0]
                if len(tmp) > 1:
                    last_p = tmp[1].strip().strip("=").strip()
                continue
            if last_p:
                if not dic[last_p]:
                    dic[last_p] = para
                else:
                    dic[last_p] += " "
                    dic[last_p] += para
                last_p = None
            elif para:
                if para.find("=") > 0:
                    last_p = para.strip().strip("=").strip()
                else:
                    dic[para] = ""
        return dic
    except Exception as err:
        printInfo(err)
        try:
            tag = ""
            if html.find("</") < 0 and html.find("/>") < 0:
                start = html.find("<")
                end = html.find(" ", start + 1)
                tag = "</" + html[start + 1 : end] + ">"
            tree = ET.XML(html + tag)
            return XmlDictConfig(tree)
        except Exception as err:
            printInfo(err)
    return Dict()
