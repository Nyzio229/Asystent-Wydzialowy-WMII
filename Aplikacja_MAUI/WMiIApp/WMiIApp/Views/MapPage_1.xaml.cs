namespace WMiIApp;

public partial class MapPage_1 : ContentPage
{
	public MapPage_1()
	{
		InitializeComponent();
	}

    private void HandleRoomButtonClick(object sender, EventArgs e)
    {
        var button = (Button)sender;
        DisplayAlert("Pomieszczenie", "Klikni�to " + button.Text, "OK");
    }
}