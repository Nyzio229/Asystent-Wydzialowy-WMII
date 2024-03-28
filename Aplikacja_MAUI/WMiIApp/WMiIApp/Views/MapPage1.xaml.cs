namespace WMiIApp;

public partial class MapPage1 : ContentPage
{
	public MapPage1()
	{
		InitializeComponent();
	}

    private void HandleRoomButtonClick(object sender, EventArgs e)
    {
        var button = (Button)sender;
        DisplayAlert("Pomieszczenie", "Klikniêto " + button.Text, "OK");
    }
}