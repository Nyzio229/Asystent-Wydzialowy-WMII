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

        private void ImageButton_Clicked(object sender, EventArgs e)
        {
            entry.HideKeyboardAsync();
        }
    }

}
