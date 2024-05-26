using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using ServerApiMikoAI.Models.Classify;
using ServerApiMikoAI.Models.Context;
using Swashbuckle.AspNetCore.Annotations;
using System.Text;

namespace ServerApiMikoAI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ClassifyController : ControllerBase
    {

        private readonly AuthorizationService _authorizationService;

        public ClassifyController(AuthorizationService authorization)
        {
            _authorizationService = authorization;
        }

        [HttpPost(Name = "Classify")]
        [ProducesResponseType(typeof(ClassifyResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<IActionResult> Post(ClassifyRequest classifyRequest)
        {
            string deviceId = HttpContext.Request.Headers["device_id"];
            string apiKey = HttpContext.Request.Headers["api_key"];

            var isAuthorized = await _authorizationService.IsDeviceAuthorized(deviceId, apiKey);

            if (!isAuthorized)
            {
                return Unauthorized("Invalid DeviceId or ApiKey.");
            }

            ClassifyResponse classifyResponse = await ClassifyAPI(classifyRequest);

            switch (classifyResponse.label)
            {
                case "-1":
                    return Ok(classifyResponse);
                case "-2":
                    return StatusCode(400, "Response not Successful");
                case "-3":
                    return StatusCode(500, $"Internal server error: {classifyResponse.metadata.source}");
                default:
                    return Ok(classifyResponse);
            }
        }

        public static async Task<ClassifyResponse> ClassifyAPI(ClassifyRequest classifyRequest)
        {
            string apiUrl = "http://158.75.112.151:9123/classify";


            var jsonPayload = JsonConvert.SerializeObject(classifyRequest);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            ClassifyResponse errorResponse = new ClassifyResponse();
            errorResponse.metadata = new CategoryNavigationMetadata();

            using (var httpClient = new HttpClient())
            {
                try
                {
                    var response = await httpClient.PostAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();
                        ClassifyResponse classifyResponse = JsonConvert.DeserializeObject<ClassifyResponse>(responseContent);

                        if (classifyResponse.label != null)
                        {
                            return (classifyResponse);
                        }
                        errorResponse.label = "-1";
                        return errorResponse;
                    }
                    else
                    {
                        errorResponse.label = "-2";
                        return errorResponse;
                    }
                }
                catch (Exception ex)
                {
                    errorResponse.label = "-3";
                    errorResponse.metadata.source = ex.Message;
                    return errorResponse;
                }
            }
        }
    }
}
