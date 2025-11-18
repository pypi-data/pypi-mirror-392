# Oddiy array va ro'yxatlar bilan ishlash

o'zgaruvchi sonlar = [1, 2, 3, 4, 5];
o'zgaruvchi ismlar = ["Ali", "Vali", "Guli", "Nodira"];

chiqar("Sonlar ro'yxati:");
chiqar(sonlar);

chiqar("\nIsmlar ro'yxati:");
chiqar(ismlar);

# Array elementlarini o'zgartirish
o'zgaruvchi yangi_ismlar = ismlar;
yangi_ismlar[1] = "Mahmud";
chiqar("\nO'zgartirilgan ro'yxat:");
chiqar(yangi_ismlar);

# Sonlarning yig'indisini hisoblash
o'zgaruvchi summa = 0;
o'zgaruvchi i = 0;
qilsa (i < len(sonlar)) {
    summa = summa + sonlar[i];
    i = i + 1;
}

chiqar("\nSonlarning yig'indisi: " + str(summa));
chiqar("O'rtacha qiymat: " + str(summa / len(sonlar)));