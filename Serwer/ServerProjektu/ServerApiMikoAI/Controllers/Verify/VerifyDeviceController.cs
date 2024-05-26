using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ServerApiMikoAI.Models.Context;
using ServerApiMikoAI.Models.Verify;
using Swashbuckle.AspNetCore.Annotations;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Configuration;

namespace ServerApiMikoAI.Controllers.Verify
{
    [Route("[controller]")]
    [ApiController]
    public class VerifyDeviceController : ControllerBase
    {
        private readonly VerificationDataBaseContext _context;
        private readonly IConfiguration _configuration;

        public VerifyDeviceController(VerificationDataBaseContext context, IConfiguration configuration)
        {
            _context = context;
            _configuration = configuration;

        }

        [HttpPost]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<IActionResult> VerifyCode([FromBody] VerifyDeviceRequest request) {

            if (string.IsNullOrEmpty(request.DeviceId) || request.VerificationCode <= 0) {
                return Ok("DeviceId and VerificationCode are required.");
            }


            //var emailVerification = await _context.verification_table.Where(ev => ev.device_id == request.DeviceId && ev.verification_code == request.VerificationCode).FirstOrDefaultAsync();

            var emailVerification = await _context.verification_table
                .Where(ev => ev.device_id == request.DeviceId && ev.verification_code == request.VerificationCode && ev.expiration_date >= DateTime.UtcNow)
                .FirstOrDefaultAsync();

            if (emailVerification == null) {
                return Ok("Invalid verification code or device id.");
            }


            // Wygeneruj i zaszyfruj klucz API
            var apiKey = GenerateApiKey();
            var encryptedApiKey = EncryptApiKey(apiKey);

            // Zapisz zaszyfrowany klucz API w bazie danych
            var apiAccess = new ApiAccessTableContext {
                device_id = request.DeviceId,
                api_key = encryptedApiKey,
                is_active = true
            };

            _context.api_access.Add(apiAccess);
            await _context.SaveChangesAsync();


            // Zapisz klucz API w bazie danych
            //var apiAccess = new ApiAccessTableContext
            //{
            //    device_id = request.DeviceId,
            //    api_key = apiKey
            //};
            //_context.api_access.Add(apiAccess);
            //await _context.SaveChangesAsync();

            return Ok(new { ApiKey = apiKey });
            //return null;
        }



        private string GenerateApiKey() {
            return Guid.NewGuid().ToString("N"); // Wygenerowanie unikalnego klucza API
        }

        // Metoda do szyfrowania klucza API
        private string EncryptApiKey(string apiKey) {
            using (Aes aesAlg = Aes.Create()) {
                byte[] key = Encoding.UTF8.GetBytes(_configuration["EncryptionSettings:Key"]); // Klucz szyfrowania (możesz użyć inny klucz)
                byte[] iv = Encoding.UTF8.GetBytes(_configuration["EncryptionSettings:IV"]); // Wektor inicjalizacyjny (możesz użyć inny wektor)



                using (ICryptoTransform encryptor = aesAlg.CreateEncryptor(key, iv)) {
                    byte[] encryptedBytes = encryptor.TransformFinalBlock(Encoding.UTF8.GetBytes(apiKey), 0, apiKey.Length);
                    return Convert.ToBase64String(encryptedBytes);
                }
            }
        }

    }
}
