using MailKit.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using MimeKit.Text;
using MimeKit;
using ServerApiMikoAI.Models;
using MailKit.Net.Smtp;

namespace ServerApiMikoAI.Controllers {
    [Route("api/[controller]")]
    [ApiController]
    public class VerifyGmailController : ControllerBase {
        //private readonly VerificationDataBaseContext _context;
        //private readonly EmailSettings _email;
        //public VerifyGmailController(VerificationDataBaseContext context) {
        //    _context = context;
        //}

        //[HttpPost]
        //public async Task<string> VerifyEmail([FromBody] VerifyEmailRequest request) {
        //    if (string.IsNullOrEmpty(request.Email) || string.IsNullOrEmpty(request.DeviceId)) {
        //        return "Email and DeviceId are required.";
        //    }
        //    Random rnd = new Random();
        //    int verificationCode = rnd.Next(100000, 999999);

        //    var emailVerifcation = new VerificationTableContext {
        //        device_id = request.DeviceId,
        //        verify_code = verificationCode
        //    };


        //    _context.verification_table.Add(emailVerifcation);
        //    await _context.SaveChangesAsync();

        //    // obsługa wysłania maila
        //    try {
        //        UserCredential credential = await GoogleWebAuthorizationBroker.AuthorizeAsync(
        //            new ClientSecrets {
        //                ClientId = "45354090370-po2gcn6l9sihskqh4cfbb7ie7k293448.apps.googleusercontent.com",
        //                ClientSecret = "YourClientSecret"
        //            },
        //            new[] { GmailService.Scope.GmailSend },
        //            "user",
        //            CancellationToken.None
        //        );

        //        var service = new GmailService(new BaseClientService.Initializer() {
        //            HttpClientInitializer = credential,
        //            ApplicationName = "YourAppName"
        //        });

        //        var message = CreateEmailMessage(request.Email, "Your Name", "Verification Code", $"Your verification code is: {verificationCode}");
        //        await SendMessage(service, "me", message);

        //    }
        //    catch (Exception ex) {
        //        return $"Erorr: {ex.Message}";
        //    }
        //    return $"Wysłano kod: {verificationCode}, na adres: {request.Email}";
        //}
        //private MimeMessage CreateEmailMessage(string toEmail, string fromName, string subject, string messageText) {
        //    var message = new MimeMessage();
        //    message.From.Add(new MailboxAddress(fromName, _emailSettings.FromEmail));
        //    message.To.Add(new MailboxAddress(toEmail));
        //    message.Subject = subject;
        //    message.Body = new TextPart("plain") {
        //        Text = messageText
        //    };
        //    return message;
        //}
        //private async Task SendMessage(GmailService service, string userId, MimeMessage emailMessage) {
        //    using (var stream = new MemoryStream()) {
        //        await emailMessage.WriteToAsync(stream);
        //        var message = new Message {
        //            Raw = Convert.ToBase64String(stream.ToArray())
        //        };

        //        await service.Users.Messages.Send(message, userId).ExecuteAsync();
        //    }
        //}
    }
}
