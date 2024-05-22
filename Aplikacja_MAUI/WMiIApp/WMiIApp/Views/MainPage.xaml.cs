using CommunityToolkit.Maui.Core.Platform;
using System.Collections;
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
            entry.Unfocus();
        }

        protected async override void OnAppearing()
        {
            base.OnAppearing();
            await Task.Delay(100);
            loadingGif.IsAnimationPlaying = true;
        }

        private async void entry_Focused(object sender, FocusEventArgs e)
        {
            int counter = 0;
            while(true)
            {
                counter++;
                if(counter>=10)
                {
                    break;
                }
                bool isShowed = entry.IsSoftInputShowing();
                if(isShowed)
                {
                    collectionView.ScrollTo(1000, position: ScrollToPosition.End);
                    break;
                }
                else
                {
                    await Task.Delay(300);
                }

            }
        }
    }

}
