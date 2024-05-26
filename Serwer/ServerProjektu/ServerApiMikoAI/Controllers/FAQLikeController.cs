using Google.Protobuf.WellKnownTypes;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore.Metadata.Internal;
using Newtonsoft.Json;
using ServerApiMikoAI.Models;
using ServerApiMikoAI.Models.Classify;
using ServerApiMikoAI.Models.Context;
using ServerApiMikoAI.Models.FAQ;
using Swashbuckle.AspNetCore.Annotations;
using System.Text;

namespace ServerApiMikoAI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class FAQLikeController : ControllerBase
    {
        private readonly AuthorizationService _authorizationService;

        public FAQLikeController(AuthorizationService authorization)
        {
            _authorizationService = authorization;
        }

        [HttpPost(Name = "FAQLikeRequest")]
        [ProducesResponseType(typeof(FAQFinalResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<IActionResult> Post(FAQMessage FAQMessage)
        {
            string deviceId = HttpContext.Request.Headers["device_id"];
            string apiKey = HttpContext.Request.Headers["api_key"];

            var isAuthorized = await _authorizationService.IsDeviceAuthorized(deviceId, apiKey);

            if (!isAuthorized)
            {
                return Unauthorized("Invalid DeviceId or ApiKey.");
            }


            FAQFinalResponse faqFinalResponse = await FAQLikeRequest(FAQMessage);
            switch (faqFinalResponse.faq[0].answerPL)
            {
                case "-1":
                    return Ok(faqFinalResponse);
                case "-2":
                    return StatusCode(400, "Response not Successful");
                case "-3":
                    return StatusCode(500, $"Internal server error: {faqFinalResponse.faq[0].questionPL}");
                default:
                    return Ok(faqFinalResponse);
            }
        }

        public static async Task<FAQFinalResponse> FAQLikeRequest(FAQMessage faqMessage)
        {
            string apiUrl = "http://158.75.112.151:9123/faq_like";

            var jsonPayload = JsonConvert.SerializeObject(faqMessage);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            FAQFinalResponse faqFinalResponse = new FAQFinalResponse();
            faqFinalResponse.faq = new List<FAQFinalItem>();

            for (int i = 0; i < faqMessage.limit; i++)
            {
                FAQFinalItem faqFinalItem = new FAQFinalItem();
                faqFinalResponse.faq.Add(faqFinalItem);
            }
            using (var httpClient = new HttpClient())
            {
                try
                {
                    var response = await httpClient.PostAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();
                        FAQResponse faqResponse = JsonConvert.DeserializeObject<FAQResponse>(responseContent);

                        if (faqResponse.faq_ids.Length > 0)
                        {
                            FAQRequest faqRequestEN = new FAQRequest();
                            FAQRequest faqRequestPL = new FAQRequest();

                            faqRequestEN.faq_ids = faqResponse.faq_ids;
                            faqRequestPL.faq_ids = faqResponse.faq_ids;
                            faqRequestPL.lang = "pl";
                            faqRequestEN.lang = "en";

                            FAQResult faqResultEN = await FAQController.FAQRequest(faqRequestEN);
                            FAQResult faqResultPL = await FAQController.FAQRequest(faqRequestPL);

                            for (int i = 0; i < faqResponse.faq_ids.Length; i++)
                            {
                                faqFinalResponse.faq[i].answerEN = faqResultEN.faq[i].answer;
                                faqFinalResponse.faq[i].questionEN = faqResultEN.faq[i].question;
                                faqFinalResponse.faq[i].answerPL = faqResultPL.faq[i].answer;
                                faqFinalResponse.faq[i].questionPL = faqResultPL.faq[i].question;
                            }
                            return faqFinalResponse;
                        }
                        faqFinalResponse.faq[0].answerPL = "-1";
                        faqFinalResponse.faq[0].answerEN = "-1";
                        faqFinalResponse.faq[0].questionPL = "-1";
                        faqFinalResponse.faq[0].questionEN = "-1";
                        return faqFinalResponse;
                    }
                    else
                    {
                        faqFinalResponse.faq[0].answerPL = "-2";
                        return faqFinalResponse;
                    }
                }
                catch (Exception ex)
                {
                    faqFinalResponse.faq[0].answerPL = "-3";
                    faqFinalResponse.faq[0].questionPL = ex.Message;
                    return faqFinalResponse;
                }
            }
        }
    }
}
