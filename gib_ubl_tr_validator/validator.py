# -*- coding: utf-8 -*-
"""
UBL-TR 1.2 XML Şema ve GİB İş Kuralları Doğrulayıcısı
"""

import re
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Standard UBL-TR Namespaces
NS = {
    "inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "xades": "http://uri.etsi.org/01903/v1.3.2#"
}

VALID_PROFILES = [
    "TEMELFATURA", "TEMELIFATURA", "TICARIFATURA", "IHRACAT",
    "YOLCUBERABERFATURA", "EARSIVFATURA", "KAMU", "HKS", "ENERJI"
]

VALID_INVOICE_TYPES = [
    "SATIS", "IADE", "TEVKIFAT", "ISTISNA", "OZELMATRAH",
    "IHRACKAYITLI", "SGK", "KOMISYONCU", "TASFIYE"
]

@dataclass
class ValidationError:
    code: str
    message: str
    field_path: str
    severity: str = "ERROR"  # ERROR or WARNING

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


class UBLTRValidator:
    """Gelir İdaresi Başkanlığı UBL-TR 1.2 Standart Doğrulayıcısı"""

    def __init__(self, xml_content: Optional[str] = None, xml_file: Optional[str] = None):
        self.root: Optional[ET.Element] = None
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.metadata: Dict[str, Any] = {}

        if xml_file:
            with open(xml_file, "r", encoding="utf-8") as f:
                self.xml_content = f.read()
        else:
            self.xml_content = xml_content or ""

    def validate(self) -> ValidationResult:
        self.errors.clear()
        self.warnings.clear()
        self.metadata.clear()

        if not self.xml_content.strip():
            self.errors.append(ValidationError(
                code="GIB_EMPTY_XML",
                message="XML içeriği boş olamaz.",
                field_path="/"
            ))
            return ValidationResult(is_valid=False, errors=self.errors)

        try:
            self.root = ET.fromstring(self.xml_content)
        except ET.ParseError as e:
            self.errors.append(ValidationError(
                code="GIB_XML_SYNTAX_ERROR",
                message=f"XML sözdizim hatası: {str(e)}",
                field_path="/"
            ))
            return ValidationResult(is_valid=False, errors=self.errors)

        self._check_root_and_namespaces()
        self._check_header_elements()
        self._check_supplier_party()
        self._check_customer_party()
        self._check_tax_totals()
        self._check_monetary_totals()
        self._check_invoice_lines()

        is_valid = len(self.errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=list(self.errors),
            warnings=list(self.warnings),
            metadata=dict(self.metadata)
        )

    def _find_val(self, path: str, parent: Optional[ET.Element] = None) -> Optional[str]:
        p = parent if parent is not None else self.root
        if p is None:
            return None
        el = p.find(path, NS)
        return el.text.strip() if el is not None and el.text else None

    def _check_root_and_namespaces(self):
        tag = self.root.tag
        if not tag.endswith("Invoice"):
            self.errors.append(ValidationError(
                code="GIB_INVALID_ROOT",
                message=f"Kök eleman 'Invoice' olmalıdır. Bulunan: {tag}",
                field_path="Invoice"
            ))

        ubl_ver = self._find_val("cbc:UBLVersionID")
        self.metadata["UBLVersionID"] = ubl_ver
        if ubl_ver != "2.1":
            self.errors.append(ValidationError(
                code="GIB_INVALID_UBL_VER",
                message=f"UBLVersionID '2.1' olmalıdır. Bulunan: '{ubl_ver}'",
                field_path="Invoice/cbc:UBLVersionID"
            ))

        cust_id = self._find_val("cbc:CustomizationID")
        self.metadata["CustomizationID"] = cust_id
        if cust_id != "TR1.2":
            self.errors.append(ValidationError(
                code="GIB_INVALID_CUSTOMIZATION",
                message=f"CustomizationID 'TR1.2' olmalıdır. Bulunan: '{cust_id}'",
                field_path="Invoice/cbc:CustomizationID"
            ))

    def _check_header_elements(self):
        # ProfileID
        profile_id = self._find_val("cbc:ProfileID")
        self.metadata["ProfileID"] = profile_id
        if not profile_id or profile_id.upper() not in VALID_PROFILES:
            self.errors.append(ValidationError(
                code="GIB_INVALID_PROFILE_ID",
                message=f"Geçersiz ProfileID: '{profile_id}'. Geçerli profiller: {', '.join(VALID_PROFILES)}",
                field_path="Invoice/cbc:ProfileID"
            ))

        # Invoice ID (Fatura No: 16 hane, örn GIB2026000000001)
        invoice_id = self._find_val("cbc:ID")
        self.metadata["InvoiceID"] = invoice_id
        if not invoice_id:
            self.errors.append(ValidationError(
                code="GIB_MISSING_INVOICE_ID",
                message="Fatura Numarası (cbc:ID) eksik.",
                field_path="Invoice/cbc:ID"
            ))
        elif not re.match(r"^[A-Z0-9]{3}[0-9]{4}[0-9]{9}$", invoice_id):
            self.errors.append(ValidationError(
                code="GIB_INVALID_INVOICE_ID_FORMAT",
                message=f"Fatura Numarası formatı geçersiz (16 karakter olmalı: 3 seri + 4 yıl + 9 sıra no): '{invoice_id}'",
                field_path="Invoice/cbc:ID"
            ))

        # UUID
        uuid_str = self._find_val("cbc:UUID")
        self.metadata["UUID"] = uuid_str
        if not uuid_str:
            self.errors.append(ValidationError(
                code="GIB_MISSING_UUID",
                message="Fatura Evrensel Tekil Kimliği (cbc:UUID) eksik.",
                field_path="Invoice/cbc:UUID"
            ))
        else:
            try:
                uuid.UUID(uuid_str)
            except ValueError:
                self.errors.append(ValidationError(
                    code="GIB_INVALID_UUID_FORMAT",
                    message=f"cbc:UUID geçerli bir RFC 4122 UUID formatında değil: '{uuid_str}'",
                    field_path="Invoice/cbc:UUID"
                ))

        # IssueDate (YYYY-MM-DD)
        issue_date = self._find_val("cbc:IssueDate")
        self.metadata["IssueDate"] = issue_date
        if not issue_date or not re.match(r"^\d{4}-\d{2}-\d{2}$", issue_date):
            self.errors.append(ValidationError(
                code="GIB_INVALID_ISSUE_DATE",
                message=f"Düzenleme Tarihi (cbc:IssueDate) YYYY-MM-DD formatında olmalıdır. Bulunan: '{issue_date}'",
                field_path="Invoice/cbc:IssueDate"
            ))

        # InvoiceTypeCode
        type_code = self._find_val("cbc:InvoiceTypeCode")
        self.metadata["InvoiceTypeCode"] = type_code
        if not type_code or type_code.upper() not in VALID_INVOICE_TYPES:
            self.errors.append(ValidationError(
                code="GIB_INVALID_INVOICE_TYPE_CODE",
                message=f"Geçersiz Fatura Tipi Kodu: '{type_code}'. İzin verilenler: {', '.join(VALID_INVOICE_TYPES)}",
                field_path="Invoice/cbc:InvoiceTypeCode"
            ))

        # DocumentCurrencyCode
        curr_code = self._find_val("cbc:DocumentCurrencyCode")
        self.metadata["DocumentCurrencyCode"] = curr_code
        if not curr_code or len(curr_code) != 3:
            self.errors.append(ValidationError(
                code="GIB_INVALID_CURRENCY_CODE",
                message=f"Belge Para Birimi Kodu (cbc:DocumentCurrencyCode) 3 karakterli ISO kodu olmalıdır (Örn: TRY, USD): '{curr_code}'",
                field_path="Invoice/cbc:DocumentCurrencyCode"
            ))

    def _check_supplier_party(self):
        supplier = self.root.find("cac:AccountingSupplierParty/cac:Party", NS)
        if supplier is None:
            self.errors.append(ValidationError(
                code="GIB_MISSING_SUPPLIER_PARTY",
                message="Satıcı / Gönderici bilgileri (cac:AccountingSupplierParty) bulunamadı.",
                field_path="Invoice/cac:AccountingSupplierParty"
            ))
            return

        # VKN or TCKN
        party_id = supplier.find("cac:PartyIdentification/cbc:ID", NS)
        if party_id is None or not party_id.text:
            self.errors.append(ValidationError(
                code="GIB_MISSING_SUPPLIER_ID",
                message="Satıcı VKN veya TCKN numarası bulunamadı.",
                field_path="Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID"
            ))
        else:
            ident = party_id.text.strip()
            self.metadata["SupplierID"] = ident
            if not (len(ident) in [10, 11] and ident.isdigit()):
                self.errors.append(ValidationError(
                    code="GIB_INVALID_SUPPLIER_ID_FORMAT",
                    message=f"Satıcı Kimlik No 10 haneli VKN veya 11 haneli TCKN olmalıdır: '{ident}'",
                    field_path="Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID"
                ))

        # Title or Name
        party_name = supplier.find("cac:PartyName/cbc:Name", NS)
        person_name = supplier.find("cac:Person/cbc:FirstName", NS)
        if party_name is None and person_name is None:
            self.errors.append(ValidationError(
                code="GIB_MISSING_SUPPLIER_NAME",
                message="Satıcı ticari unvanı (cac:PartyName) veya şahıs adı (cac:Person) bulunmalıdır.",
                field_path="Invoice/cac:AccountingSupplierParty/cac:Party"
            ))

    def _check_customer_party(self):
        customer = self.root.find("cac:AccountingCustomerParty/cac:Party", NS)
        if customer is None:
            self.errors.append(ValidationError(
                code="GIB_MISSING_CUSTOMER_PARTY",
                message="Alıcı bilgileri (cac:AccountingCustomerParty) bulunamadı.",
                field_path="Invoice/cac:AccountingCustomerParty"
            ))
            return

        party_id = customer.find("cac:PartyIdentification/cbc:ID", NS)
        if party_id is not None and party_id.text:
            ident = party_id.text.strip()
            self.metadata["CustomerID"] = ident
            if not (len(ident) in [10, 11] and ident.isdigit()) and ident != "11111111111" and ident != "2222222222":
                self.warnings.append(ValidationError(
                    code="GIB_CUSTOMER_ID_WARNING",
                    message=f"Alıcı Kimlik No standart 10/11 haneli format dışı: '{ident}'",
                    field_path="Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID",
                    severity="WARNING"
                ))

    def _check_tax_totals(self):
        tax_total = self.root.find("cac:TaxTotal", NS)
        if tax_total is None:
            self.errors.append(ValidationError(
                code="GIB_MISSING_TAX_TOTAL",
                message="Vergi Toplamı (cac:TaxTotal) elemanı bulunamadı.",
                field_path="Invoice/cac:TaxTotal"
            ))
            return

        tax_amount_str = self._find_val("cbc:TaxAmount", tax_total)
        try:
            tax_amount = float(tax_amount_str) if tax_amount_str else 0.0
            self.metadata["TaxAmount"] = tax_amount
        except ValueError:
            self.errors.append(ValidationError(
                code="GIB_INVALID_TAX_AMOUNT",
                message=f"cbc:TaxAmount sayısal bir değer olmalıdır: '{tax_amount_str}'",
                field_path="Invoice/cac:TaxTotal/cbc:TaxAmount"
            ))

    def _check_monetary_totals(self):
        monetary = self.root.find("cac:LegalMonetaryTotal", NS)
        if monetary is None:
            self.errors.append(ValidationError(
                code="GIB_MISSING_LEGAL_MONETARY_TOTAL",
                message="Yasal Parasal Toplamlar (cac:LegalMonetaryTotal) bulunamadı.",
                field_path="Invoice/cac:LegalMonetaryTotal"
            ))
            return

        payable_str = self._find_val("cbc:PayableAmount", monetary)
        line_ext_str = self._find_val("cbc:LineExtensionAmount", monetary)
        tax_exclusive_str = self._find_val("cbc:TaxExclusiveAmount", monetary)
        tax_inclusive_str = self._find_val("cbc:TaxInclusiveAmount", monetary)

        if not payable_str:
            self.errors.append(ValidationError(
                code="GIB_MISSING_PAYABLE_AMOUNT",
                message="Ödenecek Tutar (cbc:PayableAmount) zorunludur.",
                field_path="Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount"
            ))
        else:
            try:
                payable = float(payable_str)
                self.metadata["PayableAmount"] = payable
            except ValueError:
                self.errors.append(ValidationError(
                    code="GIB_INVALID_PAYABLE_AMOUNT",
                    message=f"Ödenecek Tutar sayısal olmalıdır: '{payable_str}'",
                    field_path="Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount"
                ))

    def _check_invoice_lines(self):
        lines = self.root.findall("cac:InvoiceLine", NS)
        self.metadata["LineCount"] = len(lines)
        if len(lines) == 0:
            self.errors.append(ValidationError(
                code="GIB_NO_INVOICE_LINES",
                message="Faturada en az 1 adet fatura satırı (cac:InvoiceLine) bulunmalıdır.",
                field_path="Invoice/cac:InvoiceLine"
            ))
