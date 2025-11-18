# Ziyo - O'zbekcha Dasturlash Tili

Ziyo - bu o'zbek tilida yozilgan va Python ga transpile qilinuvchi dasturlash tili. U oson o'rganiladigan va barcha qurilmalarda ishlaydi.

## ✨ Xususiyatlari

- ✅ O'zbekcha kalit so'zlar
- ✅ Python ga transpile qilinadi
- ✅ Cross-platform (Linux, Windows, macOS, Android Termux)
- ✅ Oson o'rganish
- ✅ CLI buyruqlari
- ✅ Sintaksis tekshirish

## 🚀 O'rnatish

### pip orqali (Kelajakda)

```bash
pip install ziyo-lang
```

## 📖 Foydalanish

### CLI Buyruqlari

```bash
# .zs faylni bajarish
ziyo-run salom.zs

# Transpiled Python kodini ko'rsatish
ziyo-run salom.zs --show-py

# Sintaksis tekshirish
ziyo-run salom.zs --check

# Batafsil ma'lumot
ziyo-run --help

# Versiya ko'rsatish
ziyo-run --version
```

### Python Kutubxona sifatida

```python
import ziyo_lang

# Ziyo kodini Python kodiga aylantirish
ziyo_code = '''
o'zgaruvchi ism = "Zafar";
chiqar("Salom, " + ism + "!");
'''

# Transpile qilish
python_code = ziyo_lang.transpile(ziyo_code)
print(python_code)

# Kodni bajarish
ziyo_lang.run(ziyo_code)

# Sinov qilish
is_valid, errors = ziyo_lang.validate_code(ziyo_code)
if not is_valid:
    for error in errors:
        print(f"Xato: {error}")
```

## 🔤 Kalit So'zlar

| Ziyo | Python | Tavsif |
|------|--------|--------|
| `chiqar()` | `print()` | Chop etish |
| `funksiya` | `def` | Funksiya e'lon qilish |
| `o'zgaruvchi` | `var` | O'zgaruvchi e'lon qilish |
| `agar` | `if` | Shart operatori |
| `aks` | `else` | Agar shart bo'lmasa |
| `uchun` | `for` | Takrorlash sikli |
| `qilsa` | `while` | Shartli takrorlash |
| `qayt` | `return` | Qiymat qaytarish |
| `haqiqat` | `True` | Haqiqiy qiymat |
| `yolg'on` | `False` | Yolg'on qiymat |

## 💻 Misol Dasturlar

### Salom Dunyo

```ziyo
# Izoh - bu qator e'tiborga olinmaydi
chiqar("Salom, Dunyo!");

# O'zgaruvchi e'lon qilish
o'zgaruvchi ism = "Anvar";
chiqar("Mening ismim " + ism);

# Funksiya
funksiya salom(kim) {
    chiqar("Salom, " + kim + "!");
}

salom(ism);
```

### Hisoblovchi Dastur

```ziyo
o'zgaruvchi son = 5;

agar (son > 0) {
    chiqar("Son musbat");
} aks {
    chiqar("Son manfiy yoki nol");
}

# For sikli
uchun (i = 1; i <= son; i = i + 1) {
    chiqar("Hisoblash: " + i);
}
```

### Funksiya Misoli

```ziyo
funksiya qoshish(a, b) {
    o'zgaruvchi natija = a + b;
    qayt natija;
}

o'zgaruvchi x = 10;
o'zgaruvchi y = 20;
o'zgaruvchi summa = qoshish(x, y);

chiqar("Natija: " + summa);
```

## 📝 Sintaksis

### O'zgaruvchilar

```ziyo
# Son
o'zgaruvchi yosh = 25;

# Matn
o'zgaruvchi ism = "Aziz";

# Boolean
o'zgaruvchi student = haqiqat;

# Ro'yxat (array)
o'zgaruvchi mevalar = ["olma", "banan"];
```

### Shart Operatorlari

```ziyo
agar (shart) {
    # kod
} aks {
    # boshqa kod
}

agar (yosh >= 18) {
    chiqar("Katta");
} aks {
    chiqar("Kichik");
}
```

### Takrorlash

```ziyo
# For sikli
uchun (i = 1; i <= 5; i = i + 1) {
    chiqar(i);
}

# While sikli
o'zgaruvchi son = 3;
qilsa (son > 0) {
    chiqar("Son: " + son);
    son = son - 1;
}
```

### Funksiyalar

```ziyo
funksiya nom(param1, param2) {
    o'zgaruvchi natija = param1 + param2;
    qayt natija;
}

# Chaqirish
o'zgaruvchi javob = nom(5, 3);
```

## 🖥️ Platformalar

- 🐧 Linux (barcha distributsiyalar)
- 🪟 Windows 10/11
- 🍎 macOS 10.14+
- 📱 Android Termux
- 🌐 Web (JavaScript orqali, kelajakda)

## 🔧 Kengaytirish

### Kelgusi Xususiyatlar

- [ ] OOP qo'llab-quvvatlash (class, obyekt)
- [ ] Import moduli
- [ ] Fayl operatsiyalari
- [ ] Xatolarni boshqarish (try/except)
- [ ] Web interface
- [ ] IDE extension
- [ ] Online compiler

### O'z xususiyatlaringizni qo'shish

```python
# compiler.py da yangi kalit so'z qo'shish
self.token_map.append((r"\byangisoz\s*\(", "yangifunksiya("))

# Yoki qo'shimcha sintaksis qoidalari
def custom_processing(self, code):
    # Mahsus mantiq
    return processed_code
```

## 🤝 Hissa Qo'shish

1. Repozitoriyani fork qiling
2. Branch yarating: `git checkout -b yangi-xususiyat`
3. O'zgarishlaringizni qo'shing: `git commit -am 'Yangi xususiyat qo'shildi'`
4. Branch ga push qiling: `git push origin yangi-xususiyat`
5. Pull Request yarating

## 📄 Litsenziya

MIT License - batafsil ma'lumot uchun [LICENSE](LICENSE) faylini ko'ring.

## 📞 Aloqa

- 📧 Email: RaKUZENUZ@gmail.com
- 💬 Telegram: @UzMaxBoy

---

**Ziyo dasturlash tili - O'zbek dasturchilari uchun yaratilgan!** 🇺🇿