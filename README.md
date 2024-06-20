# APPreciation
Aplikacja pomagająca wejść w stan koherencji serca dzięki ćwiczeniom oddechowym.

**Koherencja serca** to stan głębokiego spokoju, w którym rytm serca synchronizuje się z oddechem. Tętno lekko przyspiesza podczas wdechu i zwalnia podczas wydechu. Pomóc w osiągnięciu tego stanu może ćwiczenie polegające na wykonywaniu wolnych i spokojnych oddechów. Korzyści z koherencji serca są liczne. Ciało i umysł regenerują się, poprawiają się pamięć i koncentracja, a także odczuwa się więcej pozytywnych emocji takich jak radość i wdzięczność. Dodatkowo obniżają się ciśnienie krwi i poziom kortyzolu, co w efekcie zmniejsza poziom stresu.

## Działanie aplikacji
Tutaj wstawimy zdjęcia/filmik jak działa aplikacja.

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

## Użycie aplikacji
1. Po uruchomieniu aplikacji naciśnij start, aby rozpocząć ćwiczenie oddechowe.
2. Oddychaj zgodnie ze schematem: gdy piłeczka porusza się w górę weź wdech, gdy porusza się poziomo wstrzymaj oddech, a gdy porusza się w dół zrób wydech.
3. Jeśli prędkość oddychania Ci nie odpowiada, możesz zmienić ją w ustawieniach.