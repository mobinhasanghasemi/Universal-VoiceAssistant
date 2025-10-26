import os
import sys
import time
import datetime
import webbrowser
import subprocess
from typing import Dict, List, Optional
import speech_recognition as sr
import screen_brightness_control as sbc
import psutil
from plyer import notification
from urllib.parse import quote
import pyjokes
import pyttsx3

# ==================== تنظیمات اولیه ====================
class VoiceAssistant:
    def __init__(self):
        """مقداردهی اولیه دستیار صوتی"""
        # تنظیمات تشخیص گفتار
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # تنظیمات موتور صوتی
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            # انتخاب صدای انگلیسی
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower() or 'zira' in voice.name.lower() or 'david' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            else:
                self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex' if sys.platform == 'darwin' else 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0')
        except Exception as e:
            print(f"⚠️ خطا در راه‌اندازی pyttsx3: {str(e)}")
            self.engine = None

        # تنظیمات کاربر
        self.user_name = "کاربر"
        self.assistant_name = "دستیار صوتی"
        self.language = "fa-IR"
        self.supported_languages = ["fa-IR", "en-US"]
        
        # حالت‌های سیستم
        self.sleep_mode = False
        self.debug_mode = False
        
        # دیکشنری دستورات
        self.commands = self._setup_commands()
        
        # بررسی وجود میکروفون
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
            self._notify_response("✅ میکروفون شناسایی شد", "Microphone detected")
        except Exception as e:
            self._notify_response(f"⚠️ خطای میکروفون: {str(e)}. لطفاً میکروفون را بررسی کنید.", f"Microphone error: {str(e)}. Please check your microphone.")
            sys.exit(1)

    # ==================== دیکشنری دستورات ====================
    def _setup_commands(self) -> Dict[str, List[str]]:
        """تنظیم دیکشنری دستورات با کلمات کلیدی گسترده"""
        return {
            "خروج": ["خروج", "بستن", "تمام", "خاموش", "exit", "quit", "stop", "پایان", "برو", "متوقف"],
            "خواب": ["خواب", "استراحت", "sleep", "راحت"],
            "بیدار": ["بیدار", "wake", "فعال", "برخاست"],
            "ریستارت": ["ریستارت", "restart", "ریست", "reboot", "دوباره راه‌اندازی"],
            "خاموش": ["خاموش", "shutdown", "بشین"],
            "قفل": ["قفل", "lock", "ببند"],
            "نوتیفیکیشن": ["نوتیفیکیشن", "notification", "اعلان", "هشدار", "پیغام"],
            "مرورگر": ["مرورگر", "کروم", "chrome", "فایرفاکس", "firefox", "اج", "edge", "اوپرا", "opera", "سافاری", "safari"],
            "جستجو": ["جستجو", "search", "گوگل", "google", "سرچ", "بینگ", "bing", "پیدا کن"],
            "یوتیوب": ["یوتیوب", "youtube", "yt"],
            "ویکی‌پدیا": ["ویکی‌پدیا", "wikipedia", "ویکی", "دانشنامه"],
            "گیتهاب": ["گیتهاب", "github", "گیت"],
            "توییتر": ["توییتر", "twitter", "ایکس", "x"],
            "اینستاگرام": ["اینستاگرام", "instagram", "اینستا"],
            "تلگرام": ["تلگرام", "telegram"],
            "واتساپ": ["واتساپ", "whatsapp"],
            "چت": ["چت", "گپ", "پیام", "chat", "گفتگو"],
            "ترجمه": ["ترجمه", "translate", "مترجم"],
            "موسیقی": ["موسیقی", "موزیک", "music", "آهنگ", "اسپاتیفای", "spotify"],
            "ویدیو": ["ویدیو", "فیلم", "movie", "vlc", "kmplayer"],
            "نوت‌پد": ["نوت‌پد", "notepad", "یادداشت", "متن"],
            "ورد": ["ورد", "word"],
            "اکسل": ["اکسل", "excel", "جدول"],
            "پاورپوینت": ["پاورپوینت", "powerpoint", "اسلاید"],
            "پینت": ["پینت", "paint", "نقاشی", "رسم"],
            "ماشین‌حساب": ["ماشین‌حساب", "calculator", "حساب"],
            "کامند": ["کامند", "cmd", "ترمینال"],
            "کد": ["کد", "vscode", "code"],
            "فوتوشوب": ["فوتوشوب", "photoshop"],
            "پریمیر": ["پریمیر", "premiere"],
            "دوربین": ["دوربین", "camera", "وب‌کم"],
            "نقشه": ["نقشه", "map", "گوگل‌مپ"],
            "دسکتاپ": ["دسکتاپ", "desktop"],
            "فایل": ["فایل", "explorer", "پوشه"],
            "تسک": ["تسک", "task", "مدیریت"],
            "تنظیمات": ["تنظیمات", "settings"],
            "شبکه": ["شبکه", "network", "وای‌فای", "wifi"],
            "بلوتوث": ["بلوتوث", "bluetooth"],
            "زمان": ["زمان", "ساعت", "time"],
            "تاریخ": ["تاریخ", "date", "امروز"],
            "حافظه": ["حافظه", "memory", "رم", "ram"],
            "پردازنده": ["پردازنده", "cpu"],
            "باتری": ["باتری", "battery", "شارژ"],
            "روشنایی": ["روشنایی", "brightness", "نور"],
            "زیاد": ["زیاد", "افزایش", "increase", "up", "بلند", "بیشتر"],
            "کاهش": ["کاهش", "کم", "decrease", "down", "پایین", "کمتر"],
            "اسم": ["اسم", "نام", "name"],
            "دیباگ": ["دیباگ", "debug", "تست"],
            "پاکسازی": ["پاکسازی", "clear", "پاک"],
            "آب‌وهوا": ["هوا", "آب‌وهوا", "weather"],
            "یادداشت": ["یادداشت", "نوت", "note"],
            "کش": ["کش", "cache", "موقت"],
            "تست": ["تست", "میکروفون", "mic"],
            "جوک": ["جوک", "جک", "joke"],
            "و": ["و", "همچنین", "and", "هم", "بعلاوه", "همراه", "به‌علاوه"],
            "ولی": ["ولی", "اما", "but", "با این حال", "هرچند", "در عوض", "بلکه"],
            "نه": ["نه", "خیر", "no", "نکن", "نه خیر", "اصلاً", "ابداً", "هرگز", "رد", "لغو", "cancel", "never", "nope", "نمی‌خوام", "منفی"],
            "زبان": ["زبان", "language", "انگلیسی", "فارسی", "english", "persian"],
            "باز": ["باز", "open", "اجرا", "شروع", "بزن"],
            "انجام": ["انجام", "do", "انجام بده", "بکن", "اجرا کن"],
        }

    # ==================== توابع کمکی ====================
    def _notify_response(self, text: str, tts_text: str) -> None:
        """نمایش پیام در کنسول و نوتیفیکیشن به فارسی، و پخش صوتی به انگلیسی"""
        print(f"🤖 {self.assistant_name}: {text}")
        notification.notify(
            title=self.assistant_name,
            message=text,
            timeout=10
        )
        if self.engine:
            try:
                self.engine.say(tts_text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️ خطا در پخش صوتی: {str(e)}")
        time.sleep(2)

    def _detect_language(self, text: Optional[str]) -> str:
        """تشخیص زبان ورودی"""
        if not text:
            return self.language
        if any(word in text for word in ["exit", "search", "open", "and", "but", "no", "language", "english"]):
            return "en-US"
        return "fa-IR"

    # ==================== تشخیص گفتار ====================
    def recognize_speech(self) -> Optional[str]:
        """شنیدن صدای کاربر و تبدیل به متن"""
        with sr.Microphone() as source:
            try:
                if not self.sleep_mode:
                    self._notify_response("🎤 در حال گوش دادن... (برای خروج بگویید 'خروج' یا 'exit')", "Listening... Say 'exit' to stop")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=20, phrase_time_limit=30)
                text = self.recognizer.recognize_google(audio, language=self.language)
                self._notify_response(f"👤 {self.user_name}: {text}", f"User said: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                if not self.sleep_mode:
                    self._notify_response("⏳ بدون ورودی صوتی. لطفاً صحبت کنید.", "No voice input detected. Please speak.")
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                self._notify_response(f"⚠️ خطای سرویس تشخیص گفتار: {str(e)}. اینترنت را بررسی کنید.", f"Speech recognition service error: {str(e)}. Check your internet.")
                return None
            except Exception as e:
                self._notify_response(f"⚠️ خطای میکروفون: {str(e)}. میکروفون را بررسی کنید.", f"Microphone error: {str(e)}. Check your microphone.")
                return None

    # ==================== پردازش دستورات ====================
    def process_command(self, command: str) -> bool:
        """پردازش دستورات با پشتیبانی پیشرفته از دستورات ترکیبی"""
        if not command:
            return False

        self.language = self._detect_language(command)
        words = command.split()
        actions = []
        i = 0
        while i < len(words):
            word = words[i]
            if word in self.commands["خروج"]:
                self._notify_response(f"🛑 خدانگهدار {self.user_name}!", f"Goodbye {self.user_name}!")
                return True

            if word in self.commands["خواب"]:
                self._notify_response("💤 به حالت خواب می‌روم. برای بیدار کردن بگویید 'بیدار'", "Going to sleep mode. Say 'wake' to activate.")
                self.sleep_mode = True
                return False

            if word in self.commands["بیدار"]:
                self._notify_response("🌞 بیدار شدم! چه دستوری دارید؟", "I'm awake! What's your command?")
                self.sleep_mode = False
                return False

            if word in self.commands["زبان"]:
                if any(w in words for w in ["انگلیسی", "english"]):
                    self.language = "en-US"
                    self._notify_response("زبان تشخیص گفتار به انگلیسی تنظیم شد", "Speech recognition language set to English")
                elif any(w in words for w in ["فارسی", "persian"]):
                    self.language = "fa-IR"
                    self._notify_response("زبان تشخیص گفتار به فارسی تنظیم شد", "Speech recognition language set to Persian")
                return False

            if self.sleep_mode:
                return False

            # پردازش دستورات ترکیبی
            if word in self.commands["نه"]:
                actions = actions[:-1] if actions else actions  # حذف آخرین دستور
                i += 1
                continue
            if word in self.commands["ولی"]:
                actions = []  # پاک کردن دستورات قبلی
                i += 1
                continue
            if word in self.commands["و"]:
                i += 1
                continue

            for action, keywords in self.commands.items():
                if word in keywords and action not in ["نه", "ولی", "و", "باز", "انجام"]:
                    # اگر کلمه بعدی "باز" یا "انجام" باشد، آن را هم در نظر بگیر
                    if i + 1 < len(words) and words[i + 1] in self.commands["باز"] + self.commands["انجام"]:
                        i += 1
                    actions.append((action, word))
                    break
            i += 1

        try:
            if not actions:
                self._notify_response("⛔ دستور ناشناخته. لطفاً دستور معتبر بگویید.", "Unknown command. Please provide a valid command.")
                return False

            for action, trigger_word in actions:
                self._notify_response(f"🔹 تشخیص دستور: {action}", f"Detected command: {action}")
                self._execute_command(action, command, trigger_word)
            return False
        except Exception as e:
            self._notify_response(f"⚠️ خطا در اجرای دستور: {str(e)}", f"Error executing command: {str(e)}")
            if self.debug_mode:
                print(f"⚠️ خطا: {str(e)}")
            return False

    def _execute_search(self, command: str) -> bool:
        """اجرای جستجوی مداوم تا دستور خروج"""
        while True:
            search_type = "google"
            tts_search_type = "Google"
            if any(w in command for w in self.commands["یوتیوب"]):
                search_type = "youtube"
                tts_search_type = "YouTube"
            elif any(w in command for w in self.commands["ویکی‌پدیا"]):
                search_type = "wikipedia"
                tts_search_type = "Wikipedia"

            self._notify_response(f"🔍 {search_type} باز شد. چه چیزی را می‌خواهید جستجو کنید؟", f"{tts_search_type} is opened. What would you like to search for?")
            with sr.Microphone() as source:
                self._notify_response("🎤 در حال گوش دادن برای عبارت جستجو...", "Listening for search query...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=20, phrase_time_limit=30)
            try:
                search_query = self.recognizer.recognize_google(audio, language=self.language)
                self._notify_response(f"📜 عبارت جستجو: {search_query}", f"Search query: {search_query}")

                if any(word in search_query.lower() for word in self.commands["خروج"]):
                    self._notify_response("🛑 خروج از حالت جستجو", "Exiting search mode")
                    return False

                if search_type == "youtube":
                    url = f"https://www.youtube.com/results?search_query={quote(search_query)}"
                elif search_type == "wikipedia":
                    url = f"https://{'fa' if self.language == 'fa-IR' else 'en'}.wikipedia.org/wiki/{quote(search_query)}"
                else:
                    url = f"https://www.google.com/search?q={quote(search_query)}"

                webbrowser.open(url)
                self._notify_response(f"🌐 در حال جستجو برای {search_query} در {search_type}", f"Searching for {search_query} in {tts_search_type}")
                
                self._notify_response("🔍 برای جستجوی دوباره صحبت کنید یا بگویید 'خروج'", "Speak again to search or say 'exit'")
                command = self.recognize_speech()
                if not command or any(word in command for word in self.commands["خروج"]):
                    self._notify_response("🛑 خروج از حالت جستجو", "Exiting search mode")
                    return False
            except sr.UnknownValueError:
                continue
            except Exception as e:
                self._notify_response(f"⚠️ خطا در جستجو: {str(e)}", f"Search error: {str(e)}")
                return False

    def _execute_command(self, action: str, command: str, trigger_word: str) -> bool:
        """اجرای دستورات خاص"""
        try:
            if action == "جستجو":
                return self._execute_search(command)

            elif action == "مرورگر":
                webbrowser.open("https://www.google.com")
                self._notify_response("🌐 مرورگر باز شد", "Browser opened")

            elif action == "یوتیوب":
                webbrowser.open("https://www.youtube.com")
                self._notify_response("📹 یوتیوب باز شد", "YouTube opened")

            elif action == "ویکی‌پدیا":
                webbrowser.open("https://fa.wikipedia.org" if self.language == "fa-IR" else "https://en.wikipedia.org")
                self._notify_response("📚 ویکی‌پدیا باز شد", "Wikipedia opened")

            elif action == "گیتهاب":
                webbrowser.open("https://github.com")
                self._notify_response("💻 گیتهاب باز شد", "GitHub opened")

            elif action == "توییتر":
                webbrowser.open("https://x.com")
                self._notify_response("🐦 توییتر باز شد", "Twitter opened")

            elif action == "اینستاگرام":
                webbrowser.open("https://www.instagram.com")
                self._notify_response("📷 اینستاگرام باز شد", "Instagram opened")

            elif action == "تلگرام":
                webbrowser.open("https://web.telegram.org")
                self._notify_response("💬 تلگرام باز شد", "Telegram opened")

            elif action == "واتساپ":
                webbrowser.open("https://web.whatsapp.com")
                self._notify_response("📱 واتساپ باز شد", "WhatsApp opened")

            elif action == "چت":
                webbrowser.open("https://web.whatsapp.com")
                self._notify_response("💬 چت باز شد", "Chat opened")

            elif action == "ترجمه":
                webbrowser.open("https://translate.google.com")
                self._notify_response("🌍 مترجم گوگل باز شد", "Google Translate opened")

            elif action == "موسیقی":
                os.system("start wmplayer")
                self._notify_response("🎵 پخش‌کننده موسیقی باز شد", "Music player opened")

            elif action == "ویدیو":
                os.system("start vlc")
                self._notify_response("📽️ پخش‌کننده ویدیو باز شد", "Video player opened")

            elif action == "نوت‌پد":
                os.system("start notepad")
                self._notify_response("📝 نوت‌پد باز شد", "Notepad opened")

            elif action == "ورد":
                os.system("start winword")
                self._notify_response("📄 مایکروسافت ورد باز شد", "Microsoft Word opened")

            elif action == "اکسل":
                os.system("start excel")
                self._notify_response("📊 مایکروسافت اکسل باز شد", "Microsoft Excel opened")

            elif action == "پاورپوینت":
                os.system("start powerpnt")
                self._notify_response("📽️ مایکروسافت پاورپوینت باز شد", "Microsoft PowerPoint opened")

            elif action == "پینت":
                os.system("start mspaint")
                self._notify_response("🎨 پینت باز شد", "Paint opened")

            elif action == "ماشین‌حساب":
                os.system("start calc")
                self._notify_response("🔢 ماشین حساب باز شد", "Calculator opened")

            elif action == "کامند":
                os.system("start cmd")
                self._notify_response("💻 خط فرمان باز شد", "Command prompt opened")

            elif action == "کد":
                os.system("start code")
                self._notify_response("💻 ویژوال استودیو کد باز شد", "Visual Studio Code opened")

            elif action == "فوتوشوب":
                os.system("start photoshop")
                self._notify_response("🖌️ فوتوشوب باز شد", "Photoshop opened")

            elif action == "پریمیر":
                os.system("start premiere")
                self._notify_response("🎬 پریمیر باز شد", "Premiere opened")

            elif action == "دوربین":
                os.system("start microsoft.windows.camera:")
                self._notify_response("📸 دوربین باز شد", "Camera opened")

            elif action == "نقشه":
                webbrowser.open("https://www.google.com/maps")
                self._notify_response("🗺️ گوگل مپ باز شد", "Google Maps opened")

            elif action == "دسکتاپ":
                os.system("explorer shell:::{3080F90D-D7AD-11D9-BD98-0000947B0257}")
                self._notify_response("🖥️ نمایش دسکتاپ", "Show desktop")

            elif action == "فایل":
                os.system("start explorer")
                self._notify_response("📁 فایل منیجر باز شد", "File explorer opened")

            elif action == "تسک":
                os.system("start taskmgr")
                self._notify_response("⚙️ تسک منیجر باز شد", "Task manager opened")

            elif action == "تنظیمات":
                os.system("start ms-settings:")
                self._notify_response("⚙️ تنظیمات ویندوز باز شد", "Windows settings opened")

            elif action == "شبکه":
                os.system("start ms-settings:network-status")
                self._notify_response("🌐 تنظیمات شبکه باز شد", "Network settings opened")

            elif action == "بلوتوث":
                os.system("start ms-settings:bluetooth")
                self._notify_response("📡 تنظیمات بلوتوث باز شد", "Bluetooth settings opened")

            elif action == "زمان":
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                self._notify_response(f"⏰ ساعت فعلی: {current_time}", f"Current time: {current_time}")

            elif action == "تاریخ":
                current_date = datetime.datetime.now().strftime("%Y/%m/%d")
                self._notify_response(f"📅 تاریخ امروز: {current_date}", f"Today's date: {current_date}")

            elif action == "حافظه":
                memory = psutil.virtual_memory()
                self._notify_response(f"🧠 حافظه رم: {memory.percent}% استفاده شده", f"RAM usage: {memory.percent}%")

            elif action == "پردازنده":
                cpu = psutil.cpu_percent()
                self._notify_response(f"⚙️ استفاده از پردازنده: {cpu}%", f"CPU usage: {cpu}%")

            elif action == "باتری":
                battery = psutil.sensors_battery()
                if battery:
                    self._notify_response(f"🔋 درصد باتری: {battery.percent}%", f"Battery level: {battery.percent}%")
                else:
                    self._notify_response("⚠️ اطلاعات باتری در دسترس نیست", "Battery information not available")

            elif action == "روشنایی" or action == "زیاد":
                try:
                    current_brightness = sbc.get_brightness()
                    if isinstance(current_brightness, list):
                        current_brightness = current_brightness[0]
                    sbc.set_brightness(min(current_brightness + 10, 100))
                    self._notify_response("💡 روشنایی افزایش یافت", "Brightness increased")
                except Exception as e:
                    self._notify_response(f"⚠️ خطا در تنظیم روشنایی: {str(e)}", f"Error adjusting brightness: {str(e)}")

            elif action == "کاهش":
                try:
                    current_brightness = sbc.get_brightness()
                    if isinstance(current_brightness, list):
                        current_brightness = current_brightness[0]
                    sbc.set_brightness(max(current_brightness - 10, 0))
                    self._notify_response("💡 روشنایی کاهش یافت", "Brightness decreased")
                except Exception as e:
                    self._notify_response(f"⚠️ خطا در تنظیم روشنایی: {str(e)}", f"Error adjusting brightness: {str(e)}")

            elif action == "نوتیفیکیشن":
                self._notify_response("🔔 این یک اعلان تست است!", "This is a test notification!")

            elif action == "اسم":
                words = command.split()
                name_index = words.index("اسم") + 1 if "اسم" in words else -1
                if name_index != -1 and name_index < len(words):
                    self.user_name = words[name_index]
                    self._notify_response(f"👤 نام شما به {self.user_name} تغییر کرد", f"Your name changed to {self.user_name}")
                else:
                    self._notify_response(f"👤 نام فعلی شما: {self.user_name}", f"Your current name: {self.user_name}")

            elif action == "دیباگ":
                self.debug_mode = not self.debug_mode
                self._notify_response(f"🔍 حالت دیباگ: {'فعال' if self.debug_mode else 'غیرفعال'}", f"Debug mode: {'enabled' if self.debug_mode else 'disabled'}")

            elif action == "پاکسازی":
                os.system("cls" if os.name == "nt" else "clear")
                self._notify_response("🧹 کنسول پاک شد", "Console cleared")

            elif action == "جوک":
                joke = pyjokes.get_joke()
                self._notify_response(joke, joke)

            elif action == "ریستارت":
                os.system("shutdown /r /t 1")
                self._notify_response("🔄 سیستم در حال ریستارت...", "System restarting...")

            elif action == "خاموش":
                os.system("shutdown /s /t 1")
                self._notify_response("🛑 سیستم در حال خاموش شدن...", "System shutting down...")

            elif action == "قفل":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                self._notify_response("🔒 سیستم قفل شد", "System locked")

            elif action == "آب‌وهوا":
                webbrowser.open("https://www.accuweather.com")
                self._notify_response("🌤️ سایت آب‌وهوا باز شد", "Weather site opened")

            elif action == "یادداشت":
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                note_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', f'note_{timestamp}.txt')
                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write("یادداشت جدید\n")
                os.system(f"start notepad {note_path}")
                self._notify_response(f"📝 یادداشت جدید در {note_path} ایجاد شد", f"New note created at {note_path}")

            elif action == "کش":
                try:
                    os.system("del /q /s %temp%\\*")
                    self._notify_response("🧹 فایل‌های کش موقت پاک شدند", "Temporary cache files cleared")
                except Exception as e:
                    self._notify_response(f"⚠️ خطا در پاکسازی کش: {str(e)}", f"Error clearing cache: {str(e)}")

            elif action == "تست":
                self._notify_response("🎤 لطفاً چیزی بگویید تا میکروفون تست شود...", "Please say something to test the microphone...")
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                try:
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    self._notify_response(f"✅ میکروفون کار می‌کند! شنیدم: {text}", f"Microphone works! I heard: {text}")
                except Exception as e:
                    self._notify_response(f"⚠️ خطا در تست میکروفون: {str(e)}", f"Microphone test error: {str(e)}")

            return False
        except Exception as e:
            self._notify_response(f"⚠️ خطا در اجرای دستور: {str(e)}", f"Error executing command: {str(e)}")
            if self.debug_mode:
                print(f"⚠️ خطا: {str(e)}")
            return False

    # ==================== اجرای اصلی برنامه ====================
    def run(self):
        """اجرای حلقه اصلی برنامه"""
        self._notify_response(f"🌟 {self.assistant_name} فعال شد", f"{self.assistant_name} activated")
        self._notify_response("=====================================", "=====================================")
        
        while True:
            command = self.recognize_speech()
            if self.process_command(command):
                break

if __name__ == "__main__":
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"⚠️ خطا در راه‌اندازی برنامه: {str(e)}")