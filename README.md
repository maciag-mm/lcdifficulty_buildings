# lcdifficulty_buildings
[EN]
Semi-automated toolkit for calculating parameters of rural building layout for the assessment of land consolidation difficulty.
License: GNU General Public License v3.0

[PL]
Półautomatyczny zestaw narzędzi do obliczania parametrów zabudowy wiejskiej dla potrzeb analizy trudności prac scalania gruntów.
Licencja: GNU General Public License v3.0

Zawartość repozytorium:
L.p.	Nazwa pliku i rozszerzenie
Typ pliku;	Zastosowanie;	Środowisko obsługi pliku
1.	SALATA 1.3.py;
skrypt w języku Python;	delimitacja obszarów zabudowy metodą Salaty [2019];	QGIS 3.40.0
2.	PAW g1 DŁUGOŚĆ 1.1.py;
skrypt w języku Python;	obliczanie wskaźnika g_1 (długość obszarów zabudowy);	QGIS 3.40.0
3.	PAW g2 WYDŁUŻENIE 1.1.py;
skrypt w języku Python;	obliczanie wskaźnika g_2 (wydłużenie obszarów zabudowy);	QGIS 3.40.0
4.	PAW g3 POWIERZCHNIA 1.1.py;
skrypt w języku Python;	obliczanie wskaźnika g_3 (powierzchnia obszarów zabudowy);	QGIS 3.40.0
5.	PAW g4 LICZBA OBSZARÓW ZABUDOWY 1.1.py;
skrypt w języku Python;	obliczanie wskaźnika g_4 (liczba obszarów zabudowy);	QGIS 3.40.0
6.	PAW g5 LICZBA BUDYNKÓW 1.1.py;
skrypt w języku Python;	obliczanie wskaźnika g_5 (liczba budynków);	QGIS 3.40.0
7.	PAW g6 GĘSTOŚĆ BUDYNKÓW W OBSZ ZAB 1.2.py;
skrypt w języku Python;	obliczanie wskaźnika g_6  (przeciętna liczba budynków na 1 ha obszarów zabudowy);	QGIS 3.40.0
8.	PAW g7 GĘSTOŚĆ BUDYNKÓW W OBR EWID 1.1.py;
skrypt w języku Python;	obliczanie wskaźnika g_7 (przeciętna liczba budynków na 1 ha obrębu ewidencyjnego);	QGIS 3.40.0
9.	PAW g8 g9 KOMIWOJAŻER p1 1.4.py;
skrypt w języku Python;	generowanie plików CSV ze współrzędnymi centroidów budynków (dane wejściowe dla programów G8_06.cpp oraz Komiwoj_NN_07.cpp);	QGIS 3.40.0
10.	PAW g8 ŚREDNIA ODL NAJBL SĄSIADA W OBSZ ZAB p2 2.1.py;
skrypt w języku Python;	obliczanie wskaźnika g_8 (przeciętna odległość pomiędzy budynkami w obszarze zabudowy);	QGIS 3.40.0
11.	G8_06.cpp;
program w języku C++;	przypisanie budynkom najbliższego sąsiada i obliczenie odległości (dane wejściowe dla skryptu PAW g8 ŚREDNIA ODL NAJBL SĄSIADA W OBSZ ZAB p2 2.1.py);	kompilator obsługujący standard C++11
12.	Komiwoj_NN_07.cpp;
program w języku C++;	obliczanie wskaźnika g_9 (długość cyklu Hamiltona dla wszystkich budynków wsi);	kompilator obsługujący standard C++11
13.	SALATA 1.3.model3;
model algorytmów programu QGIS;	delimitacja obszarów zabudowy metodą Salaty [2019];	QGIS 3.40.0
14.	PAW g1 DŁUGOŚĆ 1.1.model3;
model algorytmów programu QGIS;	obliczanie wskaźnika g_1 (długość obszarów zabudowy);	QGIS 3.40.0
15.	PAW g2 WYDŁUŻENIE 1.1.model3;
model algorytmów programu QGIS;	obliczanie wskaźnika g_2 (wydłużenie obszarów zabudowy);	QGIS 3.40.0
16.	PAW g3 POWIERZCHNIA 1.1.model3;
model algorytmów programu QGIS;	obliczanie wskaźnika g_3 (powierzchnia obszarów zabudowy);	QGIS 3.40.0
17.	PAW g4 LICZBA OBSZARÓW ZABUDOWY 1.1.model3;
model algorytmów programu QGIS;	obliczanie wskaźnika g_4 (liczba obszarów zabudowy);	QGIS 3.40.0
18.	PAW g5 LICZBA BUDYNKÓW 1.1.model3;
model algorytmów programu QGIS;	obliczanie wskaźnika g_5 (liczba budynków);	QGIS 3.40.0
19.	PAW g6 GĘSTOŚĆ BUDYNKÓW W OBSZ ZAB 1.2.model3;
model algorytmów programu QGIS;	obliczanie wskaźnika g_6  (przeciętna liczba budynków na 1 ha obszarów zabudowy);	QGIS 3.40.0
20.	PAW g7 GĘSTOŚĆ BUDYNKÓW W OBR EWID 1.1.model3;
model algorytmów programu QGIS;	obliczanie wskaźnika g_7 (przeciętna liczba budynków na 1 ha obrębu ewidencyjnego);	QGIS 3.40.0
21.	PAW g8 g9 KOMIWOJAŻER p1 1.4.model3;
model algorytmów programu QGIS;	generowanie plików CSV ze współrzędnymi centroidów budynków (dane wejściowe dla programów G8_06.cpp oraz Komiwoj_NN_07.cpp);	QGIS 3.40.0
22.	PAW g8 ŚREDNIA ODL NAJBL SASIADA W OBSZ ZAB p2 2.1.model3;
model algorytmów programu QGIS;	obliczanie wskaźnika g_8 (przeciętna odległość pomiędzy budynkami w obszarze zabudowy);	QGIS 3.40.0
23.	LICENSE;
plik tekstowy;	warunki licencyjne;	przeglądarka lub edytor tekstu
24.	README.md;
plik tekstowy;	opis zawartości repozytorium;	przeglądarka lub edytor tekstu
