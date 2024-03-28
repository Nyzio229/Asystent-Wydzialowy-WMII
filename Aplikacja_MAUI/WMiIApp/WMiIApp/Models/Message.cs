using System.Text.Json.Serialization;

namespace WMiIApp.Models
{
    public class Message
    {
        public string? Content { get; set; }
        public string? Role { get; set; }
        [JsonIgnore]
        public bool IsSent { get; set; }
    }
}
