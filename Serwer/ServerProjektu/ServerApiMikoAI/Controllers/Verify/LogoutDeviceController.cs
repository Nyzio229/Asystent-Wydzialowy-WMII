using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models.Context;
using Swashbuckle.AspNetCore.Annotations;
using Microsoft.EntityFrameworkCore;

namespace ServerApiMikoAI.Controllers.Verify {
    [Route("api/[controller]")]
    [ApiController]
    public class LogoutDeviceController : ControllerBase {
        private readonly VerificationDataBaseContext _context;
        public LogoutDeviceController(VerificationDataBaseContext context) {
            _context = context; 
        }
        [HttpPost]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<IActionResult> LogoutDevice([FromBody] LogoutRequest request) {
            // Sprawdzamy, czy istnieje wpis dla danego deviceId w tabeli api_access
            var apiAccessEntry = await _context.api_access.FirstOrDefaultAsync(a => a.device_id == request.device_id);

            if (apiAccessEntry == null) {
                return NotFound("Device not found.");
            }

            // Ustawiamy pole is_active na false dla danego urządzenia
            apiAccessEntry.is_active = false;

            // Zapisujemy zmiany do bazy danych
            await _context.SaveChangesAsync();

            return Ok("Device logged out successfully.");
        }
    }
    public class LogoutRequest {
        public string device_id { get; set; }
    }
}
