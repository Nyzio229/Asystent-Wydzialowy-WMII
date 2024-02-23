using Newtonsoft.Json;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json.Serialization;
using WMiIApp.Models;

namespace WMiIApp.Services
{
    public class MessageService
    {
        const string uri= "https://7018-188-146-248-221.ngrok-free.app/LLMResponse";
        HttpClient httpClient;
        public MessageService()
        {
            this.httpClient = new HttpClient();
        }

        Message message;
        public async Task<string> GetMessage(string text)
        {
            message = new Message();
            message.Content = text;
            message.Role = "user";
            /*var messages = new[]
            {
                new
                {
                    content = text,
                    role = "user"
                }
            };*/

            var messages = new
            {
                //content = "cos tam",
                content = message.Content,
                role = "user"
            };
            var payload = new
            {
                messages
            };
            var jsonPayload = JsonConvert.SerializeObject(payload);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uri, content);
            if (response.IsSuccessStatusCode)
            {
                //message = await response.Content.ReadFromJsonAsync(MessageContext.Default.Message);
                var responseContent = await response.Content.ReadAsStringAsync();
                return responseContent;
            }
            return "nie udalo sie";
        }
    }
}
