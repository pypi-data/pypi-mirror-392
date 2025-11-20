# Cordatus Jtop Service Kurulum Talimatları

## Kurulum

### 1. PyPI'den Kurun

```bash
pip install cordatus-jtop-service==4.3.2.5
```

### 2. Servisi Kurma (Önemli!)

PyPI'den kurduktan sonra, systemd servisini aktif etmek için aşağıdaki komutu **sudo ile** çalıştırmanız gerekir:

```bash
sudo cordatus-jtop-setup
```

Bu komut:
- ✅ Systemd servisini kurar ve başlatır
- ✅ Gerekli kullanıcı izinlerini ayarlar
- ✅ Environment variables ayarlar
- ✅ Eski jetson-stats kurulumlarını temizler

### 3. Kullanıcı İzinleri

Kurulum tamamlandıktan sonra, **oturumu kapatıp tekrar açmanız** gerekebilir (grup izinlerinin aktif olması için).

```bash
# Kullanıcının grup üyeliğini kontrol edin:
groups

# "jtop" grubu görünmeli
```

### 4. Servisi Kontrol Edin

```bash
sudo systemctl status jtop.service
```

### 5. JTop'u Kullanın

Artık jtop'u normal kullanıcı olarak çalıştırabilirsiniz:

```bash
jtop
```

## Kaldırma

```bash
# Servisi durdur ve devre dışı bırak
sudo systemctl stop jtop.service
sudo systemctl disable jtop.service

# Paketi kaldır
pip uninstall cordatus-jtop-service
```

## Sorun Giderme

### "Permission denied" hatası

```bash
# Kullanıcınızı jtop grubuna ekleyin:
sudo usermod -a -G jtop $USER

# Oturumu kapatıp tekrar açın
```

### Servis başlamıyor

```bash
# Servis loglarını kontrol edin:
sudo journalctl -u jtop.service -f

# Servisi manuel başlatın:
sudo systemctl restart jtop.service
```

### Eski jetson-stats ile çakışma

Eğer daha önce jetson-stats kurduysanız:

```bash
# Önce eski paketi kaldırın:
sudo pip3 uninstall jetson-stats

# Sonra cordatus-jtop-service kurun:
pip install cordatus-jtop-service==4.3.2.5
sudo cordatus-jtop-setup
```

## Geliştirme Modu

Development için:

```bash
git clone <repo-url>
cd jetson_stats
sudo pip install -e .
```

Development modunda setup.py'daki `JTOPDevelopCommand` otomatik çalışır.
