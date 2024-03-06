using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Any;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json;
using ServerApiMikoAI.Models;
using Swashbuckle.AspNetCore.Annotations;
using Swashbuckle.AspNetCore.SwaggerGen;
using System.ComponentModel.DataAnnotations;
using System.Net;
using System.Text;
using System.Text.Json;

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
    public class LLMResponseController : ControllerBase
    {
        private readonly PostrgeSQLContext _context;
        public LLMResponseController(PostrgeSQLContext context)
        {
            _context = context;
        }

        [HttpPost(Name = "LLMRequest")]
        [ProducesResponseType(typeof(LLMRequest), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<string> Post(LLMRequest request)
        {
            return await LLMApi(request,_context);
        }

        public static async Task<string> LLMApi([FromBody][Required] LLMRequest request,PostrgeSQLContext context)
        {
            string apiUrl = "http://158.75.112.151:9123/v1/chat/completions";

            var messages = new[]
            {
                new
                {
                    content = "Your name is MikołAI and you are a helpful, respectful, friendly and honest personal for students at Nicolaus Copernicus University (faculty of Mathematics and Computer Science) in Toruń, Poland. Your main task is responding to students' questions regarding their studies, but you can also engage in a friendly informal chat. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. Please ensure that your responses are socially unbiased and positive in nature. If you don't know the answer to a question, please don't share false information.",
                    role = "system"
                },
                new
                {
                    content = request.messages.Content,
                    role = "user"
                }
            };

            var payload = new
            {
                messages
            };

            var jsonPayload = JsonConvert.SerializeObject(payload);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            float[] embedding = await EmbedingController.Embedding(request.messages.Content);
            int resultId = await QdrantController.QdrantClientId(embedding);

            if(resultId != -1)
            {
                PostgreConnectionController postgreConnectionController = new PostgreConnectionController(context);
                TableContext tableContext =  await postgreConnectionController.GetQueryById(resultId);

                return tableContext.odpowiedz;
            }

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
                            Console.WriteLine(chatResponseMessage);
                            return chatResponseMessage;
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
