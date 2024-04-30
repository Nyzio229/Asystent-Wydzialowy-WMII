using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{

    public class RoomMap
    {
        private readonly List<Room> rooms = new List<Room>();

        public void AddRoom(Room room)
        {
            if (room == null)
            {
                throw new ArgumentNullException(nameof(room));
            }

            rooms.Add(room);
        }

        public Room GetRoomById(string id)
        {
            return rooms.FirstOrDefault(r => r.Id == id);
        }

        public List<Room> GetRooms()
        {
            return rooms;
        }

        // Metoda znajdująca pokój na podstawie jego nazwy
        public Room FindByName(string name)
        {
            return rooms.FirstOrDefault(r => r.Name == name);
        }

    }

}
