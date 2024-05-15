﻿using CommunityToolkit.Mvvm.ComponentModel;
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

        [ObservableProperty]
        public bool isAnimated = false;

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
            await Task.Delay(3000);
        }

        //odpowiedzi na sztywno
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

        //    IsAnimated = true;
        //    await PutTaskDelay();
        //    IsAnimated = false;

        //    Text = "Wbrew powszechnemu przekonaniu, Lorem Ipsum nie jest po prostu przypadkowym tekstem. " +
        //        "Ma swoje korzenie w klasycznej literaturze łacińskiej z 45 r. p.n.e., co czyni go ponad 2000 lat starym.";


        //    Message messageReceived = new Message();
        //    messageReceived.Content = Text;
        //    messageReceived.Role = "assistant";
        //    messageReceived.IsSent = false;

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

        async Task<bool> TranslateFromPLToEN()
        {
            try
            {
                Message messageTranslated = new()
                {
                    Role = "user",
                    IsSent = true,
                    Content = await messageService.TranslateMessage(Items, "pl", "en-GB")
                };
                ItemsEN.Add(messageTranslated);
                return true;
            }
            catch (HttpRequestException)
            {
                await Shell.Current.DisplayAlert("Błąd!", "Coś poszło nie tak z tłumaczeniem...", "OK");
                return false;
            }
            catch (Exception)
            {
                await Shell.Current.DisplayAlert("Błąd!", "Coś poszło nie tak...", "OK");
                return false;
            }
            finally
            {
                Text = string.Empty;
            }
        }

        async Task<bool> Categorize()
        {
            try
            {
                ClassifyResponse classifyResponse = new();
                classifyResponse = await messageService.GetCategory(ItemsEN);
                switch (classifyResponse.label)
                {
                    case "-1":
                        //await Shell.Current.DisplayAlert("Error!", "-1 CATEGORY", "OK");
                        return true;
                    case "navigation":
                        await Shell.Current.GoToAsync("///MapPage_1");
                        await Shell.Current.DisplayAlert("Hurra!", "From: " + classifyResponse.metadata.source + " " + "To: " + classifyResponse.metadata.destination, "OK");
                        return false;
                    case "chat":
                        //ogólne
                        return true;
                    default:
                        await Shell.Current.DisplayAlert("Błąd!", "Coś poszło nie tak... (kategoryzacja)", "OK");
                        return false;
                }
            }
            catch (HttpRequestException)
            {
                await Shell.Current.DisplayAlert("Błąd!", "Coś poszło nie tak...Sprawdź połączenie z internetem.", "OK");
                return false;
            }
            catch (Exception)
            {
                await Shell.Current.DisplayAlert("Błąd!", "Coś poszło nie tak...", "OK");
                return false;
            }
            finally
            {
                Text = string.Empty;
            }
        }

        async Task<bool> GetFaq()
        {
            try
            {
                List<TableContext> tableContexts = new List<TableContext>();
                tableContexts = await messageService.GetMessageFromFAQ(ItemsEN);
                if (tableContexts[0].AnswerPL != "-1")
                {
                    Message faqQuestionEN = new()
                    {
                        Content = "Did you mean...\n" + tableContexts[0].QuestionEN,
                        IsSent = false,
                        Role = "assistant"
                    };
                    ItemsEN.Add(faqQuestionEN);

                    Message faqAnswerEN = new()
                    {
                        Content = "Answer: \n" + tableContexts[0].AnswerEN,
                        IsSent = false,
                        Role = "assistant"
                    };
                    ItemsEN.Add(faqAnswerEN);

                    Message faqQuestionPL = new()
                    {
                        Content = "Czy chodziło ci o...\n" + tableContexts[0].QuestionPL,
                        IsSent = false,
                        Role = "assistant"
                    };
                    IsAnimated = false;
                    Items.Add(faqQuestionPL);

                    Message faqAnswerPL = new()
                    {
                        Content = "Odpowiedź: \n" + tableContexts[0].AnswerPL,
                        IsSent = false,
                        Role = "assistant",
                        IsFAQ = true
                    };
                    Items.Add(faqAnswerPL);

                    IsEnabled = true;
                    AcceptFAQCommand.NotifyCanExecuteChanged();
                    RejectFAQCommand.NotifyCanExecuteChanged();
                    CanBeSent = false;
                    SendCommand.NotifyCanExecuteChanged();
                    return false;
                }
                else
                {
                    return true;
                }
            }
            catch (HttpRequestException)
            {
                await Shell.Current.DisplayAlert("Błąd!", "Coś poszło nie tak...Sprawdź połączenie z internetem.", "OK");
                return false;
            }
            catch (Exception)
            {
                await Shell.Current.DisplayAlert("Błąd!", "Coś poszło nie tak...", "OK");
                return false;
            }
            finally
            {
                Text = string.Empty;
            }
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
            IsAnimated = true;

            //translacja
            if (await TranslateFromPLToEN() == false)
            {
                return;
            }

            //kategoryzacja
            if (await Categorize() == false)
            {
                IsAnimated = false;
                return;
            }

            //FAQ
            if (await GetFaq() == false)
            {
                return;
            }

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
                IsAnimated = false;
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
