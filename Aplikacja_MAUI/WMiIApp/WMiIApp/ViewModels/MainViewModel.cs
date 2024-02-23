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
        Message message;
        public MainViewModel(MessageService messageService) 
        {
            Items = new ObservableCollection<string>();
            this.messageService = messageService;
        }

        [ObservableProperty]
        ObservableCollection<string> items;

        [ObservableProperty]
        string text;

        async Task PutTaskDelay()
        {
            await Task.Delay(2000);
        }
        /*
        [RelayCommand]
        async Task Add()
        {
            if (string.IsNullOrEmpty(Text))
                return; 
            Items.Add(Text);
            Text = string.Empty;
            await PutTaskDelay();
            //test
                Text = "odpowiedź z serwera...";
                Items.Add(Text);
                Text = string.Empty;
            //test
        }*/
        
        
       
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
        }
        
    }
}
