#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <limits>
#include <iomanip>
#include <dirent.h>

using namespace std;

// Struktura reprezentuj¹ca punkt
struct Point {
    string layer_name;
    int point_id;
    double x;
    double y;
};

// Funkcja do obliczania odleg³oœci euklidesowej
double euclidean_distance(const Point& p1, const Point& p2) {
    return sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y));
}

// Funkcja do wczytywania danych z pliku CSV
vector<Point> read_csv(const string& filename) {
    vector<Point> points;
    ifstream file(filename);

    if (!file.is_open()) {
        cerr << "Blad otwarcia pliku: " << filename << endl;
        return points;
    }

    string line;
    getline(file, line); // Pomijamy nag³ówek

    while (getline(file, line)) {
        string layer_name;
        int point_id;
        double x, y;

        // Wczytywanie danych w prosty sposób
        size_t pos1 = line.find(',');
        size_t pos2 = line.find(',', pos1 + 1);
        size_t pos3 = line.find(',', pos2 + 1);

        layer_name = line.substr(0, pos1);
        point_id = stoi(line.substr(pos1 + 1, pos2 - pos1 - 1));
        x = stod(line.substr(pos2 + 1, pos3 - pos2 - 1));
        y = stod(line.substr(pos3 + 1));

        points.push_back({layer_name, point_id, x, y});
    }

    file.close();
    return points;
}

// Funkcja do przetwarzania danych i obliczania wyników
void process_points(const vector<Point>& points, const string& input_filename, const string& output_path, ofstream& out_file) {
    double total_distance = 0.0;
    int point_count = points.size();

    // Tworzymy nazwê pliku wynikowego
    string output_filename = output_path + "/g8_DIST_" + input_filename.substr(input_filename.find_last_of("/\\") + 1);
    ofstream dist_file(output_filename);

    if (!dist_file.is_open()) {
        cerr << "Blad otwarcia pliku wynikowego: " << output_filename << endl;
        return;
    }

    // Ustawienie precyzji zapisu liczb zmiennoprzecinkowych
    dist_file << fixed << setprecision(6);
    out_file << fixed << setprecision(6);

    for (int i = 0; i < point_count; ++i) {
        double min_distance = numeric_limits<double>::max();
        int nearest_point_id = -1;

        // Szukanie najbli¿szego s¹siada
        for (int j = 0; j < point_count; ++j) {
            if (i == j) continue;

            double distance = euclidean_distance(points[i], points[j]);
            if (distance < min_distance) {
                min_distance = distance;
                nearest_point_id = points[j].point_id;
            }
        }

        // Zapis wyników do g8_DIST_[nazwa_pliku_wejsciowego].txt
        dist_file << input_filename << "," << points[i].point_id << "," << points[i].x << "," << points[i].y << ","
                  << nearest_point_id << "," << min_distance << endl;

        total_distance += min_distance;
    }

    dist_file.close();

    // Obliczanie œredniej odleg³oœci i zapis do g8_OUT.txt
    double average_distance = total_distance / point_count;
    out_file << input_filename << "," << average_distance << endl;
}

// Funkcja do przeszukiwania folderu w poszukiwaniu plików CSV
vector<string> list_csv_files(const string& folder_path) {
    vector<string> csv_files;
    DIR* dir;
    struct dirent* entry;

    if ((dir = opendir(folder_path.c_str())) != nullptr) {
        while ((entry = readdir(dir)) != nullptr) {
            string filename = entry->d_name;
            if (filename.size() > 4 && filename.substr(filename.size() - 4) == ".csv") {
                csv_files.push_back(folder_path + "/" + filename);
            }
        }
        closedir(dir);
    } else {
        cerr << "Blad otwarcia folderu: " << folder_path << endl;
    }

    return csv_files;
}

int main() {
    string folder_path;
    cout << "Podaj sciezke do folderu z plikami CSV: ";
    cin >> folder_path;

    string output_out_filename = folder_path + "/g8_OUT.txt";
    ofstream out_file(output_out_filename);

    if (!out_file.is_open()) {
        cerr << "Blad otwarcia pliku wynikowego: " << output_out_filename << endl;
        return 1;
    }

    vector<string> csv_files = list_csv_files(folder_path);

    for (const string& filename : csv_files) {
        cout << "Przetwarzanie pliku: " << filename << endl;

        vector<Point> points = read_csv(filename);
        if (points.empty()) {
            cerr << "Blad wczytywania danych z pliku: " << filename << endl;
            continue;
        }

        process_points(points, filename, folder_path, out_file);
    }

    out_file.close();

    cout << "Przetwarzanie zakonczone. Wyniki zapisane do g8_OUT.txt oraz osobnych plikow g8_DIST_[nazwa_pliku].txt." << endl;
    return 0;
}
