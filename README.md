# APPreciation
Aplikacja pomagająca wejść w stan koherencji serca dzięki ćwiczeniom oddechowym.

**Koherencja serca** to stan głębokiego spokoju, w którym rytm serca synchronizuje się z oddechem. Tętno lekko przyspiesza podczas wdechu i zwalnia podczas wydechu. Pomóc w osiągnięciu tego stanu może ćwiczenie polegające na wykonywaniu wolnych i spokojnych oddechów. Korzyści z koherencji serca są liczne. Ciało i umysł regenerują się, poprawiają się pamięć i koncentracja, a także odczuwa się więcej pozytywnych emocji takich jak radość i wdzięczność. Dodatkowo obniżają się ciśnienie krwi i poziom kortyzolu, co w efekcie zmniejsza poziom stresu.

## Funkcje
* Ćwiczenie oddechowe, które pomoże zsynchronizować oddech z rytmem serca.
* Możliwość spersonalizowania długości wdechu i wydechu do indywidualnych potrzeb.
* Monitorowanie tętna oraz zmienności rytmu zatokowego.
* Wizualizacja poziomu koherencji serca

## Wymagania
* Wzmacniacz Perun_32

## Instalacja

1. **Sklonuj repozytorium:**

   ```bash
   git clone git@gitlab.com:neuroinf_uw_24/ekg_coherence.git
   cd ekg_coherence
   ```

2. **Uruchom skrypt instalacyjny:**

    Dla macOS i Linux:
    ```bash
    bash setup.sh 
    ```
    Dla Windows:
    ```bat
    .\setup.bat      
    ```

3. **Aktywuj wirtualne środowisko:**

    Dla macOS i Linux:
    ```bash
    source .venv/bin/activate 
    ```
    Dla Windows:
    ```PowerShell
    .venv\Scripts\activate
    ```
## Uruchomienie aplikacji 
Aby uruchomić aplikację, użyj następujących poleceń w terminalu, dostosowując opcjonalne argumenty w zależności od potrzeb.

Opcjonalne argumenty:

--mode: Tryb uruchomienia aplikacji. Dostępne opcje: online, offline. (Wymagane)

--chunk_size: Rozmiar fragmentu danych do przetwarzania. Domyślna wartość: 16.

--Fs: Częstotliwość próbkowania. Domyślna wartość: 500.

--channel: Numer kanału dla trybu online i offline. Domyślna wartość: 32.

--s_path: Ścieżka do sygnału dla trybu offline. Domyślna wartość: test_perun.raw.

--breathing: Ustawienia schematu oddechowego. Format słownika z argumentami odpowiednio:

* hold_zero - czas wstrzymania po wydechu

* inhale - czas wdechu

* hold_one - czas wstrzymania po wdechu

* exhale - czas wydechu

* speed - prędkość ([0 - very slow, 1 - slow, medium, 2 - fast, 3 - very fast])

* loops - liczba powtórzeń schematu

* Domyślna wartość: {'hold_zero':15, 'inhale':10, 'hold_one':15, 'exhale':10, 'speed':-3, 'loops':10}

### Przykładowe uruchomienia
Tryb online:

```bash
python main.py --mode online --chunk_size 16 --Fs 500 --channel 23
```

Tryb offline:

```bash
python main.py --mode offline --chunk_size 16 --Fs 500 --n_ch 1 --channel 0 --s_path test_perun.raw
```


## Użycie aplikacji
1. Po uruchomieniu aplikacji naciśnij start w górnej części aplikacji, aby uruchomić pobieranie sygnału
2. Następnie naciśnij start przy schemacie oddechowym, aby rozpocząć ćwiczenie oddechowe.
3. Oddychaj zgodnie ze schematem: gdy piłeczka porusza się w górę weź wdech, gdy porusza się poziomo wstrzymaj oddech, a gdy porusza się w dół zrób wydech.
4. Jeśli prędkość oddychania Ci nie odpowiada, możesz zmienić ją w ustawieniach.

## Literatura
1. Materiały ze strony brain.fuw.edu.pl do Pracowni Sygnałów Bioelektrycznych
2. "The Coherent Heart" - publikacja Institute of HeartMath