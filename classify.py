#%%
import time
import os
import re
NOISE = ["avmans.com", "skyav.me", "bbs.yzkof.com", "www.52iv.net", "fbzip.com@", "3xplanet", "mosaic", "youiv", "hhd800.com@", "freedl.org@","icao.me@", "ses23.com", "thz.la", "javzip.net", "oldman", "aaxv.xyz", "amav.xyz", "uncensore", "hd_", "trim", "1080", "idolred", "thz", "leaked"]

def find_White(name):
    if len(name.split(".")) < 5:
        return False
    date_Info = re.findall(r"[0-9]{2}.[0-9]{2}.[0-9]{2}", name)
    if len(date_Info) == 1:
        return date_Info[0]+name.split(date_Info[0])[-1]
    else:
        modified_Time = os.path.getatime(name)
        time_prefix = time.strftime('%Y.', time.gmtime(modified_Time))[-3:] + time.strftime('%m.%d.', time.gmtime(modified_Time))
        return time_prefix + os.path.basename(name).lower()
    
#%%

def find_Uncon(name):
    signs = ["carib", "1pon", "heyzo", "fc2-ppv", "fcp", "sky", "s2m", "bt", "smbd"]
    company = ""
    for item in signs:
        if item in name.lower():
            company = item
            break
    digit6 = re.findall(r"[0-9]{6}", name)
    digit3 = re.findall(r"[0-9]{3}", name)
    if len(digit3) == 0 or len(digit6) == 0:
        digit4 = re.findall(r"[0-9]{4}", name, re.I)
        if len(digit4) == 0:
            if len(digit3) == 0 or len(company) == 0:            
                return False
            else:
                return f"{company.upper()}-{digit3[-1]}"
        else:
            return f"N{digit4[-1]}"
    elif len(company) != 0 and len(digit6) != 0:
        return f"{company.upper()}-{digit6[0]}-{digit3[-1]}"
    elif len(company) == 0:
        return f"{digit6[0]}-{digit3[-1]}"
    else:
        return f"{company.upper()-digit3[-1]}"


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
                    return item.upper()
            return False
        else:
            return result[0].upper()

    def find_digit(name):
        signs = ["1080", "720"]
        for item in signs:
            name = name.replace(item, "")
        result = re.findall(r"[0-9]{5}", name, re.I)
        if len(result) == 1:
            return result[0]
        result = re.findall(r"[0-9]{4}", name, re.I)
        if len(result) == 1:
            return result[0]
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
    return f"{comp.upper()}-{digit}"


def fix_name(path):
    name = os.path.basename(path).lower()
    for item in NOISE:
        name = name.replace(item, "")
    return name


def new_Name(source, dist_dir):
    new_Name = ""
    old_Name = fix_name(source)
    file_Type = old_Name.split(".")[-1]

    new_Name = find_White(source)

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
    while os.path.isfile(os.path.join(dist_dir, new_Name+"."+file_Type)):
        new_Name+="i"
    new_Name =new_Name + "."+ file_Type
    return new_Name


# test cases
if __name__ == "__main__":
    print(new_Name("C:\迅雷下载\[thz.la]SKY-249\[thz.la]SKY-249_Shino_Megumi.wmv","E:\\Videos\\Active"))
    print(new_Name("D:\\AV\\N-n1357.wmv","D:\\AV"))
    print(new_Name("D:\download\S2M-055\S2M-055.mpg","D:\\AV"))
    print(new_Name("D:\\download\\Tokyo-Hot-n1326-HD\\1024核工厂_n1326_oshhiko_05_rf.mp4", "D:\\AV"))
    print(new_Name("D:\\download\\SDNM-229_UNCENSORED_LEAKED.mp4", "D:\\AV"))
    print(new_Name("E:\\Videos\\Archive\\White\\suckthisdick.e18.chloe.cherry.and.lola.fae.mp4", "D:\\AV"))



