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
        const string uriMain = "https://303a-188-146-252-197.ngrok-free.app/LLMResponseAdvanced"; //glowny
        //const string uriMain = "https://5cbb-2a01-117f-440f-b00-a403-5fc6-f6d1-cb76.ngrok-free.app/LLMResponse"; //do testowania
        const string uriFAQ = "https://303a-188-146-252-197.ngrok-free.app/FAQ";
        const string uriTranslate = "https://303a-188-146-252-197.ngrok-free.app/Translation";
        const string uriClassify = "https://303a-188-146-252-197.ngrok-free.app/Classify";
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

        public async Task<List<TableContext>> GetMessageFromFAQ(ObservableCollection<Message> messages)
        {
            var message = new
            {
                text = messages.Last().Content,
                limit = 1
            };
            var jsonPayload = JsonConvert.SerializeObject(message);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uriFAQ, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            //poprawić czytanie odpowiedzi
            var tableContext = JsonConvert.DeserializeObject<List<TableContext>>(responseContent);
            return tableContext;
        }

        public async Task<string> TranslateMessage(ObservableCollection<Message> messages, string from, string to)
        {
            var message = new
            {
                message = messages.Last().Content,
                translateFrom = from,
                translateTo = to
            };
            var jsonPayload = JsonConvert.SerializeObject(message);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uriTranslate, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            return responseContent;
        }

        public async Task<ClassifyResponse> GetCategory(ObservableCollection<Message> messages)
        {
            var message = new
            {
                text = messages.Last().Content
            };
            var jsonPayload = JsonConvert.SerializeObject(message);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uriClassify, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            var classifyResponse = JsonConvert.DeserializeObject<ClassifyResponse>(responseContent);
            return classifyResponse;
        }
    }
}
