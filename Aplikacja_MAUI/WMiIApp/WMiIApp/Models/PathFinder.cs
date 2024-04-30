using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class PathFinder
    {
        public List<Room> Path { get; private set; } = new List<Room>(); // Sciezka

        // Metoda znajdujaca najkrotsza sciezke miedzy dwoma pokojami na podstawie ich obiektow
        public List<Room> FindShortestPath(Room sourceRoom, Room destinationRoom)
        {
            Path.Clear(); // Wyczyszczenie sciezki przed znalezieniem nowej

            var visited = new HashSet<string>(); // Zbior odwiedzonych pokoi
            var queue = new Queue<(Room room, List<Room> path)>(); // Kolejka pokoi do odwiedzenia

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
                    // Znaleziono docelowy pokoj, ustawiamy sciezke i zwracamy ją
                    Path = path;
                    return path;
                }

                if (!visited.Contains(currentRoom.Id))
                {
                    visited.Add(currentRoom.Id); // Oznaczamy pokoj jako odwiedzony

                    // Przechodzimy do sasiednich pokoi
                    foreach (var neighbor in currentRoom.Neighbors)
                    {
                        if (!visited.Contains(neighbor.Id))
                        {
                            var newPath = new List<Room>(path); // Tworzymy nowa kopię sciezki
                            newPath.Add(neighbor); // Dodajemy sasiada do sciezki
                            queue.Enqueue((neighbor, newPath)); // Dodajemy sasiada do kolejki do odwiedzenia
                        }
                    }
                }
            }

            // Jesli nie udalo się znalezc sciezki, zwracamy null
            return null;
        }
    }
}
