using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class PathFinder
    {
        public ObservableCollection<Room> Path { get; private set; } = new ObservableCollection<Room>(); // Sciezka

        // Metoda znajdujaca najkrotsza sciezke miedzy dwoma pokojami na podstawie ich obiektow
        public List<Room> FindShortestPath(Room sourceRoom, Room destinationRoom)
        {
            var visited = new HashSet<string>(); // Zbior odwiedzonych pokoi
            var queue = new Queue<(Room room, List<Room> path)>(); // Kolejka pokoi do odwiedzenia
            ObservableCollection<Room> newPath = new ObservableCollection<Room>(); // Nowa ścieżka

            if (sourceRoom == null || destinationRoom == null)
            {
                // Niepoprawne argumenty, zwracamy null
                return null;
            }

            // Dodajemy pierwszy pokoj do kolejki
            queue.Enqueue((sourceRoom, new List<Room> { sourceRoom }));

            while (queue.Any())
            {
                var (currentRoom, path) = queue.Dequeue(); // Pobieramy pierwszy element z kolejki

                if (currentRoom == destinationRoom)
                {
                    // Znaleziono docelowy pokoj, ustawiamy sciezke i zwracamy ja
                    newPath = new ObservableCollection<Room>(path);
                    Path = newPath; // Aktualizacja sciezki w kolekcji obserwowanej
                    return path;
                }

                if (!visited.Contains(currentRoom.Id))
                {
                    visited.Add(currentRoom.Id); // Oznaczamy pokoj jako odwiedzony

                    // Przechodzimy do sąsiednich pokoi
                    foreach (var neighbor in currentRoom.Neighbors)
                    {
                        if (!visited.Contains(neighbor.Id))
                        {
                            var newRoomList = new List<Room>(path); // Tworzymy nowa kopie sciezki
                            newRoomList.Add(neighbor); // Dodajemy sasiada do sciezki
                            queue.Enqueue((neighbor, newRoomList)); // Dodajemy sasiada do kolejki do odwiedzenia
                        }
                    }
                }
            }

            // Jesli nie udalo sie znalezc sciezki, zwracamy null
            return null;
        }

    }
}
