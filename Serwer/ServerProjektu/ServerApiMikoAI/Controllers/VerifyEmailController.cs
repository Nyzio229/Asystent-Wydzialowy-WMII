using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models;
using System.ComponentModel.DataAnnotations;
using MailKit;

namespace ServerApiMikoAI.Controllers {
    [Route("[controller]")]
    [ApiController]
    public class VerifyEmailController : ControllerBase {
        private readonly VerificationDataBaseContext _context;
        public VerifyEmailController(VerificationDataBaseContext context) {
            _context = context;
        }
        [HttpPost]
       
        public async Task<string> VerifyEmail([FromBody]VerifyEmailRequest request) {
            if (string.IsNullOrEmpty(request.Email) || string.IsNullOrEmpty(request.DeviceId)) {
                return "Email and DeviceId are required.";
            }
            Random rnd = new Random();
            int verificationCode = rnd.Next(100000, 999999);

            var emailVerifcation = new VerificationTableContext { 
                device_id = request.DeviceId, 
                verify_code = verificationCode 
            };
                
        
            _context.verification_table.Add(emailVerifcation);
            await _context.SaveChangesAsync();

            return null;
        }
    }
}
