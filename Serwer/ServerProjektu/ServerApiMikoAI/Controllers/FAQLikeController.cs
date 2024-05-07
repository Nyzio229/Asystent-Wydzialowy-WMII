using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using ServerApiMikoAI.Models;
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

        [HttpPost(Name = "FAQLikeRequest")]
        [ProducesResponseType(typeof(FAQFinalResponse), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<FAQFinalResponse> Post(FAQMessage FAQMessage)
        {
            return await FAQLikeRequest(FAQMessage);
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
                faqFinalItem.answerEN = "-1";
                faqFinalItem.questionEN = "-1";
                faqFinalItem.answerPL = "-1";
                faqFinalItem.questionPL = "-1";
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
                        
                        if (faqResponse.faq_ids != null)
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
                        return faqFinalResponse;
                    }
                    else
                    {
                        return faqFinalResponse;
                    }
                }
                catch (Exception ex)
                {
                    return faqFinalResponse;
                }
            }
        }
    }
}
