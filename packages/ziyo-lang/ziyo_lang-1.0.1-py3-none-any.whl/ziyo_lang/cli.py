"""
Ziyo dasturlash tili CLI moduli
ziyo-run buyrug'i uchun asosiy interfeys
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from .compiler import ZiyoTranspiler, validate_code


def create_parser() -> argparse.ArgumentParser:
    """CLI parser yaratish"""
    parser = argparse.ArgumentParser(
        prog="ziyo-run",
        description="Ziyo - O'zbekcha dasturlash tili",
        epilog="""
        Misollar:
            ziyo-run salom.zs              # Faylni bajarish
            ziyo-run salom.zs --show-py    # Transpiled Python kodini ko'rsatish
            ziyo-run salom.zs --check      # Faqat sintaksis tekshirish
            ziyo-run --version             # Versiyani ko'rsatish
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help=".zs fayl manzili"
    )
    
    parser.add_argument(
        "--show-py", "--show-python",
        action="store_true",
        help="Transpiled Python kodini ko'rsatish"
    )
    
    parser.add_argument(
        "--check", "--syntax-check",
        action="store_true",
        help="Faqat sintaksis tekshirish, kodni bajarmaslik"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Ziyo 1.0.0"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Chuqur ma'lumot ko'rsatish"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Natijani faylga yozish (Python kodi uchun)"
    )
    
    return parser


def load_ziyo_file(filepath: str) -> str:
    """Ziyo faylini yuklash"""
    file_path = Path(filepath)
    
    if not file_path.exists():
        print(f"Xato: Fayl topilmadi: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    if not file_path.suffix == ".zs":
        print(f"Ogohlantirish: .zs kengaytmasi bo'lmagan fayl: {filepath}", file=sys.stderr)
    
    try:
        content = file_path.read_text(encoding="utf-8")
        return content
    except UnicodeDecodeError:
        print(f"Xato: Fayl UTF-8 kodlash bilan o'qilmadi: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Xato: Fayl o'qishda xato: {e}", file=sys.stderr)
        sys.exit(1)


def save_output(content: str, output_path: str):
    """Natija faylini saqlash"""
    try:
        output_file = Path(output_path)
        output_file.write_text(content, encoding="utf-8")
        print(f"Natija faylga saqlandi: {output_path}")
    except Exception as e:
        print(f"Xato: Fayl saqlashda xato: {e}", file=sys.stderr)
        sys.exit(1)


def run_ziyo_code(ziyo_code: str, show_python: bool = False, verbose: bool = False):
    """Ziyo kodini bajarish"""
    transpiler = ZiyoTranspiler()
    
    is_valid, errors = validate_code(ziyo_code)
    if not is_valid:
        print("Sintaksis xatolari topildi:", file=sys.stderr)
        for error in errors:
            print(f"  • {error}", file=sys.stderr)
        sys.exit(1)
    
    python_code = transpiler.transpile(ziyo_code)
    
    if show_python or verbose:
        print("─" * 50)
        print("Transpiled Python kodi:")
        print("─" * 50)
        print(python_code)
        print("─" * 50)
    
    try:
        transpiler.run(ziyo_code)
    except Exception as e:
        print(f"Bajarish xatosi: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Asosiy CLI funksiyasi"""
    parser = create_parser()
    args = parser.parse_args()
    
    if hasattr(args, 'version') and args.version is not None:
        return
    
    if not args.file:
        parser.error("Fayl argumenti kerak: ziyo-run fayl.zs")
    
    ziyo_code = load_ziyo_file(args.file)
    
    if args.verbose:
        print(f"Fayl yuklandi: {args.file}")
        print(f"Kod uzunligi: {len(ziyo_code)} belgi")
    
    if args.check:
        is_valid, errors = validate_code(ziyo_code)
        if is_valid:
            print("✓ Sintaksis to'g'ri")
        else:
            print("✗ Sintaksis xatolari:")
            for error in errors:
                print(f"  • {error}")
            sys.exit(1)
        return
    
    if args.show_py:
        transpiler = ZiyoTranspiler()
        python_code = transpiler.transpile(ziyo_code)
        
        if args.output:
            save_output(python_code, args.output)
        else:
            print(python_code)
        return
    
    run_ziyo_code(ziyo_code, show_python=args.show_py, verbose=args.verbose)


def interactive_mode():
    """Interaktiv rejim (kelajakda qo'shiladi)"""
    print("Ziyo interaktiv rejim hali ishlab chiqilmagan.")
    print("Fayl bilan ishlash uchun: ziyo-run fayl.zs")


if __name__ == "__main__":
    main()