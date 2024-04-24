using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using ServerApiMikoAI.Models.Context;
using ServerApiMikoAI.Models.FAQ;
using Swashbuckle.AspNetCore.Annotations;
using System.Text;

namespace ServerApiMikoAI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class FAQController : ControllerBase
    {
        private readonly PostrgeSQLContext _context;
        public FAQController(PostrgeSQLContext context)
        {
            _context = context;
        }

        [HttpPost(Name = "FAQRequest")]
        [ProducesResponseType(typeof(TableContext), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<TableContext[]> Post(FAQMessage FAQMessage)
        {
            return await FAQRequest(FAQMessage, _context);
        }

        public static async Task<TableContext[]> FAQRequest(FAQMessage FAQMessage, PostrgeSQLContext postrgeSQLContext)
        {
            string apiUrl = "http://158.75.112.151:9123/faq_like";

            var jsonPayload = JsonConvert.SerializeObject(FAQMessage);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            TableContext[] tableContexts = new TableContext[FAQMessage.limit];
            tableContexts[0] = new TableContext();
            tableContexts[0].id_pytania = -1;
            //tableContexts[0].id_pytania = 1;
            //tableContexts[0].odpowiedz = "Odpowiedz ddddd";
            //tableContexts[0].pytanie = "Pytanie pppppppp";

            using (var httpClient = new HttpClient())
            {
                try
                {
                    var response = await httpClient.PostAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();
                        FAQResponse faqResponse = JsonConvert.DeserializeObject<FAQResponse>(responseContent);

                        if (faqResponse.faq_ids != null && faqResponse.faq_ids.Length > 0)
                        {
                            PostgreConnectionController postgreConnectionController = new PostgreConnectionController(postrgeSQLContext);
                            for (int i = 0; i < faqResponse.faq_ids.Length; i++)
                            {
                                tableContexts[i] = await postgreConnectionController.GetQueryById(faqResponse.faq_ids[i]);
                            }
                            return tableContexts;
                        }
                        return tableContexts;
                    }
                    else
                    {
                        return tableContexts;
                    }
                }
                catch (Exception ex)
                {
                    tableContexts[0].id_pytania = -1;
                    return tableContexts;
                }
            }
        }
    }
}
