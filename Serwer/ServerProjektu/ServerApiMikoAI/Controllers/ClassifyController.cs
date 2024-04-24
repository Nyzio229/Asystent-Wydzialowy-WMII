using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using ServerApiMikoAI.Models.Classify;
using Swashbuckle.AspNetCore.Annotations;
using System.Text;

namespace ServerApiMikoAI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ClassifyController : ControllerBase
    {
        [HttpPost(Name = "Classify")]
        [ProducesResponseType(typeof(ClassifyResponse), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<ClassifyResponse> Post(ClassifyRequest classifyRequest)
        {
            return await ClassifyAPI(classifyRequest);
        }

        public static async Task<ClassifyResponse> ClassifyAPI(ClassifyRequest classifyRequest)
        {
            string apiUrl = "http://158.75.112.151:9123/classify";


            var jsonPayload = JsonConvert.SerializeObject(classifyRequest);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            ClassifyResponse classifyResponseError = new ClassifyResponse();
            classifyResponseError.label = "-1";

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
                            return classifyResponse;
                        }
                        return classifyResponseError;
                    }
                    else
                    {
                        return classifyResponseError;
                    }
                }
                catch (Exception ex)
                {
                    return classifyResponseError;
                }
            }
        }
    }
}
