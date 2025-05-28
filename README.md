# Projekt portal SCiNET  
1. Klonowanie projektu

```sh
git clone https://github.com/CuriousCocainist/merito-2025.git
```

2. Tworzenie wirtualnej zmiennej środowiskowej
```shell
python -m venv .venv
```

3. Aktywacja zmiennej środowiskowej
```shell
.venv/Scripts/activate
```

4. Instralacja pakietów / paczek
```shell
pip install -r requirements.txt
```
5. Stworzenie / podłączenie bazy danych postgresql
   - stworzenie pliku .env
   - skopiowanie zawartości z pliku .env.example
   - wklejenie zawartości do pliku .env
   - uzupełnienie od dane lokalne (Twoje dane konfiguracyjne)

6 .Wywołanie migracji (podstawowej)
```shell
python manage.py migrate
```

7. Wgranie przykładowych danych do projektu
```sh
python manage.py seed_users
python manage.py seed_articles
```

8. Postawienie frontu (Musisz mieć zainstalowanego  [Node](https://nodejs.org/en) z Chocolatey - czyli zaznaczyć checkbox podczas instalacji)
Wykonaj komendę 
```sh
npm i
```


# Uwaga   
Po każdym pobraniu zmian należy wykonać komendę przebudowania arkuszy styli z tailwindCSS.   
Poniższe polecenie przebuduje tailwindCSS oraz uruchomi obserwowanie zmian na plikach i będzie działało do czasu ctrl + c lub wyłączenia środowiska IDE

```sh
npm run tailwind:dev
```