using CommunityToolkit.Maui.Core.Platform;
using System.Collections.ObjectModel;
using System.Text;
using WMiIApp.Models;

namespace WMiIApp;

public partial class MapPage_1 : ContentPage
{
    private List<string> allRoomNames; // Lista wszystkich nazw pokoi
    private List<string> filteredRoomNames; // Lista nazw pokoi startowych po zastosowaniu filtru

    public MapPage_1()
	{
		InitializeComponent();

        // Inicjalizacja listy nazw pokojow
        allRoomNames = App.GlobalRooms.GetRooms().Select(room => room.Name).OrderBy(name => name).ToList();
        filteredRoomNames = allRoomNames;

        App.pathFinder.Path.CollectionChanged += Path_CollectionChanged;
    }

    private void HandleRoomButtonClick(object sender, EventArgs e)
    {
        // Pobierz identyfikator kliknietego przycisku
        Button clickedButton = (Button)sender;
        string roomId = clickedButton.ClassId;

        // Znajdz sale w RoomMap
        Room room = App.GlobalRooms.GetRoomById(roomId);

        if (room != null)
        {
            // Wyswietl informacje o sali
            DisplayRoomInfo(room);
        }
    }

    private async void DisplayRoomInfo(Room room)
    {
        string message = $"Nazwa sali: {room.Name}\n" +
                         $"Piêtro: {room.Floor}\n";

        // Wyswietlanie innych nazw, jesli s¹ dostêpne
        if (room.OtherNames.Any())
        {
            message += "Inne Nazwy: ";
            foreach (string otherName in room.OtherNames)
            {
                message += $" {otherName} ";
            }
            message += "\n";
        }

        if (room.Residents.Any())
        {
            message += "Rezydenci: ";
            foreach (string resident in room.Residents)
            {
                message += $" {resident} ";
            }

            message += "\n";
        }

        // Jesli plan zajec jest dostepny, dodaj go do wiadomosci
        if (!string.IsNullOrEmpty(room.ScheduleImagePath))
        {
            message += "Plan zajêæ:\n" + room.ScheduleImagePath + "\n";
        }

        // Wyswietlanie alertu z dodatkowa opcj¹
        bool isTrasaClicked = await DisplayAlert("Pomieszczenie", message, "OK", "Trasa");
        if (!isTrasaClicked)
        {
            // Wyswietlanie arkusza dzialan z dwiema opcjami
            string actionResult = await DisplayActionSheet("Wybierz akcjê", "Anuluj", null, "Dodaj jako miejsce startowe", "Dodaj jako miejsce docelowe");
            if (actionResult == "Dodaj jako miejsce startowe")
            {
                sourceRoomListView.SelectedItem = room.Name;
            }
            else if (actionResult == "Dodaj jako miejsce docelowe")
            {
                destinationRoomListView.SelectedItem = room.Name;
            }
        }
    }
   
    private void OnSourceSearchBarTextChanged(object sender, TextChangedEventArgs e)
    {
        if (!string.IsNullOrEmpty(sourceSearchBar.Text))
        {
            string filterText = sourceSearchBar.Text.ToLower();
            List<string> filteredRoomNames = allRoomNames.Where(roomName => roomName.ToLower().Contains(filterText)).ToList();
            sourceRoomListView.ItemsSource = filteredRoomNames;
            sourceRoomListView.IsVisible = true;
        }
        else
        {
            sourceRoomListView.IsVisible = false; // Ukrywamy CollectionView gdy tekst jest pusty
        }
    }

    private void OnSourceRoomListViewSelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (e.CurrentSelection.FirstOrDefault() != null)
        {
            string selectedRoom = (string)e.CurrentSelection.FirstOrDefault();

            sourceRoomListView.IsVisible = false;

            sourceSearchBar.Text = selectedRoom;

            sourceSearchBar.HideKeyboardAsync();
        }
    }

    private void OnDestinationSearchBarTextChanged(object sender, TextChangedEventArgs e)
    {
        if (!string.IsNullOrEmpty(destinationSearchBar.Text))
        {
            string filterText = destinationSearchBar.Text.ToLower();
            List<string> filteredRoomNames = allRoomNames.Where(roomName => roomName.ToLower().Contains(filterText)).ToList();
            destinationRoomListView.ItemsSource = filteredRoomNames;
            destinationRoomListView.IsVisible = true; 
        }
        else
        {
            destinationRoomListView.IsVisible = false; // Ukrywamy CollectionView gdy tekst jest pusty
        }
    }


    private void OnDestinationRoomListViewSelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (e.CurrentSelection.FirstOrDefault() != null)
        {
            string selectedRoom = (string)e.CurrentSelection.FirstOrDefault();

            destinationRoomListView.IsVisible = false;

            destinationSearchBar.Text = selectedRoom;

            destinationSearchBar.HideKeyboardAsync();
        }
    }

    // Metoda wywo³ywana po kliknieciu przycisku "Wyznacz trase"
    private void OnCalculateRouteClicked(object sender, EventArgs e)
    {
        string sourceRoomName = (string)sourceRoomListView.SelectedItem;
        string destinationRoomName = (string)destinationRoomListView.SelectedItem;

        // Pobieramy obiekty pokoi na podstawie ich nazw
        Room sourceRoom = App.GlobalRooms.FindByName(sourceRoomName);
        Room destinationRoom = App.GlobalRooms.FindByName(destinationRoomName);

        if (sourceRoom == null || destinationRoom == null)
        {
            // Niepoprawne argumenty, wyœwietlamy alert
            DisplayAlert("B³¹d", "Nie mo¿na znaleŸæ pokoju Ÿród³owego lub docelowego.", "OK");
            return;
        }

        // Znajdujemy najkrotsza sciezke miêdzy pokojami
        List<Room> shortestPath = App.pathFinder.FindShortestPath(sourceRoom, destinationRoom);

        if (shortestPath == null)
        {
            // Nie udalo siê znalezc sciezki, wyswietlamy alert
            DisplayAlert("B³¹d", "Nie mo¿na znaleŸæ œcie¿ki.", "OK");
        }
        else
        {
            // Znaleziono sciezke, wyswietlamy alert z lista pokoi
            string message = "Znaleziona droga:\n";
            foreach (var room in shortestPath)
            {
                message += room.Name + "\n";
            }
            DisplayAlert("Znaleziona droga", message, "OK");
        }

    }

    private void OnShowMenuButtonClicked(object sender, EventArgs e)
    {
        // Zmien widocznosc okna menu
        if (menuGrid.IsVisible == false)
            menuGrid.IsVisible = true;
        else menuGrid.IsVisible = false;
    }

    private void Path_CollectionChanged(object sender, System.Collections.Specialized.NotifyCollectionChangedEventArgs e)
    {
            graphics_1.Invalidate();
        var newPage = new MapPage_1(); 
        Navigation.PushAsync(newPage);

        // Zamykanie bie¿¹cej strony
        Navigation.PopAsync();
    }

}