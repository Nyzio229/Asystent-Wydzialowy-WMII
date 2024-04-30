using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models;
using System.ComponentModel.DataAnnotations;
using MailKit.Net.Smtp;
using MimeKit;
using MimeKit.Text;
using MailKit.Security;
using ServerApiMikoAI.Models.Context;
using ServerApiMikoAI.Models.Verify;

namespace ServerApiMikoAI.Controllers.Verify
{
    [Route("[controller]")]
    [ApiController]
    public class VerifyEmailController : ControllerBase
    {
        private readonly VerificationDataBaseContext _context;
        private readonly EmailSettings _email;
        public VerifyEmailController(VerificationDataBaseContext context)
        {
            _context = context;
        }

        [HttpPost]
        public async Task<string> VerifyEmail([FromBody] VerifyEmailRequest request)
        {
            if (string.IsNullOrEmpty(request.Email) || string.IsNullOrEmpty(request.DeviceId))
            {
                return "Email and DeviceId are required.";
            }
            Random rnd = new Random();
            int verificationCode = rnd.Next(100000, 999999);
            DateTime expirationDateLocal = DateTime.Now.AddMinutes(15);
            DateTime expirationDateUtc = expirationDateLocal.ToUniversalTime();

            var emailVerifcation = new VerificationTableContext
            {
                device_id = request.DeviceId,
                verification_code = verificationCode,
                expiration_date = expirationDateUtc                                
            };


            _context.verification_table.Add(emailVerifcation);
            await _context.SaveChangesAsync();

            // obsługa wysłania maila
            try
            {
                var mail = new MimeMessage();
                mail.From.Add(MailboxAddress.Parse("mikolai@noreply.pl"));
                mail.To.Add(MailboxAddress.Parse(request.Email));
                mail.Subject = "!!!!!!!!!!!!Kod aktywacyjny TEST!!!!!!!!!!!!!";
                mail.Body = new TextPart(TextFormat.Html) { Text = $"Kod weryfikacyjny do aplikacji to: {verificationCode}" };

                using (var smtp = new SmtpClient())
                {
                    smtp.Connect("smtp.ethereal.email", 587, SecureSocketOptions.StartTls);
                    smtp.Authenticate("gayle.smitham@ethereal.email", "mTCWk2Fx1bj12vKXyF");
                    smtp.Send(mail);
                    smtp.Disconnect(true);
                }

            }
            catch (Exception ex)
            {
                return $"Erorr: {ex.Message}";
            }
            return $"Wysłano kod: {verificationCode}, na adres: {request.Email}";
        }
    }
}
