import asyncio
import aiohttp
import os
import re
import sys
import time

# Настройка цветов для Windows
if os.name == 'nt':
    import ctypes
    from ctypes import wintypes
    
    # Константы для зеленых оттенков
    FOREGROUND_GREEN = 0x0002
    FOREGROUND_LIGHT_GREEN = 0x000A
    FOREGROUND_INTENSITY = 0x0008
    
    # Получаем хэндл консоли
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    
    green_colors = [
        FOREGROUND_GREEN,                    # Темно-зеленый
        FOREGROUND_GREEN | FOREGROUND_INTENSITY,  # Зеленый
        FOREGROUND_LIGHT_GREEN,              # Светло-зеленый
        FOREGROUND_GREEN | FOREGROUND_INTENSITY,  # Зеленый
    ]
    
    current_color_index = 0
    
    def set_green_color():
        global current_color_index
        kernel32.SetConsoleTextAttribute(handle, green_colors[current_color_index])
        current_color_index = (current_color_index + 1) % len(green_colors)
    
    def reset_color():
        kernel32.SetConsoleTextAttribute(handle, FOREGROUND_LIGHT_GREEN)
    
    def set_console_title(title):
        kernel32.SetConsoleTitleW(title)
        
else:
    # Для Linux/Mac - коды ANSI для зеленых оттенков
    green_colors = [
        '\033[92m',  # Яркий зеленый
        '\033[32m',  # Зеленый
        '\033[92m',  # Яркий зеленый
        '\033[32m',  # Зеленый
    ]
    
    current_color_index = 0
    
    def set_green_color():
        global current_color_index
        print(green_colors[current_color_index], end='')
        current_color_index = (current_color_index + 1) % len(green_colors)
    
    def reset_color():
        print('\033[92m', end='')
    
    def set_console_title(title):
        print(f'\033]0;{title}\007', end='')

def green_print(text):
    set_green_color()
    print(text)
    reset_color()

def green_print_gradient(text):
    """Печатает текст с эффектом градиента"""
    lines = text.split('\n')
    for line in lines:
        if line.strip():  # Только для непустых строк
            green_print(line)
        else:
            print(line)

def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [url.strip() for url in file if url.strip()]

def save_proxies_to_file(proxies, file_path):
    with open(file_path, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy}\n")

async def fetch_proxy_list(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 200:
                content = await response.read()
                text = content.decode('utf-8', errors='ignore')
                return text.strip().split('\n')
            else:
                green_print(f"Ошибка при загрузке данных с {url}: HTTP {response.status}")
                return []
    except Exception as e:
        green_print(f"Ошибка при соединении с {url}: {e}")
        return []

def filter_proxies(proxy_lines):
    pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$'
    filtered = []
    for line in proxy_lines:
        line = line.strip()
        if not line:
            continue
        # Разделяем строку по пробелам/табуляциям и берем первую часть
        parts = line.split()
        if parts:
            proxy_candidate = parts[0]
            if re.match(pattern, proxy_candidate):
                filtered.append(proxy_candidate)
    return filtered

async def collect_proxies(proxy_type, source_dir, proxy_dir):
    proxy_files = {
        "1": ("http.txt", "http_proxies.txt"),
        "2": ("socks4.txt", "socks4_proxies.txt"),
        "3": ("socks5.txt", "socks5_proxies.txt")
    }
    
    if proxy_type not in proxy_files:
        green_print("Неверный выбор.")
        return
    
    urls_file, proxies_file = proxy_files[proxy_type]
    urls_file_path = os.path.join(source_dir, urls_file)
    
    if not os.path.exists(urls_file_path):
        green_print(f"Файл с источниками не найден: {urls_file_path}")
        return
    
    urls = read_urls_from_file(urls_file_path)
    
    green_print(f"\nЗагружаем прокси из {len(urls)} источников...")
    
    all_proxy_lines = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_proxy_list(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        all_proxy_lines = results
    
    # Преобразуем в плоский список
    flat_proxy_lines = [line for sublist in all_proxy_lines for line in sublist]
    green_print(f"Получено {len(flat_proxy_lines)} строк прокси")
    
    filtered_proxies = filter_proxies(flat_proxy_lines)
    green_print(f"После фильтрации: {len(filtered_proxies)} прокси")
    
    unique_proxies_sorted = sorted(set(filtered_proxies))
    green_print(f"Уникальных прокси: {len(unique_proxies_sorted)}")
    
    proxies_file_path = os.path.join(proxy_dir, proxies_file)
    save_proxies_to_file(unique_proxies_sorted, proxies_file_path)
    green_print(f"Уникальные прокси сохранены в файл '{proxies_file_path}'.")

async def main():
    # Устанавливаем название окна
    set_console_title(" ඩ Proxy Collector ツ | By lolz.live/members/8522994/ | github.com/Deletewindows ")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Создаем структуру папок
    source_dir = os.path.join(script_dir, "source")
    proxy_dir = os.path.join(script_dir, "proxy")
    
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(proxy_dir, exist_ok=True)
    
    # URL источники
    http_urls = [
        "https://raw.githubusercontent.com/ObcbO/getproxy/master/file/http.txt",
        "https://raw.githubusercontent.com/ObcbO/getproxy/master/file/https.txt",
        "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt",
        "https://raw.githubusercontent.com/casals-ar/proxy-list/main/http",
        "https://raw.githubusercontent.com/casals-ar/proxy-list/main/https",
        "https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt",
        "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
        "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
        "https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/http.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/http_proxies.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ]
    
    socks4_urls = [
        "https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks4.txt",
        "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
        "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt",
        "https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks4",
        "https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks4/global/socks4_checked.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt",
        "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
        "https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/socks4.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/socks4_proxies.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt"
    ]
    
    socks5_urls = [
        "https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks5.txt",
        "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
        "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt",
        "https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks5",
        "https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks5/global/socks5_checked.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt",
        "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
        "https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/socks5.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/socks5_proxies.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"
    ]
    
    # Создаем файлы с URL в папке source, если они не существуют
    def create_url_file(file_path, urls):
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                for url in urls:
                    f.write(f"{url}\n")
            green_print(f"Создан файл {file_path}")
    
    create_url_file(os.path.join(source_dir, "http.txt"), http_urls)
    create_url_file(os.path.join(source_dir, "socks4.txt"), socks4_urls)
    create_url_file(os.path.join(source_dir, "socks5.txt"), socks5_urls)
    
    # Главный цикл программы
    while True:
        banner = r"""
    ═══════════════════════════════════════════════════════════════
      ______                    _____      ____         ______               __   _ 
     / ____/___ _____ ___  ___ / ___/___  / / /__  ____/_  __/__  ____ ___  / /__(_)
    / / __/ __ `/ __ `__ \/ _ \\__ \/ _ \/ / / _ \/ ___// / / _ \/ __ `__ \/ //_/ / 
   / /_/ / /_/ / / / / / /  __/__/ /  __/ / /  __/ /   / / /  __/ / / / / / ,< / /  
   \____/\__,_/_/ /_/ /_/\___/____/\___/_/_/\___/_/   /_/  \___/_/ /_/ /_/_/|_/_/   

                     ● ПРОГРАММА ДЛЯ СБОРА ПРОКСИ ●
    ═══════════════════════════════════════════════════════════════
        """
        
        green_print_gradient(banner)
        green_print("● Выберите тип прокси:")
        green_print("1 - HTTP прокси")
        green_print("2 - SOCKS4 прокси") 
        green_print("3 - SOCKS5 прокси")
        green_print("0 - Выход из программы")
        green_print("═" * 67)
        
        choice = input("➤ Введите номер опции: ").strip()
        
        if choice == "0":
            green_print("➤ Выход из программы...")
            break
        elif choice in ["1", "2", "3"]:
            await collect_proxies(choice, source_dir, proxy_dir)
        else:
            green_print(" ☹ Неверный выбор. Пожалуйста, выберите 1, 2, 3 или 0 для выхода.")

if __name__ == '__main__':
    asyncio.run(main())
