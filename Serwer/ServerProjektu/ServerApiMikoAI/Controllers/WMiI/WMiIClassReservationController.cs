using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models.Context;
using Swashbuckle.AspNetCore.Annotations;

namespace ServerApiMikoAI.Controllers.WMiI {
    [Route("[controller]")]
    [ApiController]
    public class WMiIClassReservationController : ControllerBase {
        private readonly WMiIPlansDatabase _context;
        public WMiIClassReservationController(WMiIPlansDatabase context) {
            _context = context;
        }

        [HttpPost]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
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
