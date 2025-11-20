# PyPI'ye Yükleme Rehberi - Cordatus JTop Service

## Sorun Neydi?

Orijinal `jetson-stats` paketi PyPI'ye yüklendiğinde `sudo pip install` ile kurulur ve kurulum sırasında `setup.py`'daki custom install komutları (`JTOPInstallCommand`) çalışır, bu da:
- systemd servisini `/etc/systemd/system/` altına kurar
- Kullanıcı gruplarını ayarlar
- Environment variables ayarlar

Ancak sizin PyPI üzerinden dağıttığınız pakette bu otomatik kurulum **çalışmaz** çünkü:
1. PyPI'den wheel paketi indirilir (önceden build edilmiş)
2. Custom install komutları wheel kurulumunda çalışmaz
3. Normal kullanıcılar `sudo pip install` yapmaz

## Çözüm

Sistem kurulumu için ayrı bir **setup komutu** ekledik: `cordatus-jtop-setup`

### Yapılan Değişiklikler

#### 1. Yeni Setup Script: `jtop/setup_service.py`
- Sistemd servisini kurar
- Kullanıcı izinlerini ayarlar
- Environment variables'ları kurar
- Root kontrolü yapar

#### 2. Setup.py'ye Entry Point Eklendi
```python
entry_points={'console_scripts': [
    'jtop=jtop.__main__:main',
    'jetson_release = jtop.jetson_release:main',
    'jetson_config = jtop.jetson_config:main',
    'jetson_swap = jtop.jetson_swap:main',
    'cordatus-jtop-setup = jtop.setup_service:main',  # ← YENİ
]},
```

#### 3. Paket İsmi Değiştirildi
```python
name="cordatus-jtop-service",
version="4.3.2.5",
```

## PyPI'ye Yükleme Adımları

### 1. Paketi Build Edin

```bash
cd /home/openzeka/Documents/jetson_stats

# Eski dist klasörünü temizleyin (opsiyonel)
rm -rf dist/ build/ *.egg-info

# Yeni paketi build edin
python3 -m build --no-isolation
```

Bu komut `dist/` klasöründe şu dosyaları oluşturur:
- `cordatus_jtop_service-4.3.2.5-py3-none-any.whl` (wheel paketi)
- `cordatus_jtop_service-4.3.2.5.tar.gz` (kaynak kodu)

### 2. Test Edin (Opsiyonel ama Önerilen)

```bash
# Yerel test için:
pip install dist/cordatus_jtop_service-4.3.2.5-py3-none-any.whl

# Setup komutunu test edin:
sudo cordatus-jtop-setup

# Servisi kontrol edin:
sudo systemctl status jtop.service

# Test sonrası kaldırın:
pip uninstall cordatus-jtop-service
```

### 3. PyPI'ye Yükleyin

```bash
# Test PyPI'ye yükleyin (önce test edin):
python3 -m twine upload --repository testpypi dist/*

# Gerçek PyPI'ye yükleyin:
python3 -m twine upload dist/*
```

PyPI credentials soracaktır:
- Username: `__token__`
- Password: PyPI API token'ınız

### 4. PyPI API Token Oluşturma

1. https://pypi.org/manage/account/ adresine gidin
2. "API tokens" bölümüne tıklayın
3. "Add API token" butonuna tıklayın
4. Token adı verin ve "Create token" deyin
5. Token'ı kopyalayın (sadece bir kere gösterilir!)

## Kullanıcılar Nasıl Kuracak?

### Jetson Cihazında Kurulum

```bash
# 1. Paketi kurun (sudo GEREKMEZ)
pip install cordatus-jtop-service==4.3.2.5

# 2. Servisi kurun (sudo GEREKİR)
sudo cordatus-jtop-setup

# 3. Oturumu kapatıp açın veya reboot edin
logout
# veya
sudo reboot

# 4. JTop'u kullanın
jtop
```

## Versiyon Güncelleme

Her yeni versiyon için:

```bash
# 1. setup.py'de versiyonu güncelleyin
# version="4.3.2.6"  # Örnek

# 2. Build edin
python3 -m build --no-isolation

# 3. PyPI'ye yükleyin
python3 -m twine upload dist/*
```

## Önemli Notlar

### ✅ Yapılan İyileştirmeler
- ✅ Kullanıcılar `sudo pip install` yapmak zorunda değil
- ✅ Servis kurulumu ayrı ve kontrolü kullanıcıda
- ✅ Hata mesajları daha açık ve yardımcı
- ✅ Setup script durumu raporluyor

### ⚠️ Dikkat Edilmesi Gerekenler
- Kullanıcılar `cordatus-jtop-setup` çalıştırmayı unutabilir - README'de büyük harflerle belirtin
- Servis dosyası `/etc/systemd/system/jtop.service` yoluna kurulur
- Kullanıcı `jtop` grubuna eklenir
- Oturum kapatma/açma gereklidir

### 🔍 Sorun Giderme

Kurulum sorunları için kullanıcılara şu kontrolleri yaptırın:

```bash
# 1. Paket kurulu mu?
pip list | grep cordatus-jtop-service

# 2. Setup script var mı?
which cordatus-jtop-setup

# 3. Servis kurulu mu?
sudo systemctl status jtop.service

# 4. Kullanıcı grupta mı?
groups | grep jtop

# 5. Servis logları:
sudo journalctl -u jtop.service -f
```

## Lisans Uyarısı

Bu paket AGPL-3.0 lisansı altındadır. Fork yapıyorsanız:
- Orijinal yazarı belirtin (Raffaello Bonghi)
- Değişiklikleri dokümante edin
- Aynı lisansı kullanın
- Kaynak kodunu paylaşın

## İletişim

Bu fork hakkında sorularınız için Cordatus ekibi ile iletişime geçin.
