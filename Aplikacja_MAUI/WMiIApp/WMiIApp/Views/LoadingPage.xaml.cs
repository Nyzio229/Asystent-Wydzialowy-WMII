namespace WMiIApp;

public partial class LoadingPage : ContentPage
{
	public LoadingPage()
	{
		InitializeComponent();
	}

    protected override async void OnNavigatedTo(NavigatedToEventArgs args)
    {
        await Task.Delay(100);
        loadingGif.IsAnimationPlaying = true;
        if (await IsAuthenticated())
        {
            await Shell.Current.GoToAsync("///MainPage");
        }
        else
        {
            await Shell.Current.GoToAsync("///EmailAuthPage");
        }
        base.OnNavigatedTo(args);
    }

    async static Task<bool> IsAuthenticated()
    {
        await Task.Delay(2000);
        var hasAuth = await SecureStorage.GetAsync("apikey");
        return !(hasAuth == null);
    }
}