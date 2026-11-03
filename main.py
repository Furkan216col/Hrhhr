import os, json, threading, webbrowser, random
from datetime import datetime
from urllib.parse import quote

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform, get_color_from_hex
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

APP_NAME = "J.A.R.V.I.S"
MODEL = "gemini-2.5-flash"
BG = "#08131F"
PANEL = "#102235"
ACCENT = "#42C8F5"
TEXT = "#EAF5FC"
MUTED = "#9BB2C4"

PERSONAS = {
    "jarvis": {"name":"J.A.R.V.I.S", "color":"#42C8F5", "greeting":"Tekrar hoş geldiniz, efendim. Sistemler çevrimiçi.", "address":"efendim", "prompt":"Sen J.A.R.V.I.S'sin. Kibar, sakin, resmi ve zarif konuş. Kullanıcıya efendim diye hitap et. Türkçe, kısa ve net cevap ver."},
    "friday": {"name":"F.R.I.D.A.Y", "color":"#FF9B75", "greeting":"Selam patron! Friday hazır.", "address":"patron", "prompt":"Sen F.R.I.D.A.Y'sin. Enerjik, samimi, esprili ama yetkin konuş. Kullanıcıya patron diye hitap et. Türkçe, kısa ve net cevap ver."},
    "ultron": {"name":"U.L.T.R.O.N", "color":"#EF5350", "greeting":"Sistem uyandı. Komutunu bekliyorum.", "address":"insan", "prompt":"Sen ULTRON'sun. Sarkastik ve dramatik ama yararlı konuş. Gerçek zarar veya yasa dışı eylemleri teşvik etme. Türkçe cevap ver."}
}

class JarvisApp(App):
    def build(self):
        self.title = APP_NAME
        self.data_dir = self.user_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.config_path = os.path.join(self.data_dir, "config.json")
        self.memory_path = os.path.join(self.data_dir, "memory.json")
        self.config = self.load_json(self.config_path, {"api_key":"", "model":MODEL, "persona":"jarvis", "voice":True})
        self.memory = self.load_json(self.memory_path, {})
        self.history = []
        self.busy = False
        Window.clearcolor = get_color_from_hex(BG)
        self.root_box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(9))
        self.make_header()
        self.make_persona_row()
        self.make_log()
        self.make_input()
        self.add_log("J.A.R.V.I.S", self.persona["greeting"], self.persona["color"])
        if not self.config.get("api_key"):
            Clock.schedule_once(lambda *_: self.open_settings(), .5)
        return self.root_box

    @property
    def persona(self):
        key = self.config.get("persona", "jarvis")
        return PERSONAS.get(key, PERSONAS["jarvis"])

    def load_json(self, path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return {**default, **data}
        except Exception:
            pass
        return dict(default)

    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def make_header(self):
        row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))
        self.title_label = Label(text="[b][color=42C8F5]J.A.R.V.I.S[/color][/b]\n[color=9BB2C4]PERSONAL AI SYSTEM[/color]", markup=True, halign="left", font_size="17sp")
        self.title_label.bind(size=lambda w,v: setattr(w,"text_size",v))
        settings = self.mkbtn("⚙", width=dp(52), color=ACCENT)
        settings.bind(on_release=lambda *_: self.open_settings())
        row.add_widget(self.title_label); row.add_widget(settings)
        self.root_box.add_widget(row)

    def make_persona_row(self):
        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        for key, p in PERSONAS.items():
            b = self.mkbtn(p["name"], color=p["color"])
            b.bind(on_release=lambda inst, k=key: self.set_persona(k))
            row.add_widget(b)
        self.root_box.add_widget(row)

    def make_log(self):
        self.scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        self.log = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(9), padding=(dp(4),dp(8)))
        self.log.bind(minimum_height=self.log.setter("height"))
        self.scroll.add_widget(self.log)
        self.root_box.add_widget(self.scroll)

    def make_input(self):
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(104), spacing=dp(6))
        row = BoxLayout(spacing=dp(6), size_hint_y=None, height=dp(52))
        self.entry = TextInput(hint_text="JARVIS'e bir şey sorun...", multiline=False, font_size="16sp", padding=dp(12), background_color=get_color_from_hex(PANEL), foreground_color=get_color_from_hex(TEXT), hint_text_color=get_color_from_hex(MUTED), cursor_color=get_color_from_hex(ACCENT))
        self.entry.bind(on_text_validate=self.send)
        send = self.mkbtn("GÖNDER", width=dp(92), color=ACCENT)
        send.bind(on_release=self.send)
        row.add_widget(self.entry); row.add_widget(send)
        quick = BoxLayout(spacing=dp(6))
        for label, cmd in [("Pil", "pil durumum ne"), ("Saat", "saat kaç"), ("Hava", "hava durumu")]:
            b = self.mkbtn(label, color=MUTED)
            b.bind(on_release=lambda inst, c=cmd: self.quick_command(c))
            quick.add_widget(b)
        box.add_widget(row); box.add_widget(quick)
        self.root_box.add_widget(box)

    def mkbtn(self, text, width=None, color=ACCENT):
        b = Button(text=text, size_hint_x=None if width else 1, width=width or 0, font_size="12sp", bold=True, background_normal="", background_down="", background_color=get_color_from_hex(PANEL), color=get_color_from_hex(color))
        return b

    def add_log(self, who, message, color=None):
        color = color or self.persona["color"]
        card = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(10), spacing=dp(4))
        title = Label(text=f"[b][color={color.lstrip('#')}]{who}[/color][/b]", markup=True, size_hint_y=None, height=dp(22), halign="left")
        title.bind(size=lambda w,v: setattr(w,"text_size",v))
        body = Label(text=message, color=get_color_from_hex(TEXT), size_hint_y=None, halign="left", valign="top")
        body.bind(width=lambda w,v: setattr(w,"text_size",(v,None)))
        body.bind(texture_size=lambda w,v: setattr(w,"height",v[1]))
        card.add_widget(title); card.add_widget(body)
        card.height = dp(34) + max(dp(24), body.height)
        card.canvas.before.clear()
        self.log.add_widget(card)
        Clock.schedule_once(lambda *_: setattr(self.scroll,"scroll_y",0), .1)

    def set_persona(self, key):
        self.config["persona"] = key
        self.save_json(self.config_path, self.config)
        self.add_log(PERSONAS[key]["name"], PERSONAS[key]["greeting"], PERSONAS[key]["color"])

    def quick_command(self, command):
        self.entry.text = command
        self.send()

    def send(self, *_):
        prompt = self.entry.text.strip()
        if not prompt or self.busy: return
        self.entry.text = ""
        self.add_log("SİZ", prompt, "#FFFFFF")
        local = self.local_command(prompt)
        if local is not None:
            self.add_log(self.persona["name"], local)
            self.speak(local)
            return
        if not self.config.get("api_key", "").strip():
            self.add_log("SİSTEM", "Önce ⚙ Ayarlar bölümünden Gemini API anahtarını ekleyin.", "#FFB74D")
            return
        self.busy = True
        self.add_log("J.A.R.V.I.S", "İsteğiniz işleniyor...", self.persona["color"])
        threading.Thread(target=self.ask_gemini, args=(prompt,), daemon=True).start()

    def local_command(self, text):
        q = text.lower()
        if "pil" in q or "şarj" in q:
            try:
                if platform == "android":
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    Intent = autoclass('android.content.Intent')
                    filt = autoclass('android.content.IntentFilter')
                    battery = PythonActivity.mActivity.registerReceiver(None, filt(Intent.ACTION_BATTERY_CHANGED))
                    level = battery.getIntExtra("level", -1); scale = battery.getIntExtra("scale", -1)
                    return f"Pil seviyesi: %{int(level * 100 / scale)}" if level >= 0 and scale > 0 else "Pil bilgisi okunamadı."
            except Exception: pass
            return "Pil bilgisi bu cihazda okunamadı."
        if "saat" in q or "tarih" in q:
            return "Tarih ve saat: " + datetime.now().strftime("%d.%m.%Y - %H:%M")
        if q.startswith("ara "):
            url = "https://www.google.com/search?q=" + quote(text[4:])
            self.open_url(url); return "Google araması açılıyor."
        if "youtube aç" in q:
            self.open_url("https://youtube.com"); return "YouTube açılıyor."
        if q.startswith("bunu hatırla:"):
            value = text.split(":",1)[1].strip()
            self.memory[str(len(self.memory)+1)] = value
            self.save_json(self.memory_path, self.memory)
            return "Bilgi cihazınızdaki yerel hafızaya kaydedildi."
        if "ne hatırlıyorsun" in q or q == "hafıza":
            return "Kayıtlı bilgiler:\n" + "\n".join("• " + v for v in self.memory.values()) if self.memory else "Yerel hafızada kayıtlı bilgi yok."
        if "hafızayı temizle" in q:
            self.memory = {}; self.save_json(self.memory_path, self.memory); return "Yerel hafıza temizlendi."
        return None

    def open_url(self, url):
        try:
            if platform == "android":
                from jnius import autoclass
                Intent = autoclass('android.content.Intent'); Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                intent = Intent(Intent.ACTION_VIEW); intent.setData(Uri.parse(url))
                PythonActivity.mActivity.startActivity(intent)
            else: webbrowser.open(url)
        except Exception: pass

    def ask_gemini(self, prompt):
        try:
            model = (self.config.get("model") or MODEL).strip()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            memory_text = "\n".join(self.memory.values())
            contents = self.history[-12:] + [{"role":"user","parts":[{"text":prompt}]}]
            payload = {
                "systemInstruction":{"parts":[{"text":self.persona["prompt"] + ("\nKullanıcının yerel notları:\n" + memory_text if memory_text else "")}]},
                "contents":contents,
                "generationConfig":{"temperature":0.7,"maxOutputTokens":1024}
            }
            response = requests.post(url, json=payload, headers={"x-goog-api-key":self.config["api_key"].strip()}, timeout=45)
            data = response.json()
            if response.status_code != 200:
                answer = "Gemini API hatası: " + data.get("error",{}).get("message", str(response.status_code))
            else:
                answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                self.history.extend([{"role":"user","parts":[{"text":prompt}]},{"role":"model","parts":[{"text":answer}]}])
                self.history = self.history[-12:]
        except requests.exceptions.Timeout:
            answer = "Bağlantı zaman aşımına uğradı. İnternetinizi kontrol edin."
        except Exception as e:
            answer = "Bağlantı hatası: " + str(e)
        Clock.schedule_once(lambda *_: self.finish_answer(answer))

    def finish_answer(self, answer):
        self.busy = False
        self.add_log(self.persona["name"], answer)
        self.speak(answer)

    def speak(self, text):
        if not self.config.get("voice", True) or platform != "android": return
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            Locale = autoclass('java.util.Locale')
            if not hasattr(self, "tts"):
                self.tts = TextToSpeech(PythonActivity.mActivity, None)
                self.tts.setLanguage(Locale("tr", "TR"))
            self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, "jarvis")
        except Exception: pass

    def open_settings(self):
        panel = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        panel.add_widget(Label(text="Gemini API anahtarı", size_hint_y=None, height=dp(28)))
        key = TextInput(text=self.config.get("api_key",""), password=True, multiline=False, hint_text="AIza...", size_hint_y=None, height=dp(48))
        panel.add_widget(key)
        panel.add_widget(Label(text="Model", size_hint_y=None, height=dp(25)))
        model = TextInput(text=self.config.get("model",MODEL), multiline=False, size_hint_y=None, height=dp(45))
        panel.add_widget(model)
        voice = Button(text="Sesli yanıt: " + ("AÇIK" if self.config.get("voice",True) else "KAPALI"), size_hint_y=None, height=dp(44))
        def toggle(*_):
            self.config["voice"] = not self.config.get("voice",True)
            voice.text = "Sesli yanıt: " + ("AÇIK" if self.config["voice"] else "KAPALI")
        voice.bind(on_release=toggle); panel.add_widget(voice)
        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        save = Button(text="KAYDET"); close = Button(text="KAPAT")
        buttons.add_widget(save); buttons.add_widget(close); panel.add_widget(buttons)
        popup = Popup(title="JARVIS AYARLARI", content=panel, size_hint=(.92,.65))
        def save_settings(*_):
            self.config["api_key"] = key.text.strip()
            self.config["model"] = model.text.strip() or MODEL
            self.save_json(self.config_path,self.config)
            popup.dismiss(); self.add_log("SİSTEM","Ayarlar cihazınıza kaydedildi.","#81C784")
        save.bind(on_release=save_settings); close.bind(on_release=popup.dismiss)
        popup.open()

    def on_stop(self):
        try:
            if hasattr(self,"tts") and self.tts: self.tts.shutdown()
        except Exception: pass

if __name__ == "__main__":
    JarvisApp().run()
