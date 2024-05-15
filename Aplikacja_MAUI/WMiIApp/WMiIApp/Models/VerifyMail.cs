using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class VerifyMail
    {
        [JsonProperty("deviceId")]
        public string DeviceId { get; set; }
        [JsonProperty("email")]
        public string Email { get; set; }
    }
}
