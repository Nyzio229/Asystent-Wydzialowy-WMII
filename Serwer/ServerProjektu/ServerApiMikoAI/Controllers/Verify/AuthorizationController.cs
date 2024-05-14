using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models;
using Microsoft.EntityFrameworkCore;
using ServerApiMikoAI.Models.Context;
using System.Security.Cryptography;
using System.Text;
using Swashbuckle.AspNetCore.Annotations;

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
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<IActionResult> AuthenticateDevice() {
            // Pobierz nagłówki z żądania
            string deviceId = HttpContext.Request.Headers["device_id"];
            string apiKey = HttpContext.Request.Headers["api_key"];

            // Sprawdź czy nagłówki zostały przekazane
            if (string.IsNullOrEmpty(deviceId) || string.IsNullOrEmpty(apiKey)) {
                return BadRequest("DeviceId and ApiKey are required in headers.");
            }

            string encryptedApiKey;
            try {
                encryptedApiKey = EncryptApiKey(apiKey);
            }
            catch (CryptographicException) {
                return Unauthorized("Invalid ApiKey.");
            }

            // Sprawdź czy urządzenie jest autoryzowane
            var apiAccess = await _context.api_access
            .Where(aa => aa.device_id == deviceId && aa.api_key == encryptedApiKey && aa.is_active == true)
            .FirstOrDefaultAsync();


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
        private string DecryptApiKey(string encryptedApiKey) {
            using (Aes aesAlg = Aes.Create()) {
                byte[] key = Encoding.UTF8.GetBytes("asdasdasdasdasda"); // Klucz szyfrowania
                byte[] iv = Encoding.UTF8.GetBytes("asdasdasdasdasda"); // Wektor inicjalizacyjny

                using (ICryptoTransform decryptor = aesAlg.CreateDecryptor(key, iv)) {
                    byte[] encryptedBytes = Convert.FromBase64String(encryptedApiKey);
                    byte[] decryptedBytes = decryptor.TransformFinalBlock(encryptedBytes, 0, encryptedBytes.Length);
                    return Encoding.UTF8.GetString(decryptedBytes);
                }
            }
        }
    }
}
