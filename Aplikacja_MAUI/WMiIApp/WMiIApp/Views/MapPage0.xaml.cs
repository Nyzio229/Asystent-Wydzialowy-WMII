namespace WMiIApp;

public partial class MapPage0 : ContentPage
{
	public MapPage0()
	{
		InitializeComponent();
	}
    private void HandleRoomButtonClick(object sender, EventArgs e)
    {
        var button = (Button)sender;
        DisplayAlert("Pomieszczenie", "Klikni�to " + button.Text, "OK");
    }
}