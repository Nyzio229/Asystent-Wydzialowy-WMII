using Newtonsoft.Json;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json.Serialization;
using WMiIApp.Models;

namespace WMiIApp.Services
{
    public class MessageService
    {
        //const string uri = "https://5cbb-2a01-117f-440f-b00-a403-5fc6-f6d1-cb76.ngrok-free.app/LLMResponseAdvanced"; //glowny
        const string uri = "https://5cbb-2a01-117f-440f-b00-a403-5fc6-f6d1-cb76.ngrok-free.app/LLMResponse"; //do testowania
        readonly HttpClient httpClient;
        public MessageService()
        {
            this.httpClient = new HttpClient();
        }

        public async Task<string> GetMessage(string text)
        {
            var messages = new
            {
                content = text,
                role = "user"
            };
            var payload = new
            {
                messages
            };
            var jsonPayload = JsonConvert.SerializeObject(payload);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uri, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            return responseContent;
        }
    }
}
