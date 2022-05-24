#%%
from hashlib import new
import os
import re
NOISE = ["bbs.yzkof.com", "fbzip.com@", "3xplanet", "mosaic", "youiv", "hhd800.com@", "freedl.org@", "ses23.com", "thz.la", "oldman", "uncen", "hd_"]

def find_White(name):
    date_Info = re.findall(r"[0-9]{2}.[0-9]{2}.[0-9]{2}", name)
    if len(date_Info) != 1:
        return False
    else:
        return date_Info[0]+name.split(date_Info[0])[-1]
    
#%%

def find_Uncon(name):
    signs = ["carib", "1pon", "heyzo"]
    company = ""
    for item in signs:
        if item in name.lower():
            company = item
    digit6 = re.findall(r"[0-9]{6}", name)
    digit3 = re.findall(r"[0-9]{3}", name)
    if len(digit3) == 0 or len(digit6) == 0:
        digit4 = re.findall(r"n[0-9]{4}", name, re.I)
        if len(digit4) == 0:
            return False
        elif len(company) != 0:
            return f"{company.upper()}-{digit4[0]}"
        else:
            return f"{digit4[0].upper()}"
    elif len(company) != 0:
        return f"{company.upper()}-{digit6[0]}-{digit3[-1]}"
    else:
        return f"{digit6[0]}-{digit3[-1]}"


def find_Con(name):
    def find_comp(name):
        result = re.findall(r"[A-Z]{5}", name, re.I)
        if len(result) == 0:
            result = re.findall(r"[A-Z]{4}", name, re.I)
        if len(result) == 0:
            result = re.findall(r"[A-Z]{3}", name, re.I)
        for item in ("rmvb", "mkv", "wmv", "avi", "iso", "dvd", "com"):
            if item in result:
                result.remove(item)
        if len(result) == 0:
            for item in ["ct", "bt", "yo", "sw"]:
                if item in name:
                    return item
            return False
        else:
            return result[0].upper()

    def find_digit(name):
        signs = ["1080", "720"]
        for item in signs:
            name = name.replace(item, "")
        result = re.findall(r"[0-9]{3}", name, re.I)
        if len(result) == 0:
            return False
        else:
            return result[-1]

    digit = find_digit(name)
    if not digit:
        return False
    comp = find_comp(name)
    if not comp:
        return False
    return f"{comp}-{digit}"


def fix_name(path):
    name = os.path.basename(path)
    for item in NOISE:
        name = name.lower().replace(item, "")
    return name


def new_Name(source, dist_dir):
    old_Name = fix_name(source)
    new_Name = ""
    file_Type = old_Name.split(".")[-1]
    new_Name = find_White(old_Name)
    if new_Name:
        return os.path.join("white", new_Name)
    uncon = find_Uncon(old_Name)
    if not uncon:
        con = find_Con(old_Name)
        if not con:
            return old_Name
        else:
            new_Name = con
    else:
        new_Name = uncon
    if new_Name + "." + file_Type == old_Name:
        return old_Name.upper()
    while os.path.isfile(os.path.join(dist_dir, new_Name+"."+file_Type)):
        new_Name+="i"
    new_Name+="."+file_Type
    return new_Name