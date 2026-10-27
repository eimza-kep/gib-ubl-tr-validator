# -*- coding: utf-8 -*-
"""
UBL-TR 1.2 Uyumlu Test e-Fatura XML Üreticisi
GİB Test Portalı ve Entegratör Sandbox Testleri İçin
"""

import uuid
from datetime import datetime

def generate_mock_invoice(
    invoice_id: str = "GIB2026000000001",
    profile_id: str = "TICARIFATURA",
    invoice_type: str = "SATIS",
    supplier_vkn: str = "1234567890",
    supplier_title: str = "Örnek Teknoloji ve Bilişim A.Ş.",
    customer_vkn: str = "9876543210",
    customer_title: str = "Müşteri Sanayi ve Ticaret Ltd. Şti.",
    currency: str = "TRY",
    item_name: str = "Yazılım Danışmanlık ve Entegrasyon Hizmeti",
    unit_price: float = 10000.0,
    quantity: float = 1.0,
    kdv_rate: float = 20.0
) -> str:
    """
    GİB UBL-TR 1.2 standartlarına tam uyumlu örnek test faturası XML'i üretir.
    """
    now = datetime.now()
    issue_date = now.strftime("%Y-%m-%d")
    issue_time = now.strftime("%H:%M:%S")
    invoice_uuid = str(uuid.uuid4())

    line_ext_amount = round(unit_price * quantity, 2)
    kdv_amount = round(line_ext_amount * (kdv_rate / 100.0), 2)
    payable_amount = round(line_ext_amount + kdv_amount, 2)

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
         xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
         xmlns:xades="http://uri.etsi.org/01903/v1.3.2#">
    <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
    <cbc:CustomizationID>TR1.2</cbc:CustomizationID>
    <cbc:ProfileID>{profile_id}</cbc:ProfileID>
    <cbc:ID>{invoice_id}</cbc:ID>
    <cbc:CopyIndicator>false</cbc:CopyIndicator>
    <cbc:UUID>{invoice_uuid}</cbc:UUID>
    <cbc:IssueDate>{issue_date}</cbc:IssueDate>
    <cbc:IssueTime>{issue_time}</cbc:IssueTime>
    <cbc:InvoiceTypeCode>{invoice_type}</cbc:InvoiceTypeCode>
    <cbc:Note>GİB Test Ortamı İçin Üretilmiş Test Faturasıdır.</cbc:Note>
    <cbc:DocumentCurrencyCode>{currency}</cbc:DocumentCurrencyCode>
    <cbc:LineCountNumeric>1</cbc:LineCountNumeric>

    <!-- Satıcı / Gönderici Bilgileri -->
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="VKN">{supplier_vkn}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>{supplier_title}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Teknoloji Caddesi No:42</cbc:StreetName>
                <cbc:CitySubdivisionName>Çankaya</cbc:CitySubdivisionName>
                <cbc:CityName>Ankara</cbc:CityName>
                <cac:Country>
                    <cbc:Name>Türkiye</cbc:Name>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cac:TaxScheme>
                    <cbc:Name>Çankaya Vergi Dairesi</cbc:Name>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>

    <!-- Alıcı Bilgileri -->
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="VKN">{customer_vkn}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>{customer_title}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Sanayi Bulvarı No:10</cbc:StreetName>
                <cbc:CitySubdivisionName>Maslak</cbc:CitySubdivisionName>
                <cbc:CityName>İstanbul</cbc:CityName>
                <cac:Country>
                    <cbc:Name>Türkiye</cbc:Name>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cac:TaxScheme>
                    <cbc:Name>Maslak Vergi Dairesi</cbc:Name>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingCustomerParty>

    <!-- Vergi Toplamı -->
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="{currency}">{kdv_amount:.2f}</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="{currency}">{line_ext_amount:.2f}</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="{currency}">{kdv_amount:.2f}</cbc:TaxAmount>
            <cbc:Percent>{kdv_rate:.0f}</cbc:Percent>
            <cac:TaxCategory>
                <cac:TaxScheme>
                    <cbc:Name>KDV</cbc:Name>
                    <cbc:TaxTypeCode>0015</cbc:TaxTypeCode>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>

    <!-- Parasal Toplamlar -->
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="{currency}">{line_ext_amount:.2f}</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="{currency}">{line_ext_amount:.2f}</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="{currency}">{payable_amount:.2f}</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="{currency}">{payable_amount:.2f}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>

    <!-- Fatura Satırı -->
    <cac:InvoiceLine>
        <cbc:ID>1</cbc:ID>
        <cbc:InvoicedQuantity unitCode="C62">{quantity:.2f}</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="{currency}">{line_ext_amount:.2f}</cbc:LineExtensionAmount>
        <cac:TaxTotal>
            <cbc:TaxAmount currencyID="{currency}">{kdv_amount:.2f}</cbc:TaxAmount>
            <cac:TaxSubtotal>
                <cbc:TaxableAmount currencyID="{currency}">{line_ext_amount:.2f}</cbc:TaxableAmount>
                <cbc:TaxAmount currencyID="{currency}">{kdv_amount:.2f}</cbc:TaxAmount>
                <cbc:Percent>{kdv_rate:.0f}</cbc:Percent>
                <cac:TaxCategory>
                    <cac:TaxScheme>
                        <cbc:Name>KDV</cbc:Name>
                        <cbc:TaxTypeCode>0015</cbc:TaxTypeCode>
                    </cac:TaxScheme>
                </cac:TaxCategory>
            </cac:TaxSubtotal>
        </cac:TaxTotal>
        <cac:Item>
            <cbc:Name>{item_name}</cbc:Name>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="{currency}">{unit_price:.2f}</cbc:PriceAmount>
        </cac:Price>
    </cac:InvoiceLine>
</Invoice>"""
    return xml_content
