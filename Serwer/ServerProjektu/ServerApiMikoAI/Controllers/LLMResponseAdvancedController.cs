using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using ServerApiMikoAI.Models;
using Swashbuckle.AspNetCore.Annotations;
using System.ComponentModel.DataAnnotations;
using System.Text;
using DeepL;

namespace ServerApiMikoAI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class LLMResponseAdvancedController : ControllerBase
    {
        private var translator = new Translator("f63c02c5-f056-...");

        private readonly PostrgeSQLContext _context;
        public LLMResponseAdvancedController(PostrgeSQLContext context)
        {
            _context = context;
        }
        
        [HttpPost(Name = "LLMRequest - New")]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<string> Post(LLMRequestAdvanced requestAdvanced)
        {
            return await LLMApiNew(requestAdvanced, _context);
        }

        public static async Task<string> LLMApiNew([Required] LLMRequestAdvanced requestAdvanced, PostrgeSQLContext context)
        {
            string apiUrl = "http://158.75.112.151:9123/v1/chat/completions";

            const string initialMessage = "Your name is MikołAI and you are a helpful, respectful, friendly and honest personal for students at Nicolaus Copernicus University (faculty of Mathematics and Computer Science) in Toruń, Poland. Your main task is responding to students' questions regarding their studies, but you can also engage in a friendly informal chat. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. Please ensure that your responses are socially unbiased and positive in nature. If you don't know the answer to a question, please don't share false information.";


            var messages = new[]
            {
                new
                {
                    content = initialMessage,
                    role = "system"
                }
            };

            if (requestAdvanced.previousQuestions.Length > 0)
            {
                foreach (PreviousQuestion previousInteraction in requestAdvanced.previousQuestions)
                {
                    var userItem = new
                    {
                        content = previousInteraction.previousQuestion,
                        role = "user"
                    };
                    var LLMItem = new
                    {
                        content = previousInteraction.previousAnswer,
                        role = "assistant"
                    };
                    messages = messages.Concat(new[] { userItem }).ToArray();
                    messages = messages.Concat(new[] { LLMItem }).ToArray();
                }
            }

            var currentUserQuestion = new
            {
                content = requestAdvanced.message,
                role = "user"
            };

            var translatedQuestion = await translator.TranslateTextAsync(
              currentUserQuestion,
              LanguageCode.Polish,
              LanguageCode.English);

            Console.WriteLine($"Tłumaczenie pytania: '{currentUserQuestion}' -> '{translatedQuestion}');

            messages = messages.Concat(new[] { translatedQuestion }).ToArray();

            var temperature = 0.7;

            var repeat_penalty = 1.176;

            var top_k = 40;

            var top_p = 0.1;

            var payload = new
            {
                messages,
                temperature,
                repeat_penalty,
                top_k,
                top_p
            };

            var jsonPayload = JsonConvert.SerializeObject(payload);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            using (var httpClient = new HttpClient())
            {
                try
                {
                    var response = await httpClient.PostAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();
                        LLMResponse chatResponse = JsonConvert.DeserializeObject<LLMResponse>(responseContent);

                        Console.WriteLine("Odpowiedź z API:");
                        Console.WriteLine(responseContent);
                        if (chatResponse.Choices != null && chatResponse.Choices.Count > 0)
                        {
                            string chatResponseMessage = chatResponse.Choices[0].Message.Content;
                            var translatedResponse = await translator.TranslateTextAsync(
                              chatResponseMessage,
                              LanguageCode.English,
                              LanguageCode.Polish);

                            Console.WriteLine($"Tłumaczenie odpowiedzi: '{chatResponseMessage}' -> '{translatedResponse}');
               
                            return translatedResponse;
                        }
                        return "Coś poszło nie tak";
                    }
                    else
                    {
                        Console.WriteLine($"Błąd: {response.StatusCode}");
                        return $"Błąd: {response.StatusCode}";
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Wystąpił błąd: {ex.Message}");
                    return $"Wystąpił błąd: {ex.Message}";
                }
            }
        }
    }
}
