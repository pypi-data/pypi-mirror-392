# Ziyo dasturlash tili - birinchi misol
# Bu fayl Ziyo tilining asosiy imkoniyatlarini ko'rsatadi

# O'zgaruvchi e'lon qilish
o'zgaruvchi ism = "Ziyo";
o'zgaruvchi yosh = 25;
o'zgaruvchi student = haqiqat;

# Funksiya e'lon qilish
funksiya salom_ber(kim) {
    chiqar("Salom, " + kim + "!");
}

funksiya yosh_hisobla(ism, yil) {
    o'zgaruvchi natija = 2025 - yil;
    chiqar(ism + " ning yoshi: " + str(natija));
    qayt natija;
}

# Shart operatorlari
agar (ism == "Ziyo") {
    chiqar("Bu Ziyo dasturlash tili!");
    chiqar("Dasturlash endi osonroq!");
    
    agar (yosh > 18) {
        chiqar("Siz kattasiz");
    } aks {
        chiqar("Siz hali yosh hisoblanasiz");
    }
} aks {
    chiqar("Noma'lum foydalanuvchi");
}

# Takrorlash (for sikli)
chiqar("\n1 dan 5 gacha sonlar:");
uchun (i = 1; i <= 5; i = i + 1) {
    chiqar("Son: " + str(i));
}

# While sikli
chiqar("\nWhile sikli misoli:");
o'zgaruvchi sanoq = 3;
qilsa (sanoq > 0) {
    chiqar("Qo'ldagi sonlar: " + str(sanoq));
    sanoq = sanoq - 1;
}

chiqar("Tayyor!");

# Funksiya chaqirish
salom_ber(ism);
yosh_hisobla("Ali", 2000);

# Array misoli
o'zgaruvchi mevalar = ["olma", "banan", "uzum"];
chiqar("\nMevalar ro'yxati:");
uchun (i = 0; i < 3; i = i + 1) {
    chiqar(str(i + 1) + ". " + mevalar[i]);
}