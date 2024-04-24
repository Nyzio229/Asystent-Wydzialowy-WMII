using System.Text;
using WMiIApp.Models;

namespace WMiIApp;

public partial class MapPage_1 : ContentPage
{
    public MapPage_1()
	{
		InitializeComponent();

    }

    private void HandleRoomButtonClick(object sender, EventArgs e)
    {
        // Pobierz identyfikator kliknietego przycisku
        Button clickedButton = (Button)sender;
        string roomId = clickedButton.ClassId;

        // ZnajdŸ sale w RoomMap
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

        // ZnajdŸ sale w RoomMap
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
                         $"Piêtro: {room.Floor}\n";

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
            message += "Plan zajêæ:\n" + room.ScheduleImagePath + "\n";
        }
        else
        {
            message += "Brak planu zajêæ dla tej sali.\n";
        }

        // Ustawiamy tekst 
        DisplayAlert("Pomieszczenie", message, "OK");
    }
    private void DisplayRoomInfoOnScreen(Room room)
    {
        string message = $"Nazwa sali: {room.Name}\n" +
                         $"Piêtro: {room.Floor}\n";

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
            message += "Plan zajêæ:\n" + room.ScheduleImagePath + "\n";
        }
        else
        {
            message += "Brak planu zajêæ dla tej sali.\n";
        }

        // Ustawiamy tekst w kontrolce Label
        RoomInfoLabel.Text = message;

        double screenWidth = Width / 1.34;
        double screenHeight = Height / 1.34;
        Content.WidthRequest = screenWidth;
        Content.HeightRequest = screenHeight;
    }

    private void routeButton_Clicked(object sender, EventArgs e)
    {

    }
}