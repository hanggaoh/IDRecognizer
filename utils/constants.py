import re

video_extensions = {
    '.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg', 
    '.3gp', '.webm', '.ogv', '.vob', '.rm', '.rmvb', '.m2ts', '.mts', '.ts', 
    '.mxf', '.divx', '.f4v', '.asf', '.amv', '.svi', '.3g2', '.m2v', '.mpe',
    '.mpv', '.m1v', '.m4p', '.m4b', ".iso", '.nrg'
}

patterns = {
    r"^([a-zA-Z0-9]+)\.(\d{2}\.\d{2}\.\d{2})(\..*)$": lambda m: f"{m.group(2)}.{m.group(1)}{m.group(3)}",
    r'(?i)(heyzo).*(\d{4})': r'\1-\2',
    r'(?i)(fc2).*(ppv).*(\d{7}|\b\d{6}\b)': r'\1-\2-\3',
    r'(?i)(\d{6})[-_](\d{3}).*(carib|1pon)': r'\3-\1-\2',
    r'(?i)(\d{6})[-_](\d{2,3}).*(10mu)': r'\3-\1-\2',
    r'(?i)(carib|1pon).*(\d{6})[-_](\d{3}).*': r'\1-\2-\3',
    r'(\d{6})[-_](\d{3})': r'\1-\2',
    r'([nNkK]\d{4})': r'\1',
    r"([a-z]{2,5})[-_]?(\d{2,3})[-_](\d{1,2})(?!(k))": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).zfill(2).upper()}",
    r"([a-z]{2,5})-(\d{2,3})[-_]?cd([\d]{1,2})": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).zfill(2).upper()}",
    r"([a-z]{2,5})[-_]?(\d{2,3})[-_]?([a-f]{1})(?!(hd|v))": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).upper()}",
    r"([a-z]{2,5})-(\d{2,3})[-_]?([A-Ea-e])(?!(v))": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).upper()}",
    r"([a-z]{2,5})-(\d{2,3})[\s]+([A-Ea-e])": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).upper()}",
    r"([a-z]{2,5})-(\d{2,3})HD([A-E])": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).upper()}",
    r"([a-z]{2,5})-(\d{2,3})\.?1080P\s*([A-E])": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).upper()}",
    r"([a-z]{2,5})[-_0]*(\d{3})\.?hhb\s*([\d])": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).zfill(2).upper()}",
    r'(?<![a-zA-Z])(ID)[-_](\d{3})': r'\1-\2',  # Modified: no a-zA-Z before 'ID'
    r"([a-z]{4,5})(\d{2,3})": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}",
    r'([A-Z]{2,7})[-_/s](?!\d{6,9})(\d{2,5})': r'\1-\2',
    r'([A-Z0-9]{3,8})[-_]*(?!\d{6,9})(\d{3,5})': r'\1-\2',
    r'([a-zA-Z]{4,6})[-_\s]?(\d{2,5})': r'\1-\2',
    r'([a-zA-Z0-9]{2,8})[-_0](\d{2,5})': r'\1-\2',
    r'([a-zA-Z]{3,4})(\d{2,5})': r'\1-\2',
    r'([a-zA-Z]{2,4})[-_]?(\d{2,5})': r'\1-\2',
}