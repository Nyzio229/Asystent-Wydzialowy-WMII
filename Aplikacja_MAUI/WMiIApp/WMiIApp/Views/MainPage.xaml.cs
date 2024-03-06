using Microsoft.Maui.Controls.Internals;
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
    }

}
