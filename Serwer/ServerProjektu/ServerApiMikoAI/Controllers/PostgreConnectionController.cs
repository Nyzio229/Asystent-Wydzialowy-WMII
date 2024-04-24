using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ServerApiMikoAI.Models.Context;
using Swashbuckle.AspNetCore.Annotations;

namespace ServerApiMikoAI.Controllers
{
    [Route("/FAQ")]
    [ApiController]
    public class PostgreConnectionController : ControllerBase {
        private readonly PostrgeSQLContext _context;
        public PostgreConnectionController(PostrgeSQLContext context) 
        { 
            _context = context; 
        }

        [HttpPost("GetQuestion")]
        [ProducesResponseType(typeof(TableContext), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<TableContext> GetQueryById(int id) {
            var query = await _context.asystentwydzialowy_faq.FindAsync(id);

            if (query == null) {
                return null;
            }
            TableContext tableContext = new TableContext();
            tableContext = query;
            return tableContext;
        }
    }
}
