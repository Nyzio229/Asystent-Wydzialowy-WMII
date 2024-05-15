using CommunityToolkit.Maui.Core.Platform;
using WMiIApp.ViewModels;


namespace WMiIApp
{
    public partial class MainPage : ContentPage
    {

        public MainPage(MainViewModel vm)
        {
            InitializeComponent();
            BindingContext = vm;
        }

        private async void ImageButton_Clicked(object sender, EventArgs e)
        {
            await entry.HideKeyboardAsync();
        }

        protected async override void OnAppearing()
        {
            base.OnAppearing();
            await Task.Delay(100);
            loadingGif.IsAnimationPlaying = true;
        }
    }

}
