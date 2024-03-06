using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using ServerApiMikoAI.Models;
using Swashbuckle.AspNetCore.Annotations;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.Text;
using System.Text.Json.Nodes;


namespace ServerApiMikoAI.Controllers
{

    [ApiController]
    [Route("[controller]")]
    public class EmbedingController : ControllerBase
    {
        [HttpPost(Name = "Embedding")]
        [ProducesResponseType(typeof(double[]), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<float[]> Post(string request)
        {
            return await Embedding(request);
        }
        public static async Task<float[]> Embedding([FromBody][Required] string request)
        {
            string apiUrl = "http://localhost:5000/api/embedding";

            var inputData = new
            {
                input_string = request
            };

            var jsonPayload = JsonConvert.SerializeObject(inputData);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            using (var httpClient = new HttpClient())
            {
                try
                {
                    var response = await httpClient.PostAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();
                        //var responseData = JsonConvert.DeserializeObject(responseContent);

                        dynamic responseData = JsonConvert.DeserializeObject(responseContent);

                        var outputArray = responseData.output_string;


                        float[] output = new float[384];
                        int i = 0;
                        Console.WriteLine("Odpowiedź z API:");
                        foreach (string embedding in outputArray)
                        {
                            Console.WriteLine(embedding);
                            output[i++] = float.Parse(embedding, CultureInfo.InvariantCulture.NumberFormat);
                        }
                        return output;
                    }
                    else
                    {
                        Console.WriteLine($"Błąd: {response.StatusCode}");
                        //return $"Błąd: {response.StatusCode}";
                        //float[] a = { 0.1f, 0.2f };
                        return null;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Wystąpił błąd: {ex.Message}");
                    //return $"Wystąpił błąd: {ex.Message}";
                    //float[] a = { 0.1f, 0.2f };
                    return null;
                }
            }
        }
    }
}
