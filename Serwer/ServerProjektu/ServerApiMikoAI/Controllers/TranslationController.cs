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
    [SwaggerTag("Endpoint do tłumaczenia wiadomości.")]
    public class TranslationController : ControllerBase
    {
        private readonly AuthorizationService _authorizationService;
        private static Translator translator = new Translator("b7b072d0-f9c7-4820-8003-dcd228a1df91:fx");

        public TranslationController(AuthorizationService authorization)
        {
            _authorizationService = authorization;
        }

        /// <summary>
        /// Tłumaczy wiadomość na inny język.
        /// </summary>
        /// <param name="translationMessage">Obiekt zawierający wiadomość do przetłumaczenia oraz informacje o językach tłumaczenia.</param>
        /// <returns>Przetłumaczona wiadomość.</returns>
        /// <response code="200">Zwraca przetłumaczoną wiadomość.</response>
        /// <response code="401">Uwierzytelnianie nie powiodło się.</response>
        /// <response code="500">Wystąpił wewnętrzny błąd serwera.</response>
        [HttpPost(Name = "Translate")]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [SwaggerOperation(OperationId = "post", Summary = "Tłumaczy wiadomość", Description = "Tłumaczy wiadomość z jednego języka na inny przy użyciu API DeepL.")]
        public async Task<IActionResult> Post(TranslationMessage translationMessage)
        {
            string deviceId = HttpContext.Request.Headers["device_id"];
            string apiKey = HttpContext.Request.Headers["api_key"];

            var isAuthorized = await _authorizationService.IsDeviceAuthorized(deviceId, apiKey);

            if (!isAuthorized)
            {
                return Unauthorized("Invalid DeviceId or ApiKey.");
            }

            string result = await DeepLApi(translationMessage);

            switch (result)
            {
                case "-1":
                    return StatusCode(500, "Internal server error");
                default:
                    return Ok(result);
            }
        }

        public static async Task<string> DeepLApi([Required] TranslationMessage translationMessage)
        {
            try
            {
                var translatedMessage = await translator.TranslateTextAsync(
                    translationMessage.message,
                    translationMessage.translateFrom,
                    translationMessage.translateTo);

                return translatedMessage.Text;

            }
            catch (Exception ex)
            {
                return "-1";
            }

        }
    }
}
