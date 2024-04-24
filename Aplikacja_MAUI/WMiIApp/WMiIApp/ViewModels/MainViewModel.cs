using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using WMiIApp.Services;
using WMiIApp.Models;
using CommunityToolkit.Maui.Core;
using CommunityToolkit.Maui.Alerts;
using static Android.Graphics.ImageDecoder;

namespace WMiIApp.ViewModels
{
    public partial class MainViewModel : ObservableObject
    {
        CancellationTokenSource? textToSpeechCancellationTokenSource;
        readonly MessageService messageService;

        [ObservableProperty]
        ObservableCollection<Message>? items;

        [ObservableProperty]
        ObservableCollection<Message>? itemsEN;

        [ObservableProperty]
        public string? text;

        public MainViewModel(MessageService messageService) 
        {
            Items = [];
            ItemsEN = [];
            this.messageService = messageService;

            Message message = new()
            {
                Content = "Cześć! Jestem MikoAI i chętnie odpowiem na wszystkie twoje pytania...",
                Role = "system",
                IsSent = false
            };
            Items.Add(message);
            Message message2 = new()
            {
                Content = "Hi, I'm MikoAI and I'm happy to answer all your questions...",
                Role = "system",
                IsSent = false
            };
            ItemsEN.Add(message2);
        }

        static async Task PutTaskDelay()
        {
            await Task.Delay(2000);
        }

        //odpowiedzi na sztywno

        [RelayCommand]
        async Task Send()
        {
            if (string.IsNullOrEmpty(Text))
                return;

            Message message = new Message();
            message.Content = Text;
            message.Role = "user";
            message.IsSent = true;

            Items.Add(message);
            Text = string.Empty;
            await PutTaskDelay();
            //Text = "odpowiedź z serwera...";
            Text = "Wbrew powszechnemu przekonaniu, Lorem Ipsum nie jest po prostu przypadkowym tekstem. " +
                "Ma swoje korzenie w klasycznej literaturze łacińskiej z 45 r. p.n.e., co czyni go ponad 2000 lat starym.";

            Message messageReceived = new Message();
            messageReceived.Content = Text;
            messageReceived.Role = "system";
            messageReceived.IsSent = false;

            Items.Add(messageReceived);
            Text = string.Empty;
        }

        ////odpowiedzi z serwera
        //[RelayCommand]
        //async Task Send()
        //{
        //    if (string.IsNullOrEmpty(Text))
        //        return;
        //    Message message = new()
        //    {
        //        Content = Text,
        //        IsSent = true,
        //        Role = "user"
        //    };
        //    Items.Add(message);
        //    try
        //    {
        //        //translacja
        //        Message messageTranslated = new()
        //        {
        //            Role = "user",
        //            IsSent = true,
        //            Content = await messageService.TranslateMessage(Items, "pl", "en-GB")
        //        };
        //        ItemsEN.Add(messageTranslated);
        //    }
        //    catch (HttpRequestException e)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", e.Message + "TRANSLATION", "OK");
        //    }
        //    catch (Exception ex)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", ex.Message + "TRANSLATION", "OK");
        //    }
        //    finally
        //    {
        //        Text = string.Empty;
        //    }

        //    //kategoryzacja
        //    try
        //    {
        //        ClassifyResponse classifyResponse = new();
        //        classifyResponse = await messageService.GetCategory(ItemsEN);
        //        switch (classifyResponse.label)
        //        {
        //            case "-1":
        //                await Shell.Current.DisplayAlert("Error!", "-1 CATEGORY", "OK");
        //                break;
        //            case "navigation":
        //                await Shell.Current.GoToAsync("Mapa"); //tu pewnie będzie błąd
        //                return;
        //            case "chat":
        //                //ogólne
        //                break;
        //        }
        //    }
        //    catch (HttpRequestException e)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", e.Message + "CATEGORY", "OK");
        //    }
        //    catch (Exception ex)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", ex.Message + "CATEGORY", "OK");
        //    }
        //    finally
        //    {
        //        Text = string.Empty;
        //    }

        //    //FAQ
        //    try
        //    {
        //        List<TableContext> tableContexts = new List<TableContext>();
        //        tableContexts = await messageService.GetMessageFromFAQ(ItemsEN);
        //        if (tableContexts[0].id_pytania != -1)
        //        {
        //            Message messageFAQ = new()
        //            {
        //                Content = "Czy chodziło ci o..\n" + tableContexts[0].pytanie,
        //                IsSent = false,
        //                Role = "system"
        //            };
        //            Items.Add(messageFAQ);
        //            //ItemsEn też dodać?
        //            Message messageFAQ2 = new()
        //            {
        //                Content = "Odpowiedź: \n" + tableContexts[0].odpowiedz,
        //                IsSent = false,
        //                Role = "system"
        //            };
        //            Items.Add(messageFAQ2);
        //            //ItemsEn też dodać?
        //            return;
        //        }
        //    }
        //    catch (HttpRequestException e)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", e.Message + "FAQ", "OK");
        //    }
        //    catch (Exception ex)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", ex.Message + "FAQ", "OK");
        //    }
        //    finally
        //    {
        //        Text = string.Empty;
        //    }

        //    //LLM
        //    try
        //    {
        //        Message messageReceived = new()
        //        {
        //            Role = "system",
        //            IsSent = false,
        //            Content = await messageService.GetMessageFromMain(ItemsEN)
        //        };
        //        ItemsEN.Add(messageReceived);
        //    }
        //    catch (HttpRequestException e)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", e.Message + "LLM", "OK");
        //    }
        //    catch (Exception ex)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", ex.Message + "LLM", "OK");
        //    }
        //    finally
        //    {
        //        Text = string.Empty;
        //    }

        //    //translacja
        //    try
        //    {
        //        Message messageTranslatedFromEN = new()
        //        {
        //            Role = "user",
        //            IsSent = false,
        //            Content = await messageService.TranslateMessage(ItemsEN, "en", "pl")
        //        };
        //        Items.Add(messageTranslatedFromEN);
        //    }
        //    catch (HttpRequestException e)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", e.Message + "Translacja", "OK");
        //    }
        //    catch (Exception ex)
        //    {
        //        await Shell.Current.DisplayAlert("Error!", ex.Message + "Translacja", "OK");
        //    }
        //    finally
        //    {
        //        Text = string.Empty;
        //    }

        //}

        [RelayCommand]
        async Task Tapped(string content)
        {
            if(textToSpeechCancellationTokenSource != null)
            {
                textToSpeechCancellationTokenSource.Cancel();
                textToSpeechCancellationTokenSource.Dispose();
                textToSpeechCancellationTokenSource = null;
            }
            else
            {
                textToSpeechCancellationTokenSource = new CancellationTokenSource();
                Message message = new()
                {
                    Content = content,
                    IsSent = true,
                    Role = "user"
                };
                await TextToSpeechService.ReadTheMessageAloud(message, textToSpeechCancellationTokenSource.Token);
            }
        }

        [RelayCommand]
        async Task Speak()
        {
            CancellationTokenSource source = new();
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
    }
}
