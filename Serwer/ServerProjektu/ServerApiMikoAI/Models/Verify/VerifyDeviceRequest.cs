namespace ServerApiMikoAI.Models.Verify
{
    public class VerifyDeviceRequest
    {
        public string DeviceId { get; set; }
        public int VerificationCode { get; set; }
    }
}
