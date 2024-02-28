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
            return await QdrantClient(request);
        }
        
        public static async Task<int> QdrantClient([FromBody][Required] float[] request)
        {
            var cmd = "C:/Users/Admin/Desktop/qdrantClient.py ";

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe";
            start.Arguments = cmd + JsonConvert.SerializeObject(request);
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            start.CreateNoWindow = true;

            using (Process process = Process.Start(start))
            {
                using (StreamReader reader = process.StandardOutput)
                {
                    string stderr = process.StandardError.ReadToEnd(); 
                    string  result = await reader.ReadToEndAsync(); 
                    return int.Parse(result);
                }
            }
        }

    }
}
