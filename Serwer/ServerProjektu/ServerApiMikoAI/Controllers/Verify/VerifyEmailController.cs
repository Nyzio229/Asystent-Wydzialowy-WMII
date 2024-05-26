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
using Swashbuckle.AspNetCore.Annotations;
using Microsoft.Extensions.Configuration;


namespace ServerApiMikoAI.Controllers.Verify
{
    [Route("[controller]")]
    [ApiController]
    public class VerifyEmailController : ControllerBase
    {
        private readonly VerificationDataBaseContext _context;
        private readonly EmailSettings _email;
        private readonly IConfiguration _configuration;
        public VerifyEmailController(VerificationDataBaseContext context, IConfiguration configuration)
        {
            _context = context;
            _configuration = configuration;
        }

        [HttpPost]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post")]
        public async Task<IActionResult> VerifyEmail([FromBody] VerifyEmailRequest request) {
            if (string.IsNullOrEmpty(request.Email) || string.IsNullOrEmpty(request.DeviceId)) {
                return BadRequest("Email and DeviceId are required.");
            }

            Random rnd = new Random();
            int verificationCode = rnd.Next(100000, 999999);
            DateTime expirationDateLocal = DateTime.Now.AddMinutes(15);
            DateTime expirationDateUtc = expirationDateLocal.ToUniversalTime();

            var emailVerification = new VerificationTableContext {
                device_id = request.DeviceId,
                verification_code = verificationCode,
                expiration_date = expirationDateUtc
            };

            _context.verification_table.Add(emailVerification);
            await _context.SaveChangesAsync();

            // obsługa wysłania maila
            try {
                var mail = new MimeMessage();
                mail.From.Add(new MailboxAddress("MikoAI Support", "mikolai@noreply.pl"));
                mail.To.Add(MailboxAddress.Parse(request.Email));
                mail.Subject = "Twój kod weryfikacyjny do aplikacji MikoAI";
                mail.Body = new TextPart(TextFormat.Html) {
                    Text = $@"
                        <html>
                        <body>
                            <p>Witaj,</p>
                            <p>Dziękujemy za korzystanie z aplikacji MikoAI.</p>
                            <p>Twój kod weryfikacyjny to: <strong>{verificationCode}</strong></p>
                            <p>Kod jest ważny przez 15 minut.</p>
                            <p>Jeżeli nie prosiłeś o ten kod, zignoruj tę wiadomość.</p>
                            <br/>
                            <p>Pozdrawiamy,</p>
                            <p>Zespół MikoAI</p>
                        </body>
                        </html>"
                };

                using (var smtp = new SmtpClient()) {
                    smtp.Connect("poczta1.mat.umk.pl", 587, SecureSocketOptions.StartTls);
                    smtp.Authenticate(_configuration["MailServerSettings:Login"], _configuration["MailServerSettings:Pswd"]);
                    smtp.Send(mail);
                    smtp.Disconnect(true);
                }

            }
            catch (Exception ex) {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Error: {ex.Message}");
            }
            return Ok($"Kod weryfikacyjny został wysłany na adres: {request.Email}");
        }
    }
}
