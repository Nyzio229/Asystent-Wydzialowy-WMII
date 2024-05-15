using banditoth.MAUI.DeviceId;
using WMiIApp.Services;

namespace WMiIApp;

public partial class CodeAuthPage : ContentPage
{
	public CodeAuthPage()
	{
		InitializeComponent();
	}
    private async void Button_Clicked(object sender, EventArgs e)
    {
        try
        {
            int code = Int32.Parse(entry.Text);
            string? deviceId = await SecureStorage.GetAsync("deviceId");
            await AuthService.VerifyDevice(code, deviceId);

            await Shell.Current.GoToAsync("///MainPage");
        }
        catch(Exception ex)
        {
            await Shell.Current.DisplayAlert("Error!", ex.Message, "OK");
        }
        
    }
}