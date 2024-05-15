using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WMiIApp.Models;

namespace WMiIApp.Services
{
    public static class AuthService
    {
        //const string uri = "https://c7fc-188-146-254-12.ngrok-free.app/";
        const string uriEmail = App.uri + "VerifyEmail";
        const string uriDevice = App.uri + "VerifyDevice";
        static HttpClient httpClient = new();

        async static public Task VerifyEmail(string email, string deviceId)
        {
            VerifyMail verifyMail = new()
            {
                DeviceId = deviceId,
                Email = email
            };
            var jsonPayload = JsonConvert.SerializeObject(verifyMail);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uriEmail, content);
            response.EnsureSuccessStatusCode();

            await SecureStorage.SetAsync("deviceId", deviceId);
        }

        async static public Task VerifyDevice(int code, string deviceId)
        {
            VerifyDevice verifyDevice = new()
            {
                DeviceId = deviceId,
                VerificationCode = code
            };
            var jsonPayload = JsonConvert.SerializeObject(verifyDevice);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync(uriDevice, content);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            var keyResponse = JsonConvert.DeserializeObject<KeyResponse>(responseContent);

            if(keyResponse != null)
            {
                await SecureStorage.SetAsync("apikey", keyResponse.ApiKey);
            }
        }
    }
}
