using DeepL;
using Microsoft.AspNetCore.Mvc;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json;
using ServerApiMikoAI.Models.Classify;
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

        private readonly AuthorizationService _authorizationService;

        public LLMResponseAdvancedController(AuthorizationService authorization)
        {
            _authorizationService = authorization;
        }

        [HttpPost(Name = "LLMRequest - New")]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<IActionResult> Post(Message[] requestAdvanced)
        {
            string deviceId = HttpContext.Request.Headers["device_id"];
            string apiKey = HttpContext.Request.Headers["api_key"];

            var isAuthorized = await _authorizationService.IsDeviceAuthorized(deviceId, apiKey);

            if (!isAuthorized)
            {
                return Unauthorized("Invalid DeviceId or ApiKey.");
            }

            string result = await LLMApiNew(requestAdvanced);

            switch (result)
            {
                case "-1":
                    return NotFound("Empty response");
                case "-2":
                    return StatusCode(400, "Response not Successful");
                case "-3":
                    return StatusCode(500, $"Internal server error");
                default:
                    return Ok(result);
            }
        }

        public static async Task<string> LLMApiNew([Required] Message[] requestAdvanced)
        {
            string apiUrl = "http://158.75.112.151:9123/chat";

            var messages = new List<Message>();

            foreach (Message simpleMassage in requestAdvanced)
            {
                Message newItem = new Message();
                newItem.content = simpleMassage.content;
                newItem.role = simpleMassage.role;
                messages.Add(newItem);
            }

            var payload = new
            {
                messages
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

                            return chatResponseMessage;
                        }
                        return "-1";
                    }
                    else
                    {
                        return "-2";
                    }
                }
                catch (Exception ex)
                {
                    return "-3";
                }
            }
        }
    }
}
