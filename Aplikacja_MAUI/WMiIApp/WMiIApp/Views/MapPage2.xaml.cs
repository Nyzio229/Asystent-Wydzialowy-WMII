namespace WMiIApp;

public partial class MapPage2 : ContentPage
{
	public MapPage2()
	{
		InitializeComponent();
	}

    private void HandleRoomButtonClick(object sender, EventArgs e)
    {
        var button = (Button)sender;
        DisplayAlert("Pomieszczenie", "Klikniêto " + button.Text, "OK");
    }
}