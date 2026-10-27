# GİB UBL-TR 1.2 e-Fatura & e-Arşiv XML Doğrulayıcı ve Test Üreteci 📑⚖️

[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Standart: UBL-TR 1.2](https://img.shields.io/badge/Standart-G%C4%B0B%20UBL--TR%201.2-red.svg)](https://ebelge.gib.gov.tr)
[![Bağımlılık: Yok](https://img.shields.io/badge/Dependencies-Zero--Dependency-success.svg)](https://github.com)
[![Rehber](https://img.shields.io/badge/Rehber-E--Fatura%20At%C3%B6lyesi-0284c7.svg)](https://efaturabilgi.site)

Türkiye Cumhuriyeti Hazine ve Maliye Bakanlığı **Gelir İdaresi Başkanlığı (GİB)** tarafından yürütülen e-Fatura ve e-Arşiv Fatura standartlarına (**UBL-TR 1.2**) uygun XML faturaları denetleyen, şema ve zorunlu iş kurallarını doğrulayan, aynı zamanda yazılımcı ve entegratörler için test faturası XML'i üreten hafif, bağımsız ve açık kaynaklı Python aracıdır.

Ayrıntılı mevzuat, istisna kodları ve 509 Sıra No.lu VUK Genel Tebliği kılavuzları için [E-Fatura Atölyesi (efaturabilgi.site)](https://efaturabilgi.site) portalını ziyaret edebilirsiniz.

---

## ✨ Öne Çıkan Özellikler

* ⚡ **Sıfır Harici Bağımlılık (Zero-Dependency):** C kütüphanesi veya lxml gerektirmeden %100 saf Python standart kütüphanesi (`xml.etree.ElementTree`) ile çalışır.
* 🛡️ **GİB UBL-TR 1.2 İş Kuralları:**
  * `CustomizationID` (`TR1.2`) ve `UBLVersionID` (`2.1`) doğrulaması.
  * 16 Haneli Fatura Numarası format denetimi (`GIB2026000000001` - 3 seri + 4 yıl + 9 sıra no).
  * RFC 4122 uyumlu Evrensel Tekil Tanımlayıcı (`UUID`) geçerlilik testi.
  * Satıcı ve Alıcı VKN (10 hane) / TCKN (11 hane) ve unvan kontrolü.
  * KDV oranları (%1, %10, %20) ve vergi matrahı tutarlılık hesabı.
  * `PayableAmount`, `LineExtensionAmount` ve `TaxInclusiveAmount` parasal denge denetimi.
* 🧪 **Test Faturası Üreteci (Generator):** GİB test ortamlarına (`merkeztest.gib.gov.tr`) veya entegratör sandbox hesaplarına göndermek üzere saniyeler içinde geçerli örnek UBL-TR XML'i üretir.
* 💻 **CLI & Python API:** Hem komut satırından terminal aracı olarak hem de projelerinizde içe aktarılabilir Python paketi olarak kullanılabilir.

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
git clone https://github.com/eimza-kep/gib-ubl-tr-validator.git
cd gib-ubl-tr-validator
```

### 2. Komut Satırı (CLI) Kullanımı

#### Mevcut bir faturayı doğrulayın:
```bash
python -m gib_ubl_tr_validator fatura.xml
```

#### Örnek geçerli bir test faturası XML'i üretin:
```bash
python -m gib_ubl_tr_validator --generate --profile TICARIFATURA --type SATIS --out ornek_fatura.xml
```

---

## 🐍 Python Kütüphanesi Olarak Kullanım

```python
from gib_ubl_tr_validator import UBLTRValidator, generate_mock_invoice

# 1. XML Doğrulama
xml_content = open("fatura.xml", "r", encoding="utf-8").read()
validator = UBLTRValidator(xml_content=xml_content)
result = validator.validate()

if result.is_valid:
    print(f"✅ Fatura geçerli! Fatura No: {result.metadata['InvoiceID']}")
    print(f"Ödenecek Tutar: {result.metadata['PayableAmount']} {result.metadata['DocumentCurrencyCode']}")
else:
    print(f"❌ {len(result.errors)} adet hata bulundu:")
    for err in result.errors:
        print(f"  [{err.code}] {err.message} (Konum: {err.field_path})")

# 2. Test Faturası Üretme
mock_xml = generate_mock_invoice(
    invoice_id="GIB2026000000100",
    profile_id="TEMELFATURA",
    supplier_title="Acme Teknoloji A.Ş.",
    unit_price=5000.0,
    kdv_rate=20.0
)
```

---

## 🧪 Testleri Çalıştırma

```bash
python -m unittest test_validator.py
```

---

## 📜 Lisans

Bu proje **MIT Lisansı** altında sunulmaktadır. Ticari ve bireysel projelerinizde özgürce kullanabilir, entegre edebilirsiniz. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.
