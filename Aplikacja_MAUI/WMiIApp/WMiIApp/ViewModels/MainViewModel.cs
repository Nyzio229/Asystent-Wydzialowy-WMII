using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WMiIApp.Services;
using WMiIApp.Models;

namespace WMiIApp.ViewModels
{
    public partial class MainViewModel : ObservableObject
    {
        MessageService messageService;
        public MainViewModel(MessageService messageService) 
        {
            Items = new ObservableCollection<Message>();
            this.messageService = messageService;
        }

        [ObservableProperty]
        ObservableCollection<Message> items;

        [ObservableProperty]
        string text;

        async Task PutTaskDelay()
        {
            await Task.Delay(2000);
        }
        

        [RelayCommand]
        async Task Add()
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
            Text = "Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of \"de Finibus Bonorum et Malorum\" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, \"Lorem ipsum dolor sit amet..\", comes from a line in section 1.10.32.";

            Message messageReceived = new Message();
            messageReceived.Content = Text;
            messageReceived.Role = "user";
            messageReceived.IsSent = false;

            Items.Add(messageReceived);
            Text = string.Empty;
        }
        
        
       /*
       [RelayCommand]
        async Task Add()
        {
            if (string.IsNullOrEmpty(Text))
                return;
            Items.Add(Text);
            try
            {
                Text = await messageService.GetMessage(Text);
                Items.Add(Text);
            }
            catch (Exception ex)
            {
                await Shell.Current.DisplayAlert("Error!", ex.Message, "OK");
            }
            finally 
            {
                Text = string.Empty;
            }
        }*/
        
    }
}
