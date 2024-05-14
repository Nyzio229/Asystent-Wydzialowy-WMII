using ServerApiMikoAI.Models.Context;
using System.Security.Cryptography;
using System.Text;
using Microsoft.EntityFrameworkCore;

namespace ServerApiMikoAI {
    public class AuthorizationService {
        private readonly VerificationDataBaseContext _context;

        public AuthorizationService(VerificationDataBaseContext context) {
            _context = context;
        }

        public async Task<bool> IsDeviceAuthorized(string deviceId, string apiKey) {
            // Sprawdź czy nagłówki zostały przekazane
            if (string.IsNullOrEmpty(deviceId) || string.IsNullOrEmpty(apiKey)) {
                return false;
            }

            string encryptedApiKey = EncryptApiKey(apiKey);

            // Sprawdź czy urządzenie jest autoryzowane
            var apiAccess = await _context.api_access
                .Where(aa => aa.device_id == deviceId && aa.api_key == encryptedApiKey && aa.is_active == true)
                .FirstOrDefaultAsync();

            return apiAccess != null;
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

        // Metoda do deszyfrowania klucza API
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
