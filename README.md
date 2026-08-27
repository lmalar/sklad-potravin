# Sklad potravin

Chytrá webová aplikace pro správu domácích zásob (špajz, lednice, mrazák). Aplikace je navržena primárně pro mobilní telefony, funguje jako PWA (lze ji nainstalovat na plochu) a obsahuje integrovanou čtečku čárových kódů s automatickým dohledáváním názvů v mezinárodních databázích.

## Hlavní funkce
* **Skenování z kamery:** Integrovaná čtečka EAN kódů plně optimalizovaná pro mobilní zařízení.
* **Automatické doplňování:** Kaskádové vyhledávání produktu podle kódu v databázích *Open Food Facts*, *Open Beauty Facts* a *Open Products Facts* (potraviny, kosmetika, drogerie). Aplikace sama extrahuje název a gramáž.
* **Chytrý přehled:** Živé vyhledávání, filtrování podle skladů a řazení kliknutím na hlavičky sloupců (Produkt, Sklad, Expirace).
* **Hlídání trvanlivosti:** Barevné podbarvení položek, kterým se blíží nebo už vypršela expirace (žlutá/červená).
* **PWA (Progresivní webová aplikace):** Možnost přidat si aplikaci na domovskou obrazovku telefonu jako plnohodnotnou nativní aplikaci.
* **Záloha dat:** Export celého skladu do formátu CSV (kompatibilní s MS Excel s podporou české diakritiky).
* **Správa skladů:** Snadné přidávání nových lokací a možnost smazat celou lokaci včetně obsahu.

## Technologický stack
* **Backend:** Python 3.11, Flask, SQLAlchemy (SQLite)
* **Frontend:** HTML5, Bootstrap 5, Vanilla JS, html5-qrcode
* **Nasazení:** Docker & Docker Compose

## Struktura projektu
```text
sklad-potravin/
├── docker-compose.yml     # Konfigurace pro Docker
├── Dockerfile             # Předpis pro sestavení obrazu
├── requirements.txt       # Python závislosti (Flask, SQLAlchemy, requests)
├── app.py                 # Hlavní logika aplikace (backend)
├── data/                  # Zde se automaticky vytvoří databáze sklad.db
├── static/                
│   ├── manifest.json      # Konfigurace pro PWA (instalace na mobil)
│   └── sw.js              # Service Worker pro PWA
└── templates/             
    ├── base.html          # Hlavní šablona a hlavička
    ├── index.html         # Přehled skladu a tabulka
    ├── add.html           # Formulář a skener kódů
    └── edit.html          # Úprava existující položky
```

## Instalace a spuštění (Docker)

Nejjednodušší a doporučený způsob, jak aplikaci spustit, je pomocí Dockeru. Databáze se ukládá do namapované složky `data/`, takže o svá data nepřijdete ani při aktualizaci nebo restartu kontejneru.

### 1. Příprava
Ujistěte se, že máte na svém serveru (nebo Raspberry Pi / PC) nainstalovaný **Docker** a **Docker Compose**. Naklonujte si tento repozitář nebo vytvořte výše uvedenou strukturu souborů.

Příklad souboru `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: sklad_potravin
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```




