# J.A.R.V.I.S 4.6.2 — Android Standalone Port

Bu proje, sağlanan JARVIS V3 macOS kaynak kodunun Android'de bilgisayarsız çalışacak şekilde hazırlanmış bağımsız bir Kivy portudur. macOS'a özel ekran/takvim/WhatsApp/shell otomasyonları Android'e taşınmamıştır.

## Özellikler
- Android üzerinde çalışan bağımsız Kivy arayüzü
- Gemini 2.5 Flash ile metin sohbeti (internet ve Gemini API anahtarı gerekir)
- Android sistem Text-to-Speech ile Türkçe sesli yanıt (cihazdaki TTS motoruna bağlı)
- JARVIS / FRIDAY / ULTRON kişilikleri
- Cihaz üzerinde yerel not hafızası
- Pil ve saat sorguları, Google araması ve YouTube açma
- API anahtarı ve model ayarları cihazın uygulama veri alanında saklanır

## APK derleme
1. Bu klasörün içeriğini GitHub deposunun köküne yükleyin.
2. `.github/workflows/android.yml` dosyasının da depoda olduğundan emin olun.
3. GitHub → Actions → Build JARVIS Android APK → Run workflow.
4. Başarılı işlemden sonra `JARVIS-Android-APK` artifact'ini indirin.
5. APK'yı Android telefona kurun. İlk açılışta ⚙ menüsünden kendi Gemini API anahtarınızı girin.

## Gereksinimler ve sınırlar
- JARVIS uygulaması bilgisayara bağlanmaz; doğrudan Android'de çalışır.
- Gemini yanıtları için internet bağlantısı ve kişisel Gemini API anahtarı gerekir. API kullanımı Google'ın kota/ücret koşullarına tabidir.
- API anahtarı APK'ya gömülmez; ilk açılışta uygulama içinde girilir ve uygulamanın özel veri alanında saklanır.
- Bu ilk Android portu; macOS ekran analizi, Mac uygulaması kontrolü, Mac takvimi, webcam akışı ve WhatsApp otomasyonlarını içermez.
- Sesli yanıt Android TTS kullanır. Bu sürümde mikrofonla konuşarak giriş henüz eklenmemiştir; metin girişi kullanılmaktadır.
