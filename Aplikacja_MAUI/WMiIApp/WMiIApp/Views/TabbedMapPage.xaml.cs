namespace WMiIApp;

public partial class TabbedMapPage : TabbedPage
{
    public TabbedMapPage()
    {
        InitializeComponent();

        // Ustawiamy karte startowa
        CurrentPage = Children[1];

    }

    // Funkcja po kliknieciu na pomieszczenie
    private void HandleRoomButtonClick(object sender, EventArgs e)
    {
        var button = (Button)sender;
        DisplayAlert("Pomieszczenie", "Klikniêto " + button.Text, "OK");
    }

}