using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class Room
    {
        public string Id { get; set; } 
        public string Name { get; set; }
        public double PositionX { get; set; }
        public double PositionY { get; set; }
        public int Floor { get; set; }
        public List<Room> Neighbors { get; } = new List<Room>();
        public List<string> Residents { get; } = new List<string>();
        public List<string> OtherNames { get; set; }
        public string ScheduleImagePath { get; set; }

        public Room(string id, string name, double positionX, double positionY, int floor)
        {
            Id = id;
            Name = name;
            PositionX = positionX;
            PositionY = positionY;
            Floor = floor;
            OtherNames = new List<string>();
        }

        // Funkcja do dodawania sasiadow
        public void AddNeighbor(Room neighbor)
        {
            if (!Neighbors.Contains(neighbor))
            {
                Neighbors.Add(neighbor);    
            }
        }

        // Funkcja do dodawania rezydentow
        public void AddResident(string resident)
        {
            Residents.Add(resident);
        }

        // Funkcja do dodawania innych nazw
        public void AddOtherName(string otherName)
        {
            OtherNames.Add(otherName);
        }
        

        // Metoda do wyswietlenia sasiadow w alercie
        public void PrintNeighbors()
        {
            if (Neighbors.Count == 0)
            {
                // Brak sasiadow, wyswietl alert informujacy o tym
                Application.Current.MainPage.DisplayAlert("Sąsiedzi", "Brak sąsiadów dla tego pomieszczenia.", "OK");
            }
            else
            {
                // Sasiedzi istnieja, wygeneruj wiadomosc z nazwami sasiadow
                StringBuilder message = new StringBuilder();
                message.AppendLine("Sąsiedzi dla pomieszczenia " + Name + ":");

                foreach (var neighbor in Neighbors)
                {
                    message.AppendLine("- " + neighbor.Name);
                }

                // Wyswietl alert z lista sasiadow
                Application.Current.MainPage.DisplayAlert("Sąsiedzi", message.ToString(), "OK");
            }
        }
    }
}
