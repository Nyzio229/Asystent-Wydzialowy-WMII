using DeepL;
using Google.Protobuf;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models;
using Swashbuckle.AspNetCore.Annotations;
using System.ComponentModel.DataAnnotations;

namespace ServerApiMikoAI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class TranslationController : ControllerBase
    {
        //private static Translator translator = new Translator("b7b072d0-f9c7-4820-8003-dcd228a1df91:fx");

        private static Translator translator = new Translator("f2a2b36d-035d-4a47-8440-b33db0b4ec8b:fx\r\n");

        [HttpPost(Name = "Translate")]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<string> Post(TranslationMessage translationMessage)
        {
            return await DeepLApi(translationMessage);
        }

        public static async Task<string> DeepLApi([Required] TranslationMessage translationMessage)
        {
            var translatedMessage = await translator.TranslateTextAsync(
              translationMessage.message,
              translationMessage.translateFrom,
              translationMessage.translateTo);

            return translatedMessage.Text;
        }
    }
}
