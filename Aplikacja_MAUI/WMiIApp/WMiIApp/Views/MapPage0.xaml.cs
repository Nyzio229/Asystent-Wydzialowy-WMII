using WMiIApp.Models;

namespace WMiIApp;

public partial class MapPage0 : ContentPage
{
	public MapPage0()
	{
		InitializeComponent();
	}

    private void HandleRoomButtonClick(object sender, EventArgs e)
    {
        // Pobierz identyfikator kliknietego przycisku
        Button clickedButton = (Button)sender;
        string roomId = clickedButton.ClassId;

        // Znajd� sale w RoomMap
        Room room = App.GlobalRooms.GetRoomById(roomId);

        if (room != null)
        {
            // Wyswietl informacje o sali
            DisplayRoomInfo(room);

        }
    }
    private void HandleRoomButtonClickOnScreen(object sender, EventArgs e)
    {
        // Pobierz identyfikator kliknietego przycisku
        Button clickedButton = (Button)sender;
        string roomId = clickedButton.ClassId;

        // Znajd� sale w RoomMap
        Room room = App.GlobalRooms.GetRoomById(roomId);

        if (room != null)
        {
            // Wyswietl informacje o sali
            DisplayRoomInfoOnScreen(room);
        }
    }

    private void DisplayRoomInfo(Room room)
    {
        string message = $"Nazwa sali: {room.Name}\n" +
                         $"Pi�tro: {room.Floor}\n";

        if (room.Residents.Any())
        {
            message += "Rezydenci:\n";
            foreach (string resident in room.Residents)
            {
                message += $"- {resident}\n";
            }
        }
        else
        {
            message += "Nikt nie posiada tutaj gabinetu.\n";
        }

        // Jesli plan zajec jest dostepny, dodaj go do wiadomosci
        if (!string.IsNullOrEmpty(room.ScheduleImagePath))
        {
            message += "Plan zaj��:\n" + room.ScheduleImagePath + "\n";
        }
        else
        {
            message += "Brak planu zaj�� dla tej sali.\n";
        }

        // Ustawiamy tekst 
        DisplayAlert("Pomieszczenie", message, "OK");
    }
    private void DisplayRoomInfoOnScreen(Room room)
    {
        string message = $"Nazwa sali: {room.Name}\n" +
                         $"Pi�tro: {room.Floor}\n";

        if (room.Residents.Any())
        {
            message += "Rezydenci:\n";
            foreach (string resident in room.Residents)
            {
                message += $"- {resident}\n";
            }
        }
        else
        {
            message += "Nikt nie posiada tutaj gabinetu.\n";
        }

        // Jesli plan zajec jest dostepny, dodaj go do wiadomosci
        if (!string.IsNullOrEmpty(room.ScheduleImagePath))
        {
            message += "Plan zaj��:\n" + room.ScheduleImagePath + "\n";
        }
        else
        {
            message += "Brak planu zaj�� dla tej sali.\n";
        }

        // Ustawiamy tekst w kontrolce Label
        RoomInfoLabel.Text = message;

        double screenWidth = Width / 1.34;
        double screenHeight = Height / 1.34;
        Content.WidthRequest = screenWidth;
        Content.HeightRequest = screenHeight;
    }
}