using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models;
using Microsoft.EntityFrameworkCore;
using ServerApiMikoAI.Models.Context;
using System.Security.Cryptography;
using System.Text;

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
            string encryptedApiKey = EncryptApiKey(request.api_key);
            string apiKey = request.api_key;

            // Sprawdź, czy istnieje pasujący wpis w bazie danych
            var apiAccess = await _context.api_access.Where(aa => aa.device_id == request.device_id && aa.api_key == encryptedApiKey).FirstOrDefaultAsync();

            if (apiAccess == null) {
                return Unauthorized("Invalid DeviceId or ApiKey.");
            }

            return Ok("Device authenticated successfully.");
        }
        
        // Metoda do szyfrowania klucza API
        private string EncryptApiKey(string apiKey) {
            using (Aes aesAlg = Aes.Create()) {
                byte[] key = Encoding.UTF8.GetBytes("asdasdasdasdasda"); // Klucz szyfrowania (musi być taki sam jak używany do szyfrowania w VerificationController)
                byte[] iv = Encoding.UTF8.GetBytes("asdasdasdasdasda"); // Wektor inicjalizacyjny (musi być taki sam jak używany do szyfrowania w VerificationController)

                using (ICryptoTransform encryptor = aesAlg.CreateEncryptor(key, iv)) {
                    byte[] encryptedBytes = encryptor.TransformFinalBlock(Encoding.UTF8.GetBytes(apiKey), 0, apiKey.Length);
                    return Convert.ToBase64String(encryptedBytes);
                }
            }
        }
    }
}
