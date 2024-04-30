using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models;
using Microsoft.EntityFrameworkCore;
using ServerApiMikoAI.Models.Context;

namespace ServerApiMikoAI.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class AuthorizationController : ControllerBase {
        private readonly VerificationDataBaseContext _context;

        public AuthorizationController(VerificationDataBaseContext context) {
            _context = context;
        }
        [HttpPost]
        public async Task<IActionResult> AuthenticateDevice([FromBody] AuthorizationRequest request) {
            if (string.IsNullOrEmpty(request.device_id) || string.IsNullOrEmpty(request.api_key)) {
                return BadRequest("DeviceId and ApiKey are required.");
            }

            // Oblicz hash dla otrzymanego klucza API
            string hashedApiKey = CalculateHash(request.api_key);
            string apiKey = request.api_key;

            // Sprawdź, czy istnieje pasujący wpis w bazie danych
            var apiAccess = await _context.api_access.Where(aa => aa.device_id == request.device_id && aa.api_key == apiKey).FirstOrDefaultAsync();

            if (apiAccess == null) {
                return Unauthorized("Invalid DeviceId or ApiKey.");
            }

            return Ok("Device authenticated successfully.");
        }
        private string CalculateHash(string apiKey) {
            // Tutaj możesz użyć dowolnego algorytmu haszowania, np. SHA256
            // Poniżej znajduje się przykładowa implementacja z użyciem SHA256
            using (var sha256 = System.Security.Cryptography.SHA256.Create()) {
                byte[] hashBytes = sha256.ComputeHash(System.Text.Encoding.UTF8.GetBytes(apiKey));
                return BitConverter.ToString(hashBytes).Replace("-", "").ToLower();
            }
        }
    }
}
