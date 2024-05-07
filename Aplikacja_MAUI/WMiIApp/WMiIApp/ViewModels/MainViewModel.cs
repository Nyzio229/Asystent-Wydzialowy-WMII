using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using WMiIApp.Services;
using WMiIApp.Models;
using CommunityToolkit.Maui.Core;
using CommunityToolkit.Maui.Alerts;
using WMiIApp;
using CommunityToolkit.Maui.Core.Platform;
using Newtonsoft.Json;

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

        [ObservableProperty]
        public bool isEnabled = false;

        [ObservableProperty]
        public bool canBeSent = true;

        public MainViewModel(MessageService messageService) 
        {
            Items = [];
            ItemsEN = [];
            this.messageService = messageService;

            Message message = new()
            {
                Content = "Cześć! Jestem MikoAI i chętnie odpowiem na wszystkie twoje pytania...",
                Role = "assistant",
                IsSent = false
            };
            Items.Add(message);
            Message message2 = new()
            {
                Content = "Hi, I'm MikoAI and I'm happy to answer all your questions...",
                Role = "assistant",
                IsSent = false
            };
            ItemsEN.Add(message2);
        }

        static async Task PutTaskDelay()
        {
            await Task.Delay(2000);
        }

        ////odpowiedzi na sztywno
        //[RelayCommand]
        //async Task Send()
        //{
        //    if (string.IsNullOrEmpty(Text))
        //        return;

        //    Message message = new Message();
        //    message.Content = Text;
        //    message.Role = "user";
        //    message.IsSent = true;

        //    Items.Add(message);
        //    Text = string.Empty;
        //    await PutTaskDelay();
        //    //Text = "odpowiedź z serwera...";
        //    Text = "Wbrew powszechnemu przekonaniu, Lorem Ipsum nie jest po prostu przypadkowym tekstem. " +
        //        "Ma swoje korzenie w klasycznej literaturze łacińskiej z 45 r. p.n.e., co czyni go ponad 2000 lat starym.";


        //    Message messageReceived = new Message();
        //    messageReceived.Content = Text;
        //    messageReceived.Role = "assistant";
        //    messageReceived.IsSent = false;

        //    messageReceived.IsFAQ = true;
        //    IsEnabled = true;
        //    AcceptFAQCommand.NotifyCanExecuteChanged();
        //    RejectFAQCommand.NotifyCanExecuteChanged();

        //    Items.Add(messageReceived);
        //    Text = string.Empty;
        //}

        [RelayCommand(CanExecute = nameof(CanManageFAQ))]
        void AcceptFAQ(Message msg)
        {
            msg.IsFAQ = false;
            IsEnabled = false;
            CanBeSent = true;
            AcceptFAQCommand.NotifyCanExecuteChanged();
            RejectFAQCommand.NotifyCanExecuteChanged();
            SendCommand.NotifyCanExecuteChanged();
        }
        [RelayCommand(CanExecute = nameof(CanManageFAQ))]
        void RejectFAQ(Message msg)
        {
            for (int i = Items.Count - 1; i >= 0; i--)
            {
                if (Items[i] == msg)
                {
                    Items.RemoveAt(i);
                    Items.RemoveAt(i-1);
                    break;
                }
            }
            IsEnabled = false;
            CanBeSent = true;
            AcceptFAQCommand.NotifyCanExecuteChanged();
            RejectFAQCommand.NotifyCanExecuteChanged();
            SendCommand.NotifyCanExecuteChanged();
            //dodać żeby szło dalej do llma
        }
        private bool CanManageFAQ()
        {
            return IsEnabled;
        }
        private bool CanSend()
        {
            return CanBeSent;
        }

        //odpowiedzi z serwera
        [RelayCommand(CanExecute = nameof(CanSend))]
        async Task Send()
        {
            if (string.IsNullOrEmpty(Text))
                return;
            Message message = new()
            {
                Content = Text,
                IsSent = true,
                Role = "user"
            };
            Items.Add(message);

            //translacja
            try
            {
                Message messageTranslated = new()
                {
                    Role = "user",
                    IsSent = true,
                    Content = await messageService.TranslateMessage(Items, "pl", "en-GB")
                };
                ItemsEN.Add(messageTranslated);
            }
            catch (HttpRequestException e)
            {
                await Shell.Current.DisplayAlert("Error!", e.Message + " TRANSLATION", "OK");
                return;
            }
            catch (Exception ex)
            {
                await Shell.Current.DisplayAlert("Error!", ex.Message + " TRANSLATION", "OK");
                return;
            }
            finally
            {
                Text = string.Empty;
            }

            //kategoryzacja
            try
            {
                ClassifyResponse classifyResponse = new();
                classifyResponse = await messageService.GetCategory(ItemsEN);
                switch (classifyResponse.label)
                {
                    case "-1":
                        await Shell.Current.DisplayAlert("Error!", "-1 CATEGORY", "OK");
                        break;
                    case "navigation":
                        await Shell.Current.GoToAsync("///MapPage_1");
                        await Shell.Current.DisplayAlert("Hurra!", "From: " + classifyResponse.metadata.source + " " + "To: " + classifyResponse.metadata.destination, "OK");
                        return;
                    case "chat":
                        //ogólne
                        break;
                    default:
                        await Shell.Current.DisplayAlert("Error!", "Coś poszło nie tak... (kategoryzacja)", "OK");
                        return;
                }
            }
            catch (HttpRequestException e)
            {
                await Shell.Current.DisplayAlert("Error!", e.Message + "CATEGORY", "OK");
            }
            catch (Exception ex)
            {
                await Shell.Current.DisplayAlert("Error!", ex.Message + "CATEGORY", "OK");
            }
            finally
            {
                Text = string.Empty;
            }

            ////FAQ
            //try
            //{
            //    List<TableContext> tableContexts = new List<TableContext>();
            //    tableContexts = await messageService.GetMessageFromFAQ(ItemsEN);
            //    if (tableContexts[0].id_pytania != -1)
            //    {
            //        Message messageFAQ = new()
            //        {
            //            Content = "Did you mean...\n" + tableContexts[0].pytanie,
            //            IsSent = false,
            //            Role = "assistant"
            //        };
            //        ItemsEN.Add(messageFAQ);
            //        try
            //        {
            //            Message faqTranslatedFromEN = new()
            //            {
            //                Role = "user",
            //                IsSent = false,
            //                Content = await messageService.TranslateMessage(ItemsEN, "en", "pl")
            //            };
            //            Items.Add(faqTranslatedFromEN);
            //        }
            //        catch (HttpRequestException e)
            //        {
            //            await Shell.Current.DisplayAlert("Error!", e.Message + " Translacja", "OK");
            //        }
            //        catch (Exception ex)
            //        {
            //            await Shell.Current.DisplayAlert("Error!", ex.Message + " Translacja", "OK");
            //        }
            //        Message messageFAQ2 = new()
            //        {
            //            Content = "Answer: \n" + tableContexts[0].odpowiedz,
            //            IsSent = false,
            //            Role = "assistant"
            //        };
            //        ItemsEN.Add(messageFAQ2);
            //        try
            //        {
            //            Message faq2TranslatedFromEN = new()
            //            {
            //                Role = "user",
            //                IsSent = false,
            //                Content = await messageService.TranslateMessage(ItemsEN, "en", "pl"),
            //                IsFAQ = true
            //            };
            //            Items.Add(faq2TranslatedFromEN);
            //        }
            //        catch (HttpRequestException e)
            //        {
            //            await Shell.Current.DisplayAlert("Error!", e.Message + " Translacja", "OK");
            //        }
            //        catch (Exception ex)
            //        {
            //            await Shell.Current.DisplayAlert("Error!", ex.Message + " Translacja", "OK");
            //        }
            //        IsEnabled = true;
            //        AcceptFAQCommand.NotifyCanExecuteChanged();
            //        RejectFAQCommand.NotifyCanExecuteChanged();
            //        CanBeSent = false;
            //        SendCommand.NotifyCanExecuteChanged();
            //        return;
            //    }
            //}
            //catch (HttpRequestException e)
            //{
            //    await Shell.Current.DisplayAlert("Error!", e.Message + " FAQ", "OK");
            //}
            //catch (Exception ex)
            //{
            //    await Shell.Current.DisplayAlert("Error!", ex.Message + " FAQ", "OK");
            //}
            //finally
            //{
            //    Text = string.Empty;
            //}

            //LLM
            try
            {
                Message messageReceived = new()
                {
                    Role = "assistant",
                    IsSent = false,
                    Content = await messageService.GetMessageFromMain(ItemsEN)
                };
                ItemsEN.Add(messageReceived);
            }
            catch (HttpRequestException e)
            {
                await Shell.Current.DisplayAlert("Error!", e.Message + "LLM", "OK");
                return;
            }
            catch (Exception ex)
            {
                await Shell.Current.DisplayAlert("Error!", ex.Message + "LLM", "OK");
                return;
            }
            finally
            {
                Text = string.Empty;
            }

            //translacja
            try
            {
                Message messageTranslatedFromEN = new()
                {
                    Role = "user",
                    IsSent = false,
                    Content = await messageService.TranslateMessage(ItemsEN, "en", "pl")
                };
                Items.Add(messageTranslatedFromEN);
            }
            catch (HttpRequestException e)
            {
                await Shell.Current.DisplayAlert("Error!", e.Message + "Translacja", "OK");
            }
            catch (Exception ex)
            {
                await Shell.Current.DisplayAlert("Error!", ex.Message + "Translacja", "OK");
            }
            finally
            {
                Text = string.Empty;
            }

        }

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
