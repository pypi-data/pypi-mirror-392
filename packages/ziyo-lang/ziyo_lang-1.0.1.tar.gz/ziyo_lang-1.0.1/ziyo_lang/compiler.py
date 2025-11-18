"""
Ziyo - O'zbekcha dasturlash tili transpiler
Ziyo kodini Python kodiga aylantiradi
"""

import re
import sys
from typing import Dict, List, Tuple

class ZiyoTranspiler:
    def __init__(self):
        self.token_map: List[Tuple[str, str]] = [
        
            (r"\bchiqar\s*\(", "print("),
            (r"\bfunksiya\s+([A-Za-z_][\w]*)\s*\(", r"def \1("),
            
            (r"\bqayt\b", "return"),
            (r"\bo'zgaruvchi\b\s+", ""), 
            (r"\bagar\s*\(", "if ("),
            (r"\baks\b", "else"),
            
            (r"\buchun\b", "for"),
            (r"\bqilsa\b", "while"),
            
            (r"\bhaqiqat\b", "True"),
            (r"\byolg'on\b", "False"),
            
            (r"\btegilma\b", "pass"),
            (r"\brostmi\s*\(", "isinstance("),
        ]
        
        self.context_replacements: Dict[str, str] = {
            "print": "print", 
        }

    def replace_tokens(self, line: str) -> str:
        """Uzbek kalit so'zlarini Python kodiga o'zgartirish"""
        protected_line = ""
        strings = []
        in_string = False
        quote_char = None
        i = 0
        
        while i < len(line):
            char = line[i]
            
            if char in ('"', "'") and not in_string:
                in_string = True
                quote_char = char
                protected_line += char
            elif char == quote_char and in_string:
                if i + 1 < len(line) and line[i + 1] == quote_char:
                    protected_line += char + char
                    i += 1
                else:
                    in_string = False
                    protected_line += char
            else:
                protected_line += char
            
            i += 1
        
        for pattern, replacement in self.token_map:
            protected_line = re.sub(pattern, replacement, protected_line)
        
        return protected_line

    def process_braces(self, code: str) -> str:
        """{ } jingalak qavslarni Python indentatsiyasiga o'zgartirish"""
        lines = code.splitlines()
        indent_level = 0
        result_lines = []
        
        for raw_line in lines:
            stripped_line = raw_line.strip()
            
            if not stripped_line:
                result_lines.append("")
                continue
            

            if stripped_line.endswith("{"):

                content = stripped_line[:-1].strip()
                if content:
                    processed = self.replace_tokens(content)

                    result_lines.append("    " * indent_level + processed + ":")
                else:
                    result_lines.append("    " * indent_level + "pass:")
                indent_level += 1
                
            elif stripped_line == "}":
                indent_level = max(indent_level - 1, 0)
                
            else:
                processed = self.replace_tokens(stripped_line)
                result_lines.append("    " * indent_level + processed)
        
        return "\n".join(result_lines)

    def transpile(self, ziyo_code: str) -> str:
        """
        Ziyo kodini Python kodiga aylantirish
        
        Args:
            ziyo_code: Ziyo tilida yozilgan kod
            
        Returns:
            Python kodi
        """

        if not ziyo_code.strip():
            return ""
            
        ziyo_code = self._convert_english_keywords(ziyo_code)
        
        ziyo_code = self._remove_comments(ziyo_code)
        
        python_code = self.process_braces(ziyo_code)
        
        python_code = self._remove_semicolons(python_code)
        
        return python_code

    def _remove_semicolons(self, code: str) -> str:
        """Oxirgi semicolonlarni o'chirish (string literal'dan boshqa)"""
        lines = code.splitlines()
        cleaned_lines = []
        
        for line in lines:
            if not line.strip():
                cleaned_lines.append("")
                continue
            
            in_string = False
            quote_char = None
            cleaned_line = ""
            i = 0
            
            while i < len(line):
                char = line[i]
                
                if char in ('"', "'") and not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char and in_string:
                	
                    if i + 1 < len(line) and line[i + 1] == quote_char:
                        i += 1
                    else:
                        in_string = False
                elif char == ';' and not in_string:
                    break
                
                cleaned_line += char
                i += 1
            
            cleaned_lines.append(cleaned_line)
        
        return "\n".join(cleaned_lines)

    def _convert_english_keywords(self, code: str) -> str:
        """Inglizcha kalit so'zlarni ham qo'llab-quvvatlash"""
        lines = code.splitlines()
        converted_lines = []
        
        for line in lines:
            converted_line = line
            
            english_to_uzbek = [
                (r"\bprint\s*\(", "chiqar("),
                (r"\bdef\s+([A-Za-z_][\w]*)\s*\(", r"funksiya \1("),
                (r"\breturn\b", "qayt"),
                (r"\bvar\b", "o'zgaruvchi"),
                (r"\bif\s*\(", "agar("),
                (r"\belse\b", "aks"),
                (r"\bfor\b", "uchun"),
                (r"\bwhile\b", "qilsa"),
                (r"\bTrue\b", "haqiqat"),
                (r"\bFalse\b", "yolg'on"),
                (r"\bpass\b", "tegilma"),
                (r"\bisinstance\s*\(", "rostmi("),
            ]
            
            for pattern, replacement in english_to_uzbek:
                converted_line = re.sub(pattern, replacement, converted_line)
            
            converted_lines.append(converted_line)
        
        return "\n".join(converted_lines)

    def _remove_comments(self, code: str) -> str:
        """# bilan boshlangan izohlarni o'chirish"""
        lines = code.splitlines()
        cleaned_lines = []
        
        for line in lines:
        	
            in_string = False
            quote_char = None
            
            cleaned_line = ""
            i = 0
            while i < len(line):
                char = line[i]
                
                if char in ('"', "'") and not in_string:
                    in_string = True
                    quote_char = char
                    cleaned_line += char 
                elif char == quote_char and in_string:
 
                    if i + 1 < len(line) and line[i + 1] == quote_char:
                        cleaned_line += char + char
                        i += 1
                    else:
                        in_string = False
                        quote_char = None
                        cleaned_line += char  
                elif char == '#' and not in_string:

                    break
                else:
                    cleaned_line += char
                    
                i += 1
            
            cleaned_lines.append(cleaned_line)
        
        return "\n".join(cleaned_lines)

    def run(self, ziyo_code: str, globals_dict: dict = None) -> str:
        """
        Ziyo kodini bevosita bajarish
        
        Args:
            ziyo_code: Ziyo tilida yozilgan kod
            globals_dict: Global o'zgaruvchilar lug'ati
            
        Returns:
            Transpiled Python kodi
        """
        if globals_dict is None:
            globals_dict = {}
        
        python_code = self.transpile(ziyo_code)
        
        if python_code.strip():

            exec(python_code, globals_dict)
        
        return python_code

    def validate_code(self, ziyo_code: str) -> Tuple[bool, List[str]]:
        """
        Ziyo kodining sintaksisini tekshirish
        
        Args:
            ziyo_code: Tekshiriladigan kod
            
        Returns:
            (muvafaqiyat, xatoliklar_ro'yxati)
        """
        errors = []
        
        try:
            python_code = self.transpile(ziyo_code)
            
            compile(python_code, '<ziyo>', 'exec')
            
        except SyntaxError as e:
            errors.append(f"Sintaksis xatosi: {e}")
        except Exception as e:
            errors.append(f"Umumiy xato: {e}")
        
        return len(errors) == 0, errors

def transpile(ziyo_code: str) -> str:
    """Ziyo kodini Python kodiga aylantirish"""
    transpiler = ZiyoTranspiler()
    return transpiler.transpile(ziyo_code)

def run(ziyo_code: str, globals_dict: dict = None):
    """Ziyo kodini bajarish"""
    transpiler = ZiyoTranspiler()
    return transpiler.run(ziyo_code, globals_dict)

def validate_code(ziyo_code: str) -> Tuple[bool, List[str]]:
    """Ziyo kodini tekshirish"""
    transpiler = ZiyoTranspiler()
    return transpiler.validate_code(ziyo_code)