video_extensions = {
    '.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg', 
    '.3gp', '.webm', '.ogv', '.vob', '.rm', '.rmvb', '.m2ts', '.mts', '.ts', 
    '.mxf', '.divx', '.f4v', '.asf', '.amv', '.svi', '.3g2', '.m2v', '.mpe',
    '.mpv', '.m1v', '.m4p', '.m4b', ".iso"
}

patterns = {
    r'(heyzo).*(\d{4})': r'\1-\2',
    r'(?i)(fc2).*(ppv).*(\d{7}|\b\d{6}\b)': r'\1-\2-\3',
    r'(?i)(\d{6})[-_](\d{3}).*(carib|1pon)': r'\3-\1-\2',
    r'(?i)(carib|1pon).*(\d{6})[-_](\d{3}).*': r'\1-\2-\3',
    r'(\d{6})[-_](\d{3})': r'\1-\2',
    r'([a-zA-Z]{4})[0]*(\d{3,4})': r'\1-\2',
    r'([nN]\d{4})': r'\1',
    r"([a-z]{2,5})-(\d{2,3})_(\d{1,2})": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).zfill(2).upper()}",
    r"([a-z]{2,5})-(\d{2,3})[-_]?cd([\d]{1,2})": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).zfill(2).upper()}",
    r"([a-z]{2,5})-(\d{2,3})[-_]?([A-Ea-e])": lambda m: f"{m.group(1)}-{m.group(2).zfill(3)}_{m.group(3).upper()}",
    r'([a-zA-Z]{4,6})[-_0](\d{2,4})': r'\1-\2',
    r'([a-zA-Z0-9]{2,8})[-_0](\d{2,4})': r'\1-\2',
    r'([a-zA-Z]{3,4})(\d{2,4})': r'\1-\2',
    }