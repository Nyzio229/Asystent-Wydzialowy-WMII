using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models;
using Swashbuckle.AspNetCore.Annotations;

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
        public async Task<TableContext> Post(FAQMessage FAQMessage)
        {
            return await FAQRequest(FAQMessage, _context);
        }

        public static async Task<TableContext> FAQRequest(FAQMessage FAQMessage, PostrgeSQLContext postrgeSQLContext)
        {
            float[] embedding = await EmbedingController.Embedding(FAQMessage.message);
            int resultId = await QdrantController.QdrantClientId(embedding);

            if (resultId != -1)
            {
                PostgreConnectionController postgreConnectionController = new PostgreConnectionController(postrgeSQLContext);
                TableContext tableContext = await postgreConnectionController.GetQueryById(resultId);

                return tableContext;
            }
            return new TableContext { id_pytania = -1 , odpowiedz = null, pytanie = null};
        }
    }
}
