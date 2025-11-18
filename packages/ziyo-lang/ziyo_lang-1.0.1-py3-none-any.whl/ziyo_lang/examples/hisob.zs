# Hisob va matematik operatsiyalar misollari

o'zgaruvchi a = 10;
o'zgaruvchi b = 5;

chiqar("a = " + str(a));
chiqar("b = " + str(b));
chiqar("Qo'shish: " + str(a + b));
chiqar("Ayirish: " + str(a - b));
chiqar("Ko'paytirish: " + str(a * b));
chiqar("Bo'lish: " + str(a / b));

# Funksiya misoli - kvadrat hisoblash
funksiya kvadrat(son) {
    qayt son * son;
}

o'zgaruvchi n = 7;
o'zgaruvchi natija = kvadrat(n);
chiqar(str(n) + " ning kvadrati: " + str(natija));

# Matematik funksiyalar uchun
o'zgaruvchi pi = 3.14159;
chiqar("Pi soni: " + str(pi));

o'zgaruvchi katta_son = 123456789;
chiqar("Katta son: " + str(katta_son));