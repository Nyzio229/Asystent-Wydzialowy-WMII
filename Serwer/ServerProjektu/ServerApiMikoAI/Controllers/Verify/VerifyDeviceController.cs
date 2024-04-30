using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ServerApiMikoAI.Models.Context;
using ServerApiMikoAI.Models.Verify;

namespace ServerApiMikoAI.Controllers.Verify
{
    [Route("[controller]")]
    [ApiController]
    public class VerifyDeviceController : ControllerBase
    {
        private readonly VerificationDataBaseContext _context;

        public VerifyDeviceController(VerificationDataBaseContext context)
        {
            _context = context;
        }

        [HttpPost]
        public async Task<IActionResult> VerifyCode([FromBody] VerifyDeviceRequest request)
        {

            if (string.IsNullOrEmpty(request.DeviceId) || request.VerificationCode <= 0)
            {
                return Ok("DeviceId and VerificationCode are required.");
            }

            // Sprawdź, czy istnieje taki kod weryfikacyjny dla danego urządzenia
            var emailVerification = await _context.verification_table
                .Where(ev => ev.device_id == request.DeviceId && ev.verify_code == request.VerificationCode).FirstOrDefaultAsync();

            if (emailVerification == null)
            {
                return Ok("Invalid verification code or device id.");
            }

            // Wygeneruj klucz API
            var apiKey = Guid.NewGuid().ToString(); // Możesz użyć innego mechanizmu generowania klucza API

            // Zapisz klucz API w bazie danych
            var apiAccess = new ApiAccessTableContext
            {
                device_id = request.DeviceId,
                api_key = apiKey
            };

            _context.api_access.Add(apiAccess);
            await _context.SaveChangesAsync();

            return Ok(new { ApiKey = apiKey });
            //return null;
        }


    }
}
