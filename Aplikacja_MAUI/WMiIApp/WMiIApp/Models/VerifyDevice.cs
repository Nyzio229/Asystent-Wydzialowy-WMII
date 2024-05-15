using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class VerifyDevice
    {
        [JsonProperty("deviceId")]
        public string DeviceId { get; set; }
        [JsonProperty("verificationCode")]
        public int VerificationCode { get; set; }
    }
}
