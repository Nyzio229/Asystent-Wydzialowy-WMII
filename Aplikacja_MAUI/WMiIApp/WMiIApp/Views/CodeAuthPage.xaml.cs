using banditoth.MAUI.DeviceId;
using CommunityToolkit.Maui.Core.Platform;
using WMiIApp.Services;

namespace WMiIApp;

public partial class CodeAuthPage : ContentPage
{
	public CodeAuthPage()
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
        if (isRed)
        {
            entry.TextColor = Colors.White;
        }
        try
        {
            nextStepButton.IsVisible = false;
            loadingGif.IsVisible = true;
            int code = Int32.Parse(entry.Text);
            string? deviceId = await SecureStorage.GetAsync("deviceId");
            await AuthService.VerifyDevice(code, deviceId);

            await Shell.Current.GoToAsync("///MainPage");
        }
        catch(Exception)
        {
            loadingGif.IsVisible = false;
            nextStepButton.IsVisible = true;
            await Shell.Current.DisplayAlert("B³¹d!", "Coœ posz³o nie tak...", "OK");
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