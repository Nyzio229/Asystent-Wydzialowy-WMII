using CommunityToolkit.Maui.Alerts;
using CommunityToolkit.Maui.Media;
using System.Globalization;
using WMiIApp.ViewModels;


//polski nie jest wspierany na windows

//wywołanie:
/*
        [RelayCommand]
        async Task Speak()
        {
            CancellationToken token = source.Token;
            try
            {
                await SpeechToTextService.StartListening(token, this);
            }
            catch (Exception ex) 
            {
                await Shell.Current.DisplayAlert("Error!", ex.Message, "OK");
            }
        }
 */

//można dodać obsługę zatrzymania (na android niepotrzebna)

namespace WMiIApp.Services
{
    public static class SpeechToTextService
    {
        public static async Task StartListening(CancellationToken cancellationToken, MainViewModel mvm)
        {
            var isGranted = await SpeechToText.RequestPermissions(cancellationToken);
            if (!isGranted)
            {
                await Toast.Make("Brak uprawnień!").Show(CancellationToken.None);
                return;
            }

            SpeechToText.Default.RecognitionResultUpdated += (sender, args) => OnRecognitionTextUpdated(sender, args, mvm);
            SpeechToText.Default.RecognitionResultCompleted += (sender, args) => OnRecognitionTextCompleted(sender, args, mvm);
            await SpeechToText.StartListenAsync(CultureInfo.GetCultureInfo("pl"), CancellationToken.None);
        }

        public static async Task StopListening(CancellationToken cancellationToken, MainViewModel mvm)
        {
            await SpeechToText.StopListenAsync(CancellationToken.None);
            SpeechToText.Default.RecognitionResultUpdated -= (sender, args) => OnRecognitionTextUpdated(sender, args, mvm);
            SpeechToText.Default.RecognitionResultCompleted -= (sender, args) => OnRecognitionTextCompleted(sender, args, mvm);
        }

        static void OnRecognitionTextUpdated(object? sender, SpeechToTextRecognitionResultUpdatedEventArgs args, MainViewModel mvm)
        {
            mvm.Text = args.RecognitionResult;
        }

        static void OnRecognitionTextCompleted(object? sender, SpeechToTextRecognitionResultCompletedEventArgs args, MainViewModel mvm)
        {
            mvm.Text = args.RecognitionResult;
        }
    }
}
