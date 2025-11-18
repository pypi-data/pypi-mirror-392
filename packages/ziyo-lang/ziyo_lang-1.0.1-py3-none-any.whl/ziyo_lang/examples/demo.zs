# Ziyo - O'zbekcha dasturlash tili demo
# Bu fayl Ziyo tilining barcha asosiy imkoniyatlarini ko'rsatadi

# 1. O'zgaruvchilar
o'zgaruvchi ism = "Ziyo";
o'zgaruvchi yosh = 25;
o'zgaruvchi student = haqiqat;

# 2. Print operatsiyasi
chiqar("Salom dunyo!");
chiqar("Mening ismim: " + ism);
chiqar("Yoshim: " + str(yosh));

# 3. Funksiyalar
funksiya salom_ber(kim) {
    chiqar("Salom, " + kim + "!");
}

funksiya yosh_korish(kim) {
    chiqar(kim + " ning yoshi: " + str(yosh));
}

# 4. Funksiya chaqirish
salom_ber(ism);
yosh_korish(ism);

# 5. Takrorlash (while sikli)
chiqar("While sikli:");
o'zgaruvchi sanoq = 3;
qilsa (sanoq > 0) {
    chiqar("Sanoq: " + str(sanoq));
    sanoq = sanoq - 1;
}

# 7. Ro'yxatlar
o'zgaruvchi mevalar = ["olma", "banan", "uzum"];
chiqar("Mevalar: " + str(mevalar));

# 8. Hisoblar
o'zgaruvchi a = 10;
o'zgaruvchi b = 5;
o'zgaruvchi natija = a + b;
chiqar("Hisob: " + str(natija));

chiqar("Ziyo dasturi tugadi!");