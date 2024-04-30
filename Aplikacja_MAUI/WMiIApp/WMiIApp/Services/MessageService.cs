using Newtonsoft.Json;
using System.Collections.ObjectModel;
using System.Text;
using WMiIApp.Models;

namespace WMiIApp.Services
{
    public class MessageService
    {
        const string uri = "https://13ad-188-146-252-197.ngrok-free.app/";
        const string uriMain = uri + "LLMResponseAdvanced";
        const string uriFAQ = uri + "FAQ";
        const string uriTranslate = uri + "Translation";
        const string uriClassify = uri + "Classify";
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
