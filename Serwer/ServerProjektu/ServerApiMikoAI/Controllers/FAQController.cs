﻿using Microsoft.AspNetCore.Http;
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
    [SwaggerTag("Endpoint do porówanania embedindu.")]
    public class FAQController : ControllerBase
    {
        /// <summary>
        /// Na podstawie podanego embedingu i języka znajduje pytanie i odpowiedź z FAQ.
        /// </summary>
        /// <param name="faqRequest">Obiekt zawierający zembedowane pytania i język.</param>
        /// <returns>Odpowiedź z listą pytań i odpowiedzi z FAQ.</returns>
        /// <response code="200">Zwraca listę pytań i odpowiedzi.</response>
        /// <response code="401">Uwierzytelnianie nie powiodło się.</response>
        /// <response code="500">Wystąpił wewnętrzny błąd serwera.</response>
        [HttpPost(Name = "FAQRequest")]
        [ProducesResponseType(typeof(FAQResult), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [SwaggerOperation(OperationId = "post", Summary = "Przetwarza zembedowane pytanie", Description = "Przetwarza zembedowane pytanie i zwaraca listę odpowiedzi i pytań z FAQ.")]
        public async Task<IActionResult> Post(FAQRequest faqRequest)
        {
            FAQResult result = await FAQRequest(faqRequest);
            if (result.faq[0].answer == "-1")
            {
                return StatusCode(500, $"Internal server error: Unexpected error");
            }
            return Ok(result);
        }

        public static async Task<FAQResult> FAQRequest(FAQRequest faqRequest)
        {
            string apiUrl = "http://158.75.112.151:9123/faq";

            var jsonPayload = JsonConvert.SerializeObject(faqRequest);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");


            FAQResult FAQResult = new FAQResult();
            FAQResult.faq = new List<FAQItem>();

            for (int i = 0; i < faqRequest.faq_ids.Length; i++)
            {
                FAQItem FAQItem = new FAQItem();
                FAQItem.answer = "-1";
                FAQItem.question = "-1";
                FAQResult.faq.Add(FAQItem);
            }

            using (var httpClient = new HttpClient())
            {
                try
                {
                    var response = await httpClient.PostAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();
                        FAQResult faqResponse = JsonConvert.DeserializeObject<FAQResult>(responseContent);

                        return faqResponse;
                    }
                    else
                    {
                        return FAQResult;
                    }
                }
                catch (Exception ex)
                {
                    return FAQResult;
                }
            }
        }
    }
}
