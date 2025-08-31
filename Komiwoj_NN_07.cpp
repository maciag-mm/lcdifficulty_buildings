#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <limits>
#include <dirent.h>
#include <algorithm>

// Struktura do przechowywania wspó³rzêdnych i danych wierzcho³ka
struct Vertex {
    std::string zid;
    int bid;
    double x;
    double y;
    bool visited = false;
};

// Funkcja do obliczenia odleg³oœci kartezjañskiej
double euclideanDistance(const Vertex& a, const Vertex& b) {
    return std::sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}

// Funkcja do wczytywania wierzcho³ków z pliku CSV
void readVertices(const std::string& filepath, std::vector<Vertex>& vertices) {
    std::ifstream file(filepath.c_str());
    if (!file.is_open()) {
        std::cerr << "Nie uda³o siê otworzyæ pliku: " << filepath << std::endl;
        exit(1);
    }

    std::string line;
    getline(file, line);  // Pomijamy nag³ówek

    while (getline(file, line)) {
        std::stringstream ss(line);
        Vertex vertex;
        std::string temp;

        getline(ss, vertex.zid, ',');
        getline(ss, temp, ',');
        vertex.bid = atoi(temp.c_str());

        getline(ss, temp, ',');
        vertex.x = atof(temp.c_str());

        getline(ss, temp, ',');
        vertex.y = atof(temp.c_str());

        vertices.push_back(vertex);
    }
    file.close();
}

// Funkcja wyboru wierzcho³ka pocz¹tkowego o najni¿szym BID
int findStartVertex(const std::vector<Vertex>& vertices) {
    auto it = std::min_element(vertices.begin(), vertices.end(), [](const Vertex& a, const Vertex& b) {
        return a.bid < b.bid;
    });
    return it->bid;
}

// Algorytm najbli¿szego s¹siada
void nearestNeighborTSP(const std::vector<Vertex>& vertices, int start_bid, std::vector<int>& path, std::vector<Vertex>& ordered_vertices) {
    std::vector<Vertex> verts = vertices;
    int n = verts.size();
    int start_index = -1;
    for (int i = 0; i < n; ++i) {
        if (verts[i].bid == start_bid) {
            start_index = i;
            break;
        }
    }

    if (start_index == -1) {
        std::cerr << "Nie znaleziono wierzcho³ka pocz¹tkowego o BID: " << start_bid << std::endl;
        exit(1);
    }

    path.push_back(verts[start_index].bid);
    ordered_vertices.push_back(verts[start_index]);
    verts[start_index].visited = true;
    int current_index = start_index;
    double total_distance = 0.0;

    for (int step = 1; step < n; ++step) {
        double min_dist = std::numeric_limits<double>::infinity();
        int next_index = -1;

        for (int i = 0; i < n; ++i) {
            if (!verts[i].visited) {
                double dist = euclideanDistance(verts[current_index], verts[i]);
                if (dist < min_dist) {
                    min_dist = dist;
                    next_index = i;
                }
            }
        }

        if (next_index != -1) {
            path.push_back(verts[next_index].bid);
            ordered_vertices.push_back(verts[next_index]);
            total_distance += min_dist;
            verts[next_index].visited = true;
            current_index = next_index;
        }
    }

    // Powrót do punktu pocz¹tkowego
    total_distance += euclideanDistance(verts[current_index], verts[start_index]);
    path.push_back(verts[start_index].bid);
    ordered_vertices.push_back(verts[start_index]);
}

// Funkcja do zapisu plików wynikowych
void saveResults(const std::string& inputFilePath, const std::vector<int>& path, const std::vector<Vertex>& ordered_vertices, double total_distance) {
    std::string baseName = inputFilePath.substr(0, inputFilePath.find_last_of("."));

    // Plik szczegó³owy
    std::ofstream detailedFile(baseName + "_sciezka_szczegolowa.txt");
    double cumulative_distance = 0.0;

    for (size_t i = 0; i < ordered_vertices.size(); ++i) {
        double distance_from_previous = 0.0;
        if (i > 0) {
            distance_from_previous = euclideanDistance(ordered_vertices[i - 1], ordered_vertices[i]);
            cumulative_distance += distance_from_previous;
        }

        detailedFile << ordered_vertices[i].bid << ","
                     << std::fixed << std::setprecision(2) << distance_from_previous << ","
                     << cumulative_distance << ","
                     << ordered_vertices[i].x << ","
                     << ordered_vertices[i].y << ","
                     << ordered_vertices[i].zid << std::endl;
    }
    detailedFile.close();

    // Plik OUT
     std::ofstream summaryFile(baseName + "_OUT.txt");

    double average_distance = cumulative_distance / (ordered_vertices.size() - 1);
    summaryFile << inputFilePath << "," << cumulative_distance << "," << average_distance << std::endl;

    summaryFile.close();
}

// Funkcja do listowania plików w katalogu
std::vector<std::string> listCsvFiles(const std::string& folderPath) {
    std::vector<std::string> csvFiles;
    DIR* dir;
    struct dirent* ent;
    if ((dir = opendir(folderPath.c_str())) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            std::string fileName = ent->d_name;
            if (fileName.size() > 4 && fileName.substr(fileName.size() - 4) == ".csv") {
                csvFiles.push_back(folderPath + "/" + fileName);
            }
        }
        closedir(dir);
    } else {
        std::cerr << "Nie uda³o siê otworzyæ folderu: " << folderPath << std::endl;
    }
    return csvFiles;
}

int main() {
    std::string folderPath;
    std::cout << "Podaj œcie¿kê do folderu z plikami CSV: ";
    std::cin >> folderPath;

    std::vector<std::string> csvFiles = listCsvFiles(folderPath);

    for (const auto& inputFilePath : csvFiles) {
        std::vector<Vertex> vertices;
        readVertices(inputFilePath, vertices);

        int start_bid = findStartVertex(vertices);
        std::vector<int> path;
        std::vector<Vertex> ordered_vertices;

        nearestNeighborTSP(vertices, start_bid, path, ordered_vertices);

        // Obliczenie ca³kowitej odleg³oœci
        double total_distance = 0.0;
        for (size_t i = 1; i < ordered_vertices.size(); ++i) {
            total_distance += euclideanDistance(ordered_vertices[i - 1], ordered_vertices[i]);
        }

        // Zapis wyników
        saveResults(inputFilePath, path, ordered_vertices, total_distance);

        std::cout << "Wyniki zapisane dla pliku: " << inputFilePath << std::endl;
    }
    return 0;
}
