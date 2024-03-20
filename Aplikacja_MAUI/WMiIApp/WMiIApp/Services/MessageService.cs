using Newtonsoft.Json;
using System.Collections.ObjectModel;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json.Serialization;
using WMiIApp.Models;

namespace WMiIApp.Services
{
    public class MessageService
    {
        const string uriMain = "https://6d3a-188-146-253-43.ngrok-free.app/LLMResponseAdvanced"; //glowny
        //const string uriMain = "https://5cbb-2a01-117f-440f-b00-a403-5fc6-f6d1-cb76.ngrok-free.app/LLMResponse"; //do testowania
        const string uriFAQ = "https://6d3a-188-146-253-43.ngrok-free.app/FAQ";
        readonly HttpClient httpClient;
        public MessageService()
        {
            this.httpClient = new HttpClient();
        }

        public async Task<string> GetMessageFromMain(ObservableCollection<Message> messages)
        {
            var jsonPayload = JsonConvert.SerializeObject(messages);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uriMain, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            return responseContent;
        }

        public async Task<string> GetMessageFromFAQ(ObservableCollection<Message> messages)
        {
            var message = new
            {
                message = messages.Last().Content
            };
            var jsonPayload = JsonConvert.SerializeObject(message);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uriFAQ, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            //poprawić czytanie odpowiedzi
            return responseContent;
        }
    }
}
