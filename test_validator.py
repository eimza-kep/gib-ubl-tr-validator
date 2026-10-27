# -*- coding: utf-8 -*-
import unittest
from gib_ubl_tr_validator.validator import UBLTRValidator
from gib_ubl_tr_validator.generator import generate_mock_invoice

class TestUBLTRValidator(unittest.TestCase):
    def test_valid_generated_invoice(self):
        xml_data = generate_mock_invoice()
        validator = UBLTRValidator(xml_content=xml_data)
        result = validator.validate()
        self.assertTrue(result.is_valid, f"Beklenmeyen hatalar: {[e.message for e in result.errors]}")
        self.assertEqual(result.metadata.get("CustomizationID"), "TR1.2")
        self.assertEqual(result.metadata.get("UBLVersionID"), "2.1")
        self.assertEqual(result.metadata.get("InvoiceTypeCode"), "SATIS")

    def test_invalid_empty_xml(self):
        validator = UBLTRValidator(xml_content="")
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "GIB_EMPTY_XML")

    def test_invalid_syntax_xml(self):
        validator = UBLTRValidator(xml_content="<Invoice><invalid>")
        result = validator.validate()
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "GIB_XML_SYNTAX_ERROR")

    def test_invalid_invoice_id_format(self):
        xml_data = generate_mock_invoice(invoice_id="INVALID_ID")
        validator = UBLTRValidator(xml_content=xml_data)
        result = validator.validate()
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn("GIB_INVALID_INVOICE_ID_FORMAT", error_codes)

if __name__ == "__main__":
    unittest.main()
