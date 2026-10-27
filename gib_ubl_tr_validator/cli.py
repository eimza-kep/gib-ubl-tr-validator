# -*- coding: utf-8 -*-
"""
CLI Arayüzü: UBL-TR Doğrulama ve Test Faturası Üretme Komutları
"""

import sys
import argparse
from .validator import UBLTRValidator
from .generator import generate_mock_invoice

def main():
    parser = argparse.ArgumentParser(
        description="GİB UBL-TR 1.2 e-Fatura & e-Arşiv XML Doğrulayıcı ve Test Üreteci"
    )
    parser.add_argument("file", nargs="?", help="Doğrulanacak UBL-TR XML dosya yolu")
    parser.add_argument("--generate", action="store_true", help="GİB test ortamı uyumlu örnek UBL-TR XML çıktısı üretir")
    parser.add_argument("--out", help="Üretilen XML'in kaydedileceği dosya yolu")
    parser.add_argument("--profile", default="TICARIFATURA", help="Profil ID (TEMELFATURA, TICARIFATURA, EARSIVFATURA)")
    parser.add_argument("--type", default="SATIS", help="Fatura Tipi (SATIS, IADE, TEVKIFAT, ISTISNA)")
    parser.add_argument("--quiet", action="store_true", help="Yalnızca hata kodlarını basar")

    args = parser.parse_args()

    if args.generate:
        xml_str = generate_mock_invoice(profile_id=args.profile, invoice_type=args.type)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(xml_str)
            print(f"✅ Örnek UBL-TR faturası başarıyla oluşturuldu: {args.out}")
        else:
            print(xml_str)
        sys.exit(0)

    if not args.file:
        parser.print_help()
        sys.exit(1)

    validator = UBLTRValidator(xml_file=args.file)
    result = validator.validate()

    if not args.quiet:
        print("\n" + "=" * 60)
        print("📄 GİB UBL-TR 1.2 DOĞRULAMA RAPORU")
        print("=" * 60)
        print(f"Dosya: {args.file}")
        print(f"Durum: {'✅ GEÇERLİ' if result.is_valid else '❌ GEÇERSİZ'}")

        if result.metadata:
            print("\n📋 Belge Meta Verileri:")
            for k, v in result.metadata.items():
                print(f"  • {k}: {v}")

        if result.errors:
            print(f"\n❌ Tespit Edilen Hatalar ({len(result.errors)} adet):")
            for e in result.errors:
                print(f"  [{e.code}] {e.message} (Konum: {e.field_path})")

        if result.warnings:
            print(f"\n⚠️ Uyarılar ({len(result.warnings)} adet):")
            for w in result.warnings:
                print(f"  [{w.code}] {w.message}")

        print("=" * 60)

    sys.exit(0 if result.is_valid else 1)

if __name__ == "__main__":
    main()
