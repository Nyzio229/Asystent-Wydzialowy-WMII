using CommunityToolkit.Maui.Core.Platform;
using System.Diagnostics;
using WMiIApp.Models;

namespace WMiIApp;

public partial class MapPage0 : ContentPage
{
    private List<string> allRoomNames; // Lista wszystkich nazw pokoi
    private List<string> filteredRoomNames; // Lista nazw pokoi startowych po zastosowaniu filtru
    double currentScale = 1;
    double startScale = 1;
    double xOffset = 0;
    double yOffset = 0;
    double previousWidth = 0;
    double previousHeight = 0;
    public MapPage0()
	{
		InitializeComponent();
        // Inicjalizacja listy nazw pokojow
        allRoomNames = App.GlobalRooms.GetRooms().Where(room => room.Name != "Korytarz").Select(room => room.Name).OrderBy(name => name).ToList();
        filteredRoomNames = allRoomNames;

        App.pathFinder.Path.CollectionChanged += Path_CollectionChanged;

        Device.StartTimer(TimeSpan.FromSeconds(3), () =>
        {
            graphics0.Invalidate();
            return true;
        });
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

    private void HandleRoomButtonClickStairsOneWayUp(object sender, EventArgs e)
    {
        Shell.Current.GoToAsync("///MapPage1");
    }

    private void HandleRoomButtonClickStairsOneWayDown(object sender, EventArgs e)
    {
        Shell.Current.GoToAsync("///MapPage_1");
    }

    private async void HandleRoomButtonClickStairsTwoWay(object sender, EventArgs e)
    {
        string action = await DisplayActionSheet("", "Zamknij", null, "Piwnica", "I piêtro");
        
        if (action == "Piwnica")
        {
            Shell.Current.GoToAsync("///MapPage_1");
        }
        else if (action == "I piêtro")
        {
            Shell.Current.GoToAsync("///MapPage1");
        }
    }

    private async void DisplayRoomInfo(Room room)
    {
        string message = $"Nazwa sali: {room.Name}\n" +
                         $"Piêtro: {room.Floor}\n";

        if (room.Residents.Any())
        {
            message += "Rezydenci: \n";
            foreach (string resident in room.Residents)
            {
                message += $" -> {resident}\n";
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
                App.sourceRoom = room.Name;
            }
            else if (actionResult == "Dodaj jako miejsce docelowe")
            {
                destinationRoomListView.SelectedItem = room.Name;
                App.destinationRoom = room.Name;
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

            App.sourceRoom = selectedRoom;

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

            App.destinationRoom = selectedRoom;

            destinationSearchBar.HideKeyboardAsync();
        }
    }

    // Metoda wywo³ywana po kliknieciu przycisku "Wyznacz trase"
    private void OnCalculateRouteClicked(object sender, EventArgs e)
    {
        string sourceRoomName = App.sourceRoom;
        string destinationRoomName = App.destinationRoom;

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
            menuGrid.IsVisible = false;

            // Znaleziono sciezke, wyswietlamy alert
            string message = $"Miejsce startowe znajduje siê na {shortestPath[0].Floor} piêtrze.\n";
            message += $"Miejsce docelowe znajduje siê na {shortestPath[shortestPath.Count() - 1].Floor} piêtrze.\n";
            message += "Wyœwietli³em Ci trasê na mapie \n";
            DisplayAlert("Znaleziono trasê", message, "OK");
        }

        if (sourceRoom.Floor == -1)
        {
            Shell.Current.GoToAsync("///MapPage_1");
        }
        else if (sourceRoom.Floor == 0)
        {
            Shell.Current.GoToAsync("///MapPage0");
        }
        else if (sourceRoom.Floor == 1)
        {
            Shell.Current.GoToAsync("///MapPage1");
        }
        else if (sourceRoom.Floor == 2)
        {
            Shell.Current.GoToAsync("///MapPage2");
        }

    }
    private void OnClearRouteClicked(object sender, EventArgs e)
    {
        sourceSearchBar.Text = "";
        destinationSearchBar.Text = "";

        App.sourceRoom = "";
        App.destinationRoom = "";

        App.pathFinder.Path.Clear();
    }

    private void OnShowMenuButtonClicked(object sender, EventArgs e)
    {
        // Zmien widocznosc okna menu
        if (menuGrid.IsVisible == false)
            menuGrid.IsVisible = true;
        else menuGrid.IsVisible = false;

        sourceSearchBar.Text = App.sourceRoom;
        sourceRoomListView.IsVisible = false;
        destinationSearchBar.Text = App.destinationRoom;
        destinationRoomListView.IsVisible = false;
    }

    private void Path_CollectionChanged(object sender, System.Collections.Specialized.NotifyCollectionChangedEventArgs e)
    {
        graphics0.Invalidate();

    }

    void OnPanUpdated(object sender, PanUpdatedEventArgs e)
    {
        if (currentScale > 1 && (e.StatusType == GestureStatus.Running || e.StatusType == GestureStatus.Completed))
        {
            // Interpolacja pozycji obrazka z u¿yciem mnoznika
            double multiplier = 0.5; // Mnoznik interpolacji
            double deltaX = e.TotalX * multiplier;
            double deltaY = e.TotalY * multiplier;

            // Przesun obraz o przesuniecie z uwzglednieniem interpolacji
            Content.TranslationX = Math.Clamp(Content.TranslationX + deltaX, -Content.Width * (currentScale - 1), 0);
            Content.TranslationY = Math.Clamp(Content.TranslationY + deltaY, -Content.Height * (currentScale - 1), 0);
        }
    }

    void OnPinchUpdated(object sender, PinchGestureUpdatedEventArgs e)
    {

        if (e.Status == GestureStatus.Started)
        {
            // Zapisujemy biezacy wspolczynnik skalowania zerujemy sk³adowe dla punktu centralnego transformacji
            startScale = Content.Scale;
            Content.AnchorX = 0;
            Content.AnchorY = 0;
        }
        if (e.Status == GestureStatus.Running)
        {
            // Oblicz wspolczynnik skalowania
            currentScale += (e.Scale - 1) * startScale;
            currentScale = Math.Max(1, currentScale);

            // Wspolrzedna X
            double renderedX = Content.X + xOffset;
            double deltaX = renderedX / Width;
            double deltaWidth = Width / (Content.Width * startScale);
            double originX = (e.ScaleOrigin.X - deltaX) * deltaWidth;

            // Wspolrzedna Y.
            double renderedY = Content.Y + yOffset;
            double deltaY = renderedY / Height;
            double deltaHeight = Height / (Content.Height * startScale);
            double originY = (e.ScaleOrigin.Y - deltaY) * deltaHeight;

            // Oblicz przekszta³cone wspolrzedne elementu
            double targetX = xOffset - (originX * Content.Width) * (currentScale - startScale);
            double targetY = yOffset - (originY * Content.Height) * (currentScale - startScale);

            // Zastosuj translacje na podstawie zmiany pochodzenia
            Content.TranslationX = Math.Clamp(targetX, -Content.Width * (currentScale - 1), 0);
            Content.TranslationY = Math.Clamp(targetY, -Content.Height * (currentScale - 1), 0);

            // Zastosuj wspolczynnik skalowania
            Content.Scale = currentScale;
        }
        if (e.Status == GestureStatus.Completed)
        {
            // Zapisz delte translacji elementu
            xOffset = Content.TranslationX;
            yOffset = Content.TranslationY;
        }
    }

    protected override void OnAppearing()
    {
        if(App.shouldBeVisible)
        {
            object sender = this;
            EventArgs e = EventArgs.Empty;
            OnShowMenuButtonClicked(sender, e);
            App.shouldBeVisible = false;
        }
        base.OnAppearing();
    }
}