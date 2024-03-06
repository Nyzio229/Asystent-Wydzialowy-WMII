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
            Text = "odpowiedź z serwera...";

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
