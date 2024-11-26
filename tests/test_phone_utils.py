import unittest
from src.utils.phone_utils import clean_phone_number, format_brazilian_number, validate_phone_list

class TestPhoneUtils(unittest.TestCase):
    def test_clean_phone_number(self):
        """Testa a limpeza de números de telefone"""
        test_cases = [
            ("(11) 99999-9999", "11999999999"),
            ("+55 11 99999-9999", "5511999999999"),
            ("11.99999.9999", "11999999999"),
            ("11 9999-9999", "1199999999")
        ]
        
        for input_number, expected in test_cases:
            with self.subTest(input_number=input_number):
                result = clean_phone_number(input_number)
                self.assertEqual(result, expected)
    
    def test_format_brazilian_number(self):
        """Testa a formatação de números brasileiros"""
        test_cases = [
            ("11999999999", "5511999999999"),  # Sem código do país
            ("5511999999999", "5511999999999"),  # Com código do país
            ("+5511999999999", "5511999999999"),  # Com + no início
            ("11 99999-9999", "5511999999999"),  # Com formatação
            ("011999999999", "5511999999999"),  # Com 0 no DDD
            ("999999999", None),  # Número inválido
            ("5511999999", None)  # Número curto
        ]
        
        for input_number, expected in test_cases:
            with self.subTest(input_number=input_number):
                result = format_brazilian_number(input_number)
                self.assertEqual(result, expected)
    
    def test_validate_phone_list(self):
        """Testa a validação de uma lista de números"""
        input_numbers = [
            "11999999999",  # Válido
            "5511999999999",  # Válido
            "999999",  # Inválido
            "11 99999-9999",  # Válido
            "abc123"  # Inválido
        ]
        
        valid_numbers, invalid_numbers = validate_phone_list(input_numbers)
        
        self.assertEqual(len(valid_numbers), 3)
        self.assertEqual(len(invalid_numbers), 2)
        
        # Verifica se todos os números válidos estão no formato correto
        for number in valid_numbers:
            self.assertEqual(len(number), 13)
            self.assertTrue(number.startswith("55"))

if __name__ == '__main__':
    unittest.main()
