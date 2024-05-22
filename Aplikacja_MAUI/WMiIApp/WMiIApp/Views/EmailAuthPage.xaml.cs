namespace WMiIApp;
using banditoth.MAUI.DeviceId;
using CommunityToolkit.Maui.Core.Platform;
using WMiIApp.Services;

public partial class EmailAuthPage : ContentPage
{
	public EmailAuthPage()
	{
		InitializeComponent();
    }
    private bool isRed = false;

    private async void Button_Clicked(object sender, EventArgs e)
    {
        await entry.HideKeyboardAsync();
        entry.Unfocus();
        if (string.IsNullOrEmpty(entry.Text))
        {
            return;
        }
        if(isRed)
        {
            entry.TextColor = Colors.White;
        }
        if (entry.Text.Contains("@mat.umk.pl"))
        {
            try
            {
                nextStepButton.IsVisible = false;
                loadingGif.IsVisible = true;
                DeviceIdProvider deviceIdProvider = new();
                string email = entry.Text;
                string deviceId = deviceIdProvider.GetInstallationId();
                await SecureStorage.SetAsync("deviceId", deviceId);
                await AuthService.VerifyEmail(email, deviceId);
                await Shell.Current.GoToAsync("///CodeAuthPage");
            }
            catch (Exception)
            {
                loadingGif.IsVisible = false;
                nextStepButton.IsVisible = true;
                await Shell.Current.DisplayAlert("B³¹d!", "Coœ posz³o nie tak...", "OK");
            }
        }
        else
        {
            entry.TextColor = Colors.Red;
            isRed = true;
        }
    }
    protected async override void OnAppearing()
    {
        base.OnAppearing();
        await Task.Delay(100);
        loadingGif.IsAnimationPlaying = true;
    }

    private void entry_TextChanged(object sender, TextChangedEventArgs e)
    {
        entry.TextColor = Colors.White;
    }
}