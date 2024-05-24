using Newtonsoft.Json;
using System.Collections.ObjectModel;
using System.Text;
using WMiIApp.Models;

namespace WMiIApp.Services
{
    public class MessageService
    {
        //const string uri = "https://174b-188-146-254-12.ngrok-free.app/";
        const string uriMain = App.uri + "LLMResponseAdvanced";
        const string uriFAQ = App.uri + "FAQLike";
        const string uriTranslate = App.uri + "Translation";
        const string uriClassify = App.uri + "Classify";
        readonly HttpClient httpClient;

        public MessageService()
        {
            this.httpClient = new HttpClient();
            Task task = Task.Run(async () =>
            {
                await InitializeHttpClient();
            });
            task.Wait();
        }

        async Task InitializeHttpClient()
        {
            string? deviceId = await SecureStorage.GetAsync("deviceId");
            string? apikey = await SecureStorage.GetAsync("apikey");
            httpClient.DefaultRequestHeaders.Add("device_id", deviceId);
            httpClient.DefaultRequestHeaders.Add("api_key", apikey);
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
                limit = 1,
                lang = "en"
            };
            var jsonPayload = JsonConvert.SerializeObject(message);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uriFAQ, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            //poprawić czytanie odpowiedzi
            var finalResponse = JsonConvert.DeserializeObject<FAQFinalResponse>(responseContent);
            return finalResponse.faq;
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
