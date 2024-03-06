using Microsoft.AspNetCore.Mvc;
using Qdrant.Client.Grpc;
using Qdrant.Client;
using Swashbuckle.AspNetCore.Annotations;
using System.ComponentModel.DataAnnotations;
using System.Text;
using Grpc.Core.Interceptors;
using Grpc.Net.Client;
using Newtonsoft.Json;
using System.Globalization;
using System.Diagnostics;
using ServerApiMikoAI.Models;

namespace ServerApiMikoAI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class QdrantController : ControllerBase
    {
        [HttpPost(Name = "Qdrant")]
        [ProducesResponseType(typeof(int), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<int> Post(float[] request)
        {
            return await QdrantClientId(request);
        }
        
        public static async Task<int> QdrantClientId([FromBody][Required] float[] request)
        {
            string apiUrl = "http://localhost:5000/api/getIndex";

            var data = new
            {
                data = request
            };

            var jsonPayload = JsonConvert.SerializeObject(data);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            using (var httpClient = new HttpClient())
            {
                try
                {
                    var response = await httpClient.PostAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();

                        QdrantClientAnswer responseData = JsonConvert.DeserializeObject<QdrantClientAnswer>(responseContent);

                        return responseData.output_string;
                    }
                    return -1;
                }
                catch
                {
                    return -1;
                }
            }
        }
    }

    public class QdrantClientAnswer
    {
        public int output_string;
    }
}
