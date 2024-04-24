using WMiIApp.Models;

//PRZYKŁADOWE WYWOŁANIE:
//await TextToSpeechService.ReadTheMessageAloud(message, textToSpeechCancellationTokenSource.Token);

//dodać możliwość przerwania
//poprawić wybór głosu na męski
namespace WMiIApp.Services
{
    public static class TextToSpeechService
    {
        public static async Task ReadTheMessageAloud(Message msg, CancellationToken cancelToken)
        {
            if(msg.Content != null)
            {
                SpeechOptions options = await GetOptions();
                Speak(msg.Content, options, cancelToken);
            }
        }

        private static async void Speak(string toRead, SpeechOptions options, CancellationToken cancelToken) =>
            await TextToSpeech.Default.SpeakAsync(toRead, options, cancelToken);

        private static async Task<SpeechOptions> GetOptions()
        {
            IEnumerable<Locale> locales = await TextToSpeech.Default.GetLocalesAsync();
            SpeechOptions options = new SpeechOptions()
            {
                Pitch = 0.0f,   // 0.0 - 2.0
                Volume = 0.75f, // 0.0 - 1.0
                //Locale = locales.FirstOrDefault()
            };
            foreach (var item in locales)
            {
                if (item.Language == "pl-PL")
                {
                    options.Locale = item;
                    break;
                }
                else if (item.Language == "pl")
                {
                    options.Locale = item;
                    break;
                }
            }
            return options;
        }
    }
}
