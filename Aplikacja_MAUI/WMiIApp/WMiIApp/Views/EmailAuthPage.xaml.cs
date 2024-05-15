namespace WMiIApp;
using banditoth.MAUI.DeviceId;
using WMiIApp.Services;

public partial class EmailAuthPage : ContentPage
{
	public EmailAuthPage()
	{
		InitializeComponent();
	}

    private async void Button_Clicked(object sender, EventArgs e)
    {
        try
        {
            DeviceIdProvider deviceIdProvider = new();
            string email = entry.Text;
            string deviceId = deviceIdProvider.GetInstallationId();
            await SecureStorage.SetAsync("deviceId", deviceId);
            await AuthService.VerifyEmail(email, deviceId);
            await Shell.Current.GoToAsync("///CodeAuthPage");
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error!", ex.Message, "OK");
        }
    }
}