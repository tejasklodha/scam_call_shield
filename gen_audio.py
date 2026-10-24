# Generates the sample call audio with Gemini speech generation.
# Run from the scam-call-shield folder:  python3 gen_audio.py digital normal
import base64, json, os, re, sys, time, urllib.error, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(HERE, "public", "config.js"), encoding="utf-8").read()
KEY = re.search(r'API_KEY = "([^"]+)"', html).group(1)
MODEL = "gemini-2.5-flash-preview-tts"
OUT = os.path.join(HERE, "public", "audio")
os.makedirs(OUT, exist_ok=True)

VOICES = {"Officer": "Charon", "Uncle": "Iapetus", "Caller": "Fenrir", "Aunty": "Gacrux", "Delivery": "Puck"}
STYLE = {
    "digital": "Read this phone call aloud like a real call. Officer sounds stern, official and threatening. Uncle sounds old, confused and scared.",
    "kyc": "Read this phone call aloud like a real call. Caller sounds fast, pushy and impatient. Aunty sounds old and a little confused.",
    "normal": "Read this phone call aloud like a real call. Delivery sounds friendly and relaxed. Aunty sounds calm and warm.",
}

PARTS = {
    "digital_1": "Officer: नमस्ते, मैं मुंबई कस्टम्स विभाग से इंस्पेक्टर राठौर बोल रहा हूँ। क्या आप रमेशभाई पटेल हैं?\nUncle: हाँ, बोलिए, क्या बात है?",
    "digital_2": "Officer: आपके आधार कार्ड से ताइवान भेजा गया एक पार्सल पकड़ा गया है। उसमें ड्रग्स और पाँच नकली पासपोर्ट मिले हैं।\nUncle: क्या? मैंने तो कोई पार्सल नहीं भेजा!",
    "digital_3": "Officer: मैं आपकी कॉल अभी सीबीआई को ट्रांसफर कर रहा हूँ। फोन मत काटिए, नहीं तो आपके नाम पर अरेस्ट वारंट निकल जाएगा।",
    "digital_4": "Officer: मैं सीबीआई से अधिकारी शर्मा बोल रहा हूँ। आप अभी से डिजिटल अरेस्ट में हैं। वीडियो कॉल चालू रखिए और कमरे से बाहर मत जाइए।\nUncle: लेकिन मेरा बेटा...",
    "digital_5": "Officer: यह गोपनीय जाँच है। अगर परिवार में किसी को भी बताया, तो उन्हें भी गिरफ्तार किया जाएगा।",
    "digital_6": "Officer: अपना नाम साफ करने के लिए अपनी सारी एफडी तोड़कर आरबीआई के वेरिफिकेशन खाते में पैसे ट्रांसफर कीजिए। जाँच के बाद पैसा वापस मिल जाएगा।\nUncle: कितने पैसे भेजने हैं?",
    "kyc_1": "Caller: હેલો, હું બેંકમાંથી બોલું છું. તમારું KYC અપડેટ બાકી છે.\nAunty: હા, શું કરવાનું છે?",
    "kyc_2": "Caller: આજે રાત્રે બાર વાગ્યા સુધી અપડેટ નહીં થાય તો તમારું ખાતું બંધ થઈ જશે અને પેન્શન અટકી જશે.",
    "kyc_3": "Caller: હું તમને એક લિંક મોકલું છું. તેમાંથી એક એપ ડાઉનલોડ કરી લો, હું તમારી સ્ક્રીન પરથી મદદ કરીશ.",
    "kyc_4": "Caller: હવે તમારા ફોન પર એક OTP આવ્યો હશે. એ છ આંકડા મને જલ્દી કહો.\nAunty: એક મિનિટ, ચશ્મા શોધું...",
    "kyc_5": "Caller: જલ્દી કરો માસી, સમય પૂરો થઈ જશે! કોઈને પૂછવાની જરૂર નથી, આ બેંકનું કામ છે.",
    "normal_1": "Delivery: નમસ્તે, હું કુરિયરમાંથી બોલું છું. તમારું પાર્સલ લઈને આવ્યો છું.\nAunty: હા ભાઈ, ક્યાં પહોંચ્યા?",
    "normal_2": "Delivery: હું ઇસ્કોન ચાર રસ્તા પાસે છું. તમારી સોસાયટી કઈ બાજુ છે?\nAunty: મંદિર પાસેથી ડાબી બાજુ વળો, ત્રીજું ઘર.",
    "normal_3": "Delivery: બરાબર, પાંચ મિનિટમાં પહોંચું છું. પાર્સલનું પેમેન્ટ થઈ ગયું છે, કંઈ આપવાનું નથી.\nAunty: સારું, આભાર ભાઈ.",
    "normal_4": "Delivery: ગેટ પર આવી ગયો છું, બહાર આવશો?\nAunty: હા, આવું છું.",
}


def tts(name, text):
    style = STYLE[name.split("_")[0]]
    speakers = [s for s in VOICES if re.search(rf"^{s}:", text, re.M)]
    if len(speakers) > 1:
        speech = {"multiSpeakerVoiceConfig": {"speakerVoiceConfigs": [
            {"speaker": s, "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICES[s]}}} for s in speakers]}}
        prompt = f"{style}\n\n{text}"
    else:
        s = speakers[0]
        speech = {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICES[s]}}}
        prompt = f"{style}\n\n" + re.sub(rf"^{s}:\s*", "", text, flags=re.M)
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": speech}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    for p in data["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("no audio in response")


def save_wav(path, pcm):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)


only = sys.argv[1:]  # e.g. python3 gen_audio.py digital normal
for name, text in PARTS.items():
    if only and name.split("_")[0] not in only:
        continue
    path = os.path.join(OUT, name + ".wav")
    if os.path.exists(path):
        print("skip (already made)", name); continue
    for attempt in range(6):
        try:
            save_wav(path, tts(name, text)); print("OK  ", name); break
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code == 429 or e.code >= 500:
                print(f"     {name}: busy ({e.code}), waiting 25s..."); time.sleep(25)
            else:
                print(f"FAIL {name}: {e.code} {msg}"); sys.exit(1)
        except Exception as e:
            print(f"     {name}: {e}, retrying in 10s"); time.sleep(10)
    else:
        print(f"FAIL {name}: gave up after retries")
    time.sleep(3)
print("Done. Files are in public/audio/")
