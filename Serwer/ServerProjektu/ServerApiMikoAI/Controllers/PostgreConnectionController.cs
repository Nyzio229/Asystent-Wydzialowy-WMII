using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ServerApiMikoAI.Models.Context;
using Swashbuckle.AspNetCore.Annotations;

namespace ServerApiMikoAI.Controllers
{
    [Route("/FAQ")]
    [ApiController]
    public class PostgreConnectionController : ControllerBase
    {
        private readonly PostrgeSQLContext _context;
        public PostgreConnectionController(PostrgeSQLContext context)
        {
            _context = context;
        }

        [HttpPost("GetQuestion")]
        [ProducesResponseType(typeof(TableContext), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<IActionResult> GetQueryById(int id)
        {
            try
            {
                var query = await _context.asystentwydzialowy_faq.FindAsync(id);

                if (query == null)
                {
                    return NotFound("Querry null");
                }
                TableContext tableContext = new TableContext();
                tableContext = query;
                return Ok(tableContext);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }

        }
    }
}
