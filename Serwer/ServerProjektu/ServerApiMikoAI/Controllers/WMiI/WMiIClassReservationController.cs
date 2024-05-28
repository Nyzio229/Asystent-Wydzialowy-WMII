using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models.Context;
using Swashbuckle.AspNetCore.Annotations;

namespace ServerApiMikoAI.Controllers.WMiI {
    [Route("[controller]")]
    [ApiController]
    [SwaggerTag("Endpoint do rezerwacji sal w WMiI.")]
    public class WMiIClassReservationController : ControllerBase {
        private readonly WMiIPlansDatabase _context;
        public WMiIClassReservationController(WMiIPlansDatabase context) {
            _context = context;
        }
        /// <summary>
        /// Pobiera rezerwacje sal na podaną datę.
        /// </summary>
        /// <param name="date">Data w formacie 'yyyy-MM-dd'.</param>
        /// <returns>Lista rezerwacji dla podanej daty.</returns>
        /// <response code="200">Zwraca listę rezerwacji sal na podaną datę.</response>
        /// <response code="400">Podany format daty jest nieprawidłowy.</response>
        /// <response code="500">Wystąpił błąd serwera.</response>
        [HttpPost]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post", Summary = "Pobiera rezerwacje sal na podaną datę", Description = "Pobiera rezerwacje sal na podaną datę w formacie 'yyyy-MM-dd'.")]
        public async Task<IActionResult> GetClassReservation(string date) {
            try {
                if (!DateTime.TryParse(date, out DateTime parsedDate)) {
                    return BadRequest("Invalid date format. Please provide the date in yyyy-mm-dd format.");
                }

                var rezerwacje = _context.Rezerwacje
                    .Where(r => r.dzien == parsedDate.Date)
                    .Select(r => new {
                        day = r.dzien.ToString("yyyy-MM-dd"),
                        hour = r.godz,
                        @class = r.sala
                    })
                    .ToList();

                return Ok(rezerwacje);
            }
            catch (Exception ex) {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
