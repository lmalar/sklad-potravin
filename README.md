# 📦 Sklad potravin (Domácí evidence zásob)

Jednoduchá a responzivní webová aplikace pro správu domácích zásob. Umožňuje snadno evidovat potraviny ve spíži, lednici či mrazáku pomocí skenování čárových kódů z mobilu nebo webkamery. 

## ✨ Hlavní funkce
*   **Skenování čárových kódů:** Integrovaná čtečka kódů přes kameru zařízení (využívá HTML5).
*   **Chytré doplňování:** Automatické načítání názvů produktů z celosvětové databáze [Open Food Facts](https://cz.openfoodfacts.org/).
*   **Rychlá správa kusů:** Tlačítka `+` a `-` pro okamžitou úpravu stavu zásob (při snížení na 0 se produkt automaticky smaže).
*   **Sledování expirace:** Barevné zvýraznění produktů, kterým se blíží datum spotřeby (žlutá pro aktuální/příští měsíc, červená pro prošlé).
*   **Dynamické sklady:** Aplikace si pamatuje vaše umístění (např. Lednice, Sklep) a umožňuje jejich snadné přidávání i hromadné mazání.

## 🚀 Technologie
*   **Backend:** Python 3, Flask, SQLAlchemy (SQLite)
*   **Frontend:** HTML5, Bootstrap 5, JavaScript (html5-qrcode)
*   **Prostředí:** Docker a Docker Compose

## 🛠️ Instalace a spuštění

Aplikace je plně kontejnerizovaná pro snadné nasazení pomocí Dockeru.

1. Naklonujte si tento repozitář:
   ```bash
   git clone [https://github.com/VASE_JMENO/sklad-potravin.git](https://github.com/VASE_JMENO/sklad-potravin.git)
   cd sklad-potravin
