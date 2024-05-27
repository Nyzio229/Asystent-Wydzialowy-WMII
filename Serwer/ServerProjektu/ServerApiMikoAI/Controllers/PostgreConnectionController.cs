using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ServerApiMikoAI.Models.Context;
using Swashbuckle.AspNetCore.Annotations;

namespace ServerApiMikoAI.Controllers
{
    [Route("/FAQ")]
    [ApiController]
    [SwaggerTag("Endpoint do operacji związanych z FAQ.")]
    public class PostgreConnectionController : ControllerBase
    {
        private readonly PostrgeSQLContext _context;
        public PostgreConnectionController(PostrgeSQLContext context)
        {
            _context = context;
        }
        /// <summary>
        /// Pobiera pytanie na podstawie identyfikatora.
        /// </summary>
        /// <param name="id">Identyfikator pytania.</param>
        /// <returns>Informacje o pytaniu.</returns>
        /// <response code="200">Zwraca informacje o pytaniu.</response>
        /// <response code="401">Uwierzytelnianie nie powiodło się.</response>
        /// <response code="404">Pytanie nie zostało znalezione.</response>
        /// <response code="500">Wystąpił wewnętrzny błąd serwera.</response>
        [HttpPost("GetQuestion")]
        [ProducesResponseType(typeof(TableContext), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
        [SwaggerOperation(OperationId = "post", Summary = "Pobiera pytanie na podstawie identyfikatora", Description = "Pobiera pytanie z bazy danych na podstawie podanego identyfikatora.")]
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
