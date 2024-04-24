using DeepL;
using Microsoft.AspNetCore.Mvc;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json;
using ServerApiMikoAI.Models.Context;
using ServerApiMikoAI.Models.LLM;
using Swashbuckle.AspNetCore.Annotations;
using Swashbuckle.AspNetCore.SwaggerGen;
using System.ComponentModel.DataAnnotations;
using System.Text;

namespace ServerApiMikoAI.Controllers
{
    public class RequireRequestBodyFilter : IOperationFilter
    {
        public void Apply(OpenApiOperation operation, OperationFilterContext context)
        {
            var isPostOrPutRequest = context.ApiDescription.HttpMethod.Equals("POST", StringComparison.OrdinalIgnoreCase)
                || context.ApiDescription.HttpMethod.Equals("PUT", StringComparison.OrdinalIgnoreCase);

            if (isPostOrPutRequest && operation.RequestBody != null)
            {
                operation.RequestBody.Required = true;
            }
        }
    }

    [ApiController]
    [Route("[controller]")]
    public class LLMResponseAdvancedController : ControllerBase
    {
        //private static Translator translator = new Translator("b7b072d0-f9c7-4820-8003-dcd228a1df91:fx");

        private readonly PostrgeSQLContext _context;
        public LLMResponseAdvancedController(PostrgeSQLContext context)
        {
            _context = context;
        }
        
        [HttpPost(Name = "LLMRequest - New")]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<string> Post(Message[] requestAdvanced)
        {
            return await LLMApiNew(requestAdvanced, _context);
        }

        public static async Task<string> LLMApiNew([Required] Message[] requestAdvanced, PostrgeSQLContext context)
        {
            string apiUrl = "http://158.75.112.151:9123/chat";

            const string initialMessage = "Your name is MikołAI and you are a helpful, respectful, friendly and honest personal for students at Nicolaus Copernicus University (faculty of Mathematics and Computer Science) in Toruń, Poland. Your main task is responding to students' questions regarding their studies, but you can also engage in a friendly informal chat. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. Please ensure that your responses are socially unbiased and positive in nature. If you don't know the answer to a question, please don't share false information.";


            var messages = new[]
            {
                new
                {
                    content = initialMessage,
                    role = "system"
                }
            };

            foreach (Message previousMessage in requestAdvanced)
            {
                var newItem = new
                {
                    content = previousMessage.Content,
                    role = previousMessage.Role,
                };
                messages = messages.Concat(new[] { newItem }).ToArray();
            }

            /*var translatedQuestion = await translator.TranslateTextAsync(
              messages.Last().content,
              LanguageCode.Polish,
              LanguageCode.EnglishBritish);

            Console.WriteLine($"Tłumaczenie pytania: '{messages.Last().content}' -> '{translatedQuestion}'");

            
            var messagesList = messages.ToList();
            messagesList.RemoveAt(messagesList.Count - 1);
            messages = messagesList.ToArray();

            var newCurrentUserQuestion = new
            {
                content = translatedQuestion.Text,
                role = "user"
            };
            messages = messages.Concat(new[] { newCurrentUserQuestion }).ToArray();*/





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
                        LLMResponseAdvanced chatResponse = JsonConvert.DeserializeObject<LLMResponseAdvanced>(responseContent);

                        Console.WriteLine("Odpowiedź z API:");
                        Console.WriteLine(responseContent);
                        if (chatResponse.text != null && chatResponse.text.Length > 0)
                        {
                            string chatResponseMessage = chatResponse.text;

                            /*TranslationMessage translationMessage = new TranslationMessage(chatResponseMessage, LanguageCode.English, "pl");
                            var translatedResponse = await TranslationController.DeepLApi(translationMessage);
                            var translatedResponse = await translator.TranslateTextAsync(
                              chatResponseMessage,
                              LanguageCode.EnglishBritish,
                              LanguageCode.Polish);
                            */
                            //Console.WriteLine($"Tłumaczenie odpowiedzi: '{chatResponseMessage}' -> '{translatedResponse}'");
               
                            //return translatedResponse;
                            return chatResponseMessage;
                            //return "To jest wiadnomość że poszło coś nie tak i serwer nie działa";
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
